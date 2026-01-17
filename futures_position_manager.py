"""Position management for FUTURES trading with leverage support"""
import asyncio
from datetime import datetime
from logger_config import setup_logger

logger = setup_logger('PositionManager')


class FuturesPositionManager:
    """
    Manages FUTURES positions with leverage
    
    Key differences from spot:
    - Uses fetch_positions() not balance
    - Tracks leverage and margin
    - Monitors liquidation risk
    - Handles funding fees
    """
    
    def __init__(self, exchange, symbol, leverage, max_position_usd=500, rebalance_threshold_usd=200):
        """
        Initialize futures position manager
        
        Args:
            exchange: CCXT exchange instance
            symbol: Trading symbol (futures format, e.g., 'WIF/USDT:USDT')
            leverage: Leverage to use
            max_position_usd: Maximum position size in USD
            rebalance_threshold_usd: Rebalance trigger threshold
        """
        self.exchange = exchange
        self.symbol = symbol
        self.leverage = leverage
        self.max_position_usd = max_position_usd
        self.rebalance_threshold_usd = rebalance_threshold_usd
        
        self.position_history = []
        self.rebalance_count = 0
        self.last_rebalance_time = None
        self.funding_fees_paid = 0
        
        logger.info(f"FuturesPositionManager initialized for {symbol} with {leverage}x leverage")
        logger.info(f"Max position: ${max_position_usd} | Rebalance threshold: ${rebalance_threshold_usd}")
    
    async def set_leverage(self, leverage=None):
        """
        Set leverage for the symbol
        
        Args:
            leverage: Leverage to set (uses self.leverage if None)
        """
        if leverage is None:
            leverage = self.leverage
        
        try:
            # Set leverage for the symbol
            result = await self.exchange.set_leverage(leverage, self.symbol)
            logger.info(f"✅ Leverage set to {leverage}x for {self.symbol}")
            self.leverage = leverage
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set leverage: {e}")
            return False
    
    async def get_current_position(self):
        """
        Get current futures position
        
        Returns:
            dict: Position info with:
                - position_size: Size in contracts
                - position_value_usd: Notional value in USD
                - unrealized_pnl: Unrealized profit/loss
                - entry_price: Average entry price
                - current_price: Current market price
                - margin_used: Margin being used
                - liquidation_price: Estimated liquidation price
                - side: 'long', 'short', or 'neutral'
        """
        try:
            # Fetch positions
            positions = await self.exchange.fetch_positions([self.symbol])
            
            # Get current price
            ticker = await self.exchange.fetch_ticker(self.symbol)
            current_price = (ticker['bid'] + ticker['ask']) / 2
            
            # Find position for our symbol
            position = None
            for pos in positions:
                if pos['symbol'] == self.symbol:
                    position = pos
                    break
            
            if not position or position['contracts'] == 0:
                # No position
                result = {
                    'position_size': 0,
                    'position_value_usd': 0,
                    'unrealized_pnl': 0,
                    'entry_price': 0,
                    'current_price': current_price,
                    'margin_used': 0,
                    'liquidation_price': 0,
                    'side': 'neutral',
                    'leverage': self.leverage
                }
            else:
                # Active position
                position_size = position['contracts']
                position_value_usd = abs(position['notional'])
                
                # Determine side
                if position_size > 0:
                    side = 'long'
                elif position_size < 0:
                    side = 'short'
                else:
                    side = 'neutral'
                
                result = {
                    'position_size': position_size,
                    'position_value_usd': position_value_usd,
                    'unrealized_pnl': position.get('unrealizedPnl', 0),
                    'entry_price': position.get('entryPrice', 0),
                    'current_price': current_price,
                    'margin_used': position.get('initialMargin', 0),
                    'liquidation_price': position.get('liquidationPrice', 0),
                    'side': side,
                    'leverage': position.get('leverage', self.leverage)
                }
            
            # Record to history
            self.position_history.append({
                'timestamp': datetime.now(),
                **result
            })
            
            # Keep only last 1000 records
            if len(self.position_history) > 1000:
                self.position_history = self.position_history[-1000:]
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting position: {e}", exc_info=True)
            return {
                'position_size': 0,
                'position_value_usd': 0,
                'unrealized_pnl': 0,
                'entry_price': 0,
                'current_price': 0,
                'margin_used': 0,
                'liquidation_price': 0,
                'side': 'neutral',
                'leverage': self.leverage
            }
    
    async def get_margin_info(self):
        """
        Get margin and balance information
        
        Returns:
            dict: Margin info
        """
        try:
            balance = await self.exchange.fetch_balance()
            
            # For futures, get USDT balance
            usdt_balance = balance.get('USDT', {})
            
            return {
                'total_balance': usdt_balance.get('total', 0),
                'free_balance': usdt_balance.get('free', 0),
                'used_margin': usdt_balance.get('used', 0),
                'available_margin': usdt_balance.get('free', 0),
            }
        except Exception as e:
            logger.error(f"Error getting margin info: {e}")
            return {
                'total_balance': 0,
                'free_balance': 0,
                'used_margin': 0,
                'available_margin': 0,
            }
    
    async def needs_rebalancing(self):
        """
        Check if position needs rebalancing
        
        Returns:
            bool: True if rebalancing needed
        """
        position = await self.get_current_position()
        position_value = abs(position['position_value_usd'])
        
        needs_rebalance = position_value > self.rebalance_threshold_usd
        
        if needs_rebalance:
            logger.warning(f"⚠️ Position rebalance needed: ${position_value:.2f} {position['side'].upper()}")
        
        return needs_rebalance
    
    async def rebalance(self, force=False):
        """
        Rebalance position to neutral using market orders
        
        Args:
            force: Force rebalance even if below threshold
        
        Returns:
            bool: True if rebalance executed
        """
        position = await self.get_current_position()
        position_value = abs(position['position_value_usd'])
        position_size = position['position_size']
        
        # Check if rebalance needed
        if not force and position_value < self.rebalance_threshold_usd:
            logger.debug(f"Rebalance not needed: ${position_value:.2f}")
            return False
        
        # Safety check
        if abs(position_value) < 5:
            logger.debug(f"Position too small to rebalance: ${position_value:.2f}")
            return False
        
        try:
            logger.info(f"🔄 Rebalancing position: ${position_value:.2f} {position['side'].upper()}")
            
            # Calculate amount to close (90% to avoid over-closing)
            amount_to_close = abs(position_size) * 0.9
            
            if amount_to_close <= 0:
                return False
            
            # Close position with opposite order
            if position['side'] == 'long':
                # Close long = sell
                order = await self.exchange.create_market_sell_order(
                    self.symbol,
                    amount_to_close,
                    params={'reduceOnly': True}  # Important: reduce only, don't reverse
                )
                logger.info(f"✅ Closed LONG position: {amount_to_close} contracts")
            
            elif position['side'] == 'short':
                # Close short = buy
                order = await self.exchange.create_market_buy_order(
                    self.symbol,
                    amount_to_close,
                    params={'reduceOnly': True}
                )
                logger.info(f"✅ Closed SHORT position: {amount_to_close} contracts")
            
            self.rebalance_count += 1
            self.last_rebalance_time = datetime.now()
            
            # Wait for execution
            await asyncio.sleep(1)
            
            # Check new position
            new_position = await self.get_current_position()
            logger.info(f"📊 Position after rebalance: ${new_position['position_value_usd']:.2f} {new_position['side'].upper()}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Rebalance failed: {e}", exc_info=True)
            return False
    
    async def check_liquidation_risk(self):
        """
        Check if position is at risk of liquidation
        
        Returns:
            dict: Risk assessment
        """
        position = await self.get_current_position()
        
        if position['side'] == 'neutral':
            return {'risk_level': 'NONE', 'distance_to_liq_pct': 0}
        
        current_price = position['current_price']
        liq_price = position['liquidation_price']
        
        if liq_price == 0:
            return {'risk_level': 'UNKNOWN', 'distance_to_liq_pct': 0}
        
        # Calculate distance to liquidation
        distance_pct = abs((current_price - liq_price) / current_price) * 100
        
        # Determine risk level
        if distance_pct < 5:
            risk_level = 'CRITICAL'
        elif distance_pct < 10:
            risk_level = 'HIGH'
        elif distance_pct < 20:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        if risk_level in ['CRITICAL', 'HIGH']:
            logger.warning(f"⚠️ Liquidation risk {risk_level}: {distance_pct:.2f}% from liq price ${liq_price:.4f}")
        
        return {
            'risk_level': risk_level,
            'distance_to_liq_pct': distance_pct,
            'liquidation_price': liq_price,
            'current_price': current_price
        }
    
    async def get_funding_fees(self):
        """
        Get funding fee history
        
        Returns:
            list: Funding fee records
        """
        try:
            # Fetch funding history
            funding = await self.exchange.fetch_funding_history(self.symbol, limit=100)
            
            total_funding = sum(f.get('amount', 0) for f in funding)
            self.funding_fees_paid = total_funding
            
            return funding
            
        except Exception as e:
            logger.error(f"Error fetching funding fees: {e}")
            return []
    
    def get_position_stats(self):
        """Get position statistics"""
        if not self.position_history:
            return {}
        
        return {
            'current_position': self.position_history[-1],
            'rebalance_count': self.rebalance_count,
            'last_rebalance': self.last_rebalance_time,
            'total_funding_fees': self.funding_fees_paid,
            'leverage': self.leverage
        }
    
    async def emergency_close_all(self):
        """Emergency close all positions"""
        logger.warning("🚨 EMERGENCY POSITION CLOSE INITIATED!")
        
        try:
            position = await self.get_current_position()
            
            if position['side'] == 'neutral':
                logger.info("No position to close")
                return True
            
            position_size = abs(position['position_size'])
            
            if position['side'] == 'long':
                # Close long
                order = await self.exchange.create_market_sell_order(
                    self.symbol,
                    position_size,
                    params={'reduceOnly': True}
                )
            else:
                # Close short
                order = await self.exchange.create_market_buy_order(
                    self.symbol,
                    position_size,
                    params={'reduceOnly': True}
                )
            
            logger.warning(f"✅ Emergency close executed | PnL: ${position['unrealized_pnl']:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Emergency close failed: {e}", exc_info=True)
            return False
