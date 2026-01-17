"""Position management module for maintaining position neutrality and risk control"""
import asyncio
from datetime import datetime
from logger_config import setup_logger

logger = setup_logger('PositionManager')


class PositionManager:
    """
    Manages trading positions to maintain neutrality and control risk
    
    Key responsibilities:
    - Track current position in real-time
    - Auto-rebalance when position exceeds threshold
    - Maintain position history
    - Calculate position-based metrics
    """
    
    def __init__(self, exchange, symbol, max_position_usd=200, rebalance_threshold_usd=100):
        """
        Initialize position manager
        
        Args:
            exchange: CCXT exchange instance
            symbol: Trading symbol (e.g., 'WIF/USDT')
            max_position_usd: Maximum allowed position size in USD
            rebalance_threshold_usd: Trigger rebalance when position exceeds this
        """
        self.exchange = exchange
        self.symbol = symbol
        self.max_position_usd = max_position_usd
        self.rebalance_threshold_usd = rebalance_threshold_usd
        
        self.base_currency = symbol.split('/')[0]
        self.quote_currency = symbol.split('/')[1]
        
        self.position_history = []
        self.rebalance_count = 0
        self.last_rebalance_time = None
        
        logger.info(f"PositionManager initialized for {symbol}")
        logger.info(f"Max position: ${max_position_usd} | Rebalance threshold: ${rebalance_threshold_usd}")
    
    async def get_current_position(self):
        """
        Get current position from exchange balance
        
        Returns:
            tuple: (position_value_usd, base_amount, quote_amount, current_price)
        """
        try:
            # Fetch balance
            balance = await self.exchange.fetch_balance()
            
            base_total = balance.get(self.base_currency, {}).get('total', 0)
            base_free = balance.get(self.base_currency, {}).get('free', 0)
            quote_total = balance.get(self.quote_currency, {}).get('total', 0)
            quote_free = balance.get(self.quote_currency, {}).get('free', 0)
            
            # Get current market price
            ticker = await self.exchange.fetch_ticker(self.symbol)
            current_price = (ticker['bid'] + ticker['ask']) / 2
            
            # Calculate position value in quote currency (USD)
            # Positive = long position, Negative = short position
            base_value_usd = base_total * current_price
            
            # For spot trading, we consider the base currency holding as position
            position_value_usd = base_value_usd
            
            # Record to history
            self.position_history.append({
                'timestamp': datetime.now(),
                'position_usd': position_value_usd,
                'base_amount': base_total,
                'quote_amount': quote_total,
                'price': current_price
            })
            
            # Keep only last 1000 records
            if len(self.position_history) > 1000:
                self.position_history = self.position_history[-1000:]
            
            return position_value_usd, base_total, quote_total, current_price
            
        except Exception as e:
            logger.error(f"Error getting position: {e}", exc_info=True)
            return 0, 0, 0, 0
    
    async def needs_rebalancing(self):
        """
        Check if position needs rebalancing
        
        Returns:
            bool: True if rebalancing needed
        """
        position_value, _, _, _ = await self.get_current_position()
        
        needs_rebalance = abs(position_value) > self.rebalance_threshold_usd
        
        if needs_rebalance:
            logger.warning(f"⚠️ Position rebalance needed: ${position_value:.2f}")
        
        return needs_rebalance
    
    async def rebalance(self, force=False):
        """
        Rebalance position back to neutral using market orders
        
        Args:
            force: Force rebalance even if below threshold
        
        Returns:
            bool: True if rebalance executed, False otherwise
        """
        position_value, base_amount, quote_amount, current_price = await self.get_current_position()
        
        # Check if rebalance needed
        if not force and abs(position_value) < self.rebalance_threshold_usd:
            logger.debug(f"Rebalance not needed: ${position_value:.2f}")
            return False
        
        # Safety check - don't rebalance too small positions
        if abs(position_value) < 5:
            logger.debug(f"Position too small to rebalance: ${position_value:.2f}")
            return False
        
        try:
            logger.info(f"🔄 Rebalancing position: ${position_value:.2f}")
            
            # Calculate amount to trade
            # If positive position (long), need to sell to neutralize
            # If negative position (short), need to buy to neutralize
            
            if position_value > self.rebalance_threshold_usd:
                # Long position - sell base currency
                amount_to_sell = base_amount * 0.9  # Sell 90% to avoid over-selling
                
                if amount_to_sell > 0:
                    order = await self.exchange.create_market_sell_order(
                        self.symbol, 
                        amount_to_sell
                    )
                    logger.info(f"✅ Rebalance SELL executed: {amount_to_sell:.4f} {self.base_currency}")
                    logger.info(f"Order ID: {order.get('id', 'N/A')}")
            
            elif position_value < -self.rebalance_threshold_usd:
                # Short position - buy base currency
                # Calculate how much to buy
                amount_to_buy = abs(position_value) / current_price * 0.9
                
                if amount_to_buy > 0:
                    order = await self.exchange.create_market_buy_order(
                        self.symbol,
                        amount_to_buy
                    )
                    logger.info(f"✅ Rebalance BUY executed: {amount_to_buy:.4f} {self.base_currency}")
                    logger.info(f"Order ID: {order.get('id', 'N/A')}")
            
            self.rebalance_count += 1
            self.last_rebalance_time = datetime.now()
            
            # Wait a bit for order to execute
            await asyncio.sleep(1)
            
            # Check new position
            new_position, _, _, _ = await self.get_current_position()
            logger.info(f"📊 Position after rebalance: ${new_position:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Rebalance failed: {e}", exc_info=True)
            return False
    
    def get_position_stats(self):
        """
        Get position statistics
        
        Returns:
            dict: Position statistics
        """
        if not self.position_history:
            return {}
        
        positions = [p['position_usd'] for p in self.position_history]
        
        return {
            'current_position': positions[-1] if positions else 0,
            'avg_position': sum(positions) / len(positions),
            'max_position': max(positions),
            'min_position': min(positions),
            'rebalance_count': self.rebalance_count,
            'last_rebalance': self.last_rebalance_time
        }
    
    def is_position_safe(self):
        """
        Check if current position is within safe limits
        
        Returns:
            tuple: (is_safe, reason)
        """
        if not self.position_history:
            return True, "No position data"
        
        current_position = self.position_history[-1]['position_usd']
        
        if abs(current_position) > self.max_position_usd:
            return False, f"Position exceeds max limit: ${abs(current_position):.2f} > ${self.max_position_usd}"
        
        return True, "Position within safe limits"
    
    async def emergency_close_all(self):
        """
        Emergency function to close all positions immediately
        Use only in critical situations
        """
        logger.warning("🚨 EMERGENCY POSITION CLOSE INITIATED!")
        
        try:
            position_value, base_amount, quote_amount, current_price = await self.get_current_position()
            
            # Close all base currency position
            if base_amount > 0:
                order = await self.exchange.create_market_sell_order(
                    self.symbol,
                    base_amount
                )
                logger.warning(f"🚨 Emergency sold {base_amount:.4f} {self.base_currency}")
            
            logger.warning("✅ Emergency position close completed")
            
        except Exception as e:
            logger.error(f"❌ Emergency close failed: {e}", exc_info=True)
