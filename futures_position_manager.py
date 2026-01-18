"""Position management for FUTURES trading with leverage support"""
import asyncio
from datetime import datetime
from logger_config import setup_logger

logger = setup_logger('PositionManager')


from trading import calc_sol_size, cancel_all_orders

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

    async def ensure_one_way_mode(self):
        """
        Ensure One-Way Mode (Netting) is enabled.
        This bot requires One-Way mode to function correctly.
        """
        try:
            # Check if set_position_mode is supported
            if not hasattr(self.exchange, 'set_position_mode'):
                logger.warning("⚠️ Exchange does not support set_position_mode")
                return False
                
            # strict (One-Way) = False (hedged) -> True? No.
            # set_position_mode(hedged: bool, symbol: str)
            # hedged=False means One-Way Mode
            
            try:
                await self.exchange.set_position_mode(hedged=False, symbol=self.symbol)
                logger.info(f"✅ Position Mode set to ONE-WAY for {self.symbol}")
                return True
            except Exception as e:
                if "not modified" in str(e) or "already" in str(e):
                     logger.info(f"✅ {self.symbol} is already in ONE-WAY mode")
                     return True
                else:
                    logger.error(f"❌ Failed to set One-Way Mode: {e}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error checking/setting position mode: {e}")
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
            
            # Aggregate positions (Netting for Hedge Mode)
            # Bitunix Hedge Mode returns separate rows for LONG and SHORT.
            # CRITICAL FIX: Track BOTH net and gross exposure for proper rebalancing
            
            net_contracts = 0
            net_notional = 0
            net_pnl = 0
            net_margin = 0
            weighted_entry_price = 0
            highest_liq_price = 0
            
            # NEW: Track individual sides for imbalance detection
            long_contracts = 0
            short_contracts = 0
            long_value_usd = 0
            short_value_usd = 0
            
            # To calc weighted entry
            total_contracts_abs = 0
            
            found_any = False
            
            for pos in positions:
                if pos['symbol'] == self.symbol:
                    found_any = True
                    contracts = pos['contracts']
                    net_contracts += contracts
                    net_pnl += pos.get('unrealizedPnl', 0)
                    net_margin += pos.get('initialMargin', 0)
                    
                    # Track individual sides
                    if contracts > 0:  # Long
                        long_contracts += contracts
                        long_value_usd += abs(contracts * current_price)
                    elif contracts < 0:  # Short
                        short_contracts += abs(contracts)
                        short_value_usd += abs(contracts * current_price)
                    
                    # Track weighted entry price
                    size_abs = abs(contracts)
                    if size_abs > 0:
                        weighted_entry_price += (pos.get('entryPrice', 0) * size_abs)
                        total_contracts_abs += size_abs 

            if not found_any or net_contracts == 0:
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
                # Active position (Net)
                position_size = net_contracts
                position_value_usd = abs(net_contracts * current_price) # Approx value based on current price
                
                # Check side
                if position_size > 0:
                    side = 'long'
                elif position_size < 0:
                    side = 'short'
                else:
                    side = 'neutral'
                    
                # Avg Entry
                avg_entry = weighted_entry_price / total_contracts_abs if total_contracts_abs > 0 else 0

                result = {
                    'position_size': position_size,
                    'position_value_usd': position_value_usd,
                    'unrealized_pnl': net_pnl,
                    'entry_price': avg_entry,
                    'current_price': current_price,
                    'margin_used': net_margin,
                    'liquidation_price': 0,  # Complex in hedge mode
                    'side': side,
                    'leverage': self.leverage,
                    # NEW: Gross exposure tracking for rebalance
                    'long_value_usd': long_value_usd,
                    'short_value_usd': short_value_usd,
                    'gross_exposure_usd': max(long_value_usd, short_value_usd)
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
        
        # CRITICAL FIX: Check GROSS exposure (largest side) not NET
        # This prevents imbalanced positions from avoiding rebalance
        gross_exposure = position.get('gross_exposure_usd', position_value)
        
        # Check if rebalance needed (use GROSS, not NET)
        if not force and gross_exposure < self.rebalance_threshold_usd:
            logger.debug(f"Rebalance not needed: Gross ${gross_exposure:.2f} (Net ${position_value:.2f})")
            return False
        
        # Safety check
        if abs(position_value) < 5:
            logger.debug(f"Position too small to rebalance: ${position_value:.2f}")
            return False
        
        try:
            logger.info(f"🔄 Rebalancing position: ${position_value:.2f} {position['side'].upper()}")
            
            # CRITICAL: Cancel existing orders to free up position/margin
            await cancel_all_orders(self.exchange, self.symbol)
            # Short sleep to ensure cancellation propagates
            await asyncio.sleep(0.5)
            
            # Calculate amount to close (Soft Rebalance: 25% to nibble down position)
            # Was 90% -> Too aggressive for losing positions
            raw_amount = abs(position_size) * 0.25 
            approx_price = position_value / abs(position_size) if abs(position_size) > 0 else 0
            
            # Ensure valid precision and min size
            amount_to_close = calc_sol_size(raw_amount, approx_price)
            
            # CRITICAL: Check if amount meets minimum order size
            # Bitunix SOL minimum is typically 0.1
            if amount_to_close < 0.1:
                logger.warning(f"⚠️ Rebalance amount {amount_to_close} < 0.1 SOL minimum. Skipping.")
                return False
            
            if amount_to_close <= 0:
                logger.warning("⚠️ Calculated close amount is zero. Skipping rebalance.")
                return False
            
            # CRITICAL: Get positionId for hedge mode closing
            # Fetch raw positions to get positionId
            raw_positions = await self.exchange.fetch_positions([self.symbol])
            position_id = None
            
            for p in raw_positions:
                if p['symbol'] == self.symbol:
                    # Match the side we're closing
                    if position['side'] == 'long' and p['side'] == 'long':
                        position_id = p.get('positionId')
                        break
                    elif position['side'] == 'short' and p['side'] == 'short':
                        position_id = p.get('positionId')
                        break
            
            # Close position with opposite order
            # CRITICAL: Bitunix uses NON-STANDARD logic!
            # side parameter = POSITION SIDE (not trade direction)
            # Close LONG = side="BUY", tradeSide="CLOSE"
            # Close SHORT = side="SELL", tradeSide="CLOSE"
            try:
                close_params = {'reduceOnly': True}
                if position_id:
                    close_params['positionId'] = position_id
                    logger.debug(f"Using positionId: {position_id} for CLOSE order")
                
                if position['side'] == 'long':
                    # Close long = BUY (Bitunix non-standard!)
                    action = 'buy'
                    order = await self.exchange.create_market_buy_order(
                        self.symbol,
                        amount_to_close,
                        params=close_params
                    )
                    logger.info(f"✅ Closed LONG position: {amount_to_close} contracts")
                
                elif position['side'] == 'short':
                    # Close short = SELL (Bitunix non-standard!)
                    action = 'sell'
                    order = await self.exchange.create_market_sell_order(
                        self.symbol,
                        amount_to_close,
                        params=close_params
                    )
                    logger.info(f"✅ Closed SHORT position: {amount_to_close} contracts")
                    
            except Exception as e:
                # Handle errors - but note Bitunix uses different side logic
                if "110017" in str(e) or "reduce-only" in str(e):
                    logger.warning(f"⚠️ Side Mismatch Detected! Flipping action... (Error: {str(e)[:100]})")
                    
                    # Flip the action (though this shouldn't happen with correct logic)
                    if position['side'] == 'long':
                        order = await self.exchange.create_market_sell_order(
                            self.symbol,
                            amount_to_close,
                            params={'reduceOnly': True}
                        )
                        logger.info(f"✅ Retry Successful: Closed LONG position (flipped)")
                    
                    else:
                        order = await self.exchange.create_market_buy_order(
                            self.symbol,
                            amount_to_close,
                            params={'reduceOnly': True}
                        )
                        logger.info(f"✅ Retry Successful: Closed SHORT position (flipped)")
                else:
                    raise e
            
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
        """Emergency close all positions (Iterates Raw Positions for Hedge Safety)"""
        logger.warning("🚨 EMERGENCY POSITION CLOSE INITIATED!")
        
        # Cancel all pending orders first to free up inventory
        await cancel_all_orders(self.exchange, self.symbol)
        await asyncio.sleep(0.5)
        
        try:
            # Fetch RAW positions to handle Hedge Mode correctly
            # We don't want the Net Position here. We want to close specific Long/Short entries.
            positions = await self.exchange.fetch_positions([self.symbol])
            
            closed_count = 0
            
            for pos in positions:
                if pos['symbol'] != self.symbol:
                    continue
                
                size = abs(pos['contracts'])
                if size == 0:
                    continue
                
                # Determine closing side
                # If Long, we Sell. If Short, we Buy.
                side = pos['side'].lower() # 'long' or 'short'
                
                try:
                    logger.info(f"🚨 Closing {side.upper()} position: {size} contracts...")
                    
                    if side == 'long':
                        await self.exchange.create_market_sell_order(
                            self.symbol,
                            size,
                            params={'reduceOnly': True, 'tradeSide': 'CLOSE'} 
                        )
                    elif side == 'short':
                        await self.exchange.create_market_buy_order(
                            self.symbol,
                            size,
                            params={'reduceOnly': True, 'tradeSide': 'CLOSE'}
                        )
                    
                    closed_count += 1
                    logger.info(f"✅ Closed {side.upper()} position successfully.")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to close {side.upper()} position: {e}")
                    # Smart Retry Mechanism handled?
                    # basic retry for now would be complex inside loop. 
                    # If it failed, it might be due to size or min limits.
            
            if closed_count == 0:
                logger.info("ℹ️ No active positions to close.")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Emergency close failed: {e}", exc_info=True)
            return False

    async def close_all_positions(self):
        """Standard close all positions (Take Profit) - Alias"""
        return await self.emergency_close_all()
