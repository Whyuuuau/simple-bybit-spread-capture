"""
Paper Position Manager - Wrapper for paper trading mode

Overrides FuturesPositionManager to work without API authentication
Uses PaperTradingEngine for all position operations
"""

from logger_config import setup_logger

logger = setup_logger('PaperPositionManager')


class PaperPositionManager:
    """
    Position manager for paper trading mode
    Wraps paper trading engine to provide same interface as real position manager
    """
    
    def __init__(self, paper_engine, symbol, leverage):
        """
        Initialize paper position manager
        
        Args:
            paper_engine: PaperTradingEngine instance
            symbol: Trading symbol
            leverage: Leverage amount
        """
        self.paper_engine = paper_engine
        self.symbol = symbol
        self.leverage = leverage
        
        logger.info(f"📝 Paper Position Manager initialized for {symbol}")
    
    async def set_leverage(self, leverage):
        """Set leverage (no-op for paper trading, always succeeds)"""
        logger.info(f"✅ Paper trading: leverage set to {leverage}x (simulated)")
        return True
    
    async def get_current_position(self):
        """Get current position from paper engine"""
        try:
            position = await self.paper_engine.get_position(self.symbol)
            return {
                'size': position['size'],
                'entry_price': position['entry_price'],
                'side': position['side'],
                'unrealized_pnl': 0,  # Updated separately
            }
        except Exception as e:
            logger.error(f"Error getting paper position: {e}")
            return {'size': 0, 'entry_price': 0, 'side': None, 'unrealized_pnl': 0}
    
    async def place_market_order(self, exchange, side, amount_usd):
        """Place market order through paper engine"""
        try:
            # Get current price
            ticker = await exchange.fetch_ticker(self.symbol)
            price = ticker['last']
            
            # Use paper engine
            order = await self.paper_engine.place_order(
                exchange=exchange,
                symbol=self.symbol,
                side=side,
                amount=amount_usd,
                price=price,
                order_type='market'
            )
            
            return order
            
        except Exception as e:
            logger.error(f"Error placing paper market order: {e}")
            return None
    
    async def place_limit_order(self, exchange, side, amount_usd, price):
        """Place limit order through paper engine"""
        try:
            order = await self.paper_engine.place_order(
                exchange=exchange,
                symbol=self.symbol,
                side=side,
                amount=amount_usd,
                price=price,
                order_type='limit'
            )
            
            return order
            
        except Exception as e:
            logger.error(f"Error placing paper limit order: {e}")
            return None
    
    async def close_position(self, exchange):
        """Close position through paper engine"""
        try:
            position = await self.get_current_position()
            
            if position['size'] == 0:
                logger.info("No position to close")
                return True
            
            # Determine side to close
            if position['size'] > 0:
                # Close long with sell
                side = 'sell'
                amount = position['size']
            else:
                # Close short with buy  
                side = 'buy'
                amount = abs(position['size'])
            
            # Place closing order
            order = await self.place_market_order(exchange, side, amount)
            
            if order:
                logger.info(f"✅ Paper position closed: {amount} {side}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error closing paper position: {e}")
            return False
    
    async def get_margin_info(self):
        """Get margin info (simulated for paper trading)"""
        stats = self.paper_engine.get_stats()
        return {
            'available_margin': stats['balance'],
            'used_margin': 0,
            'margin_level': 999,  # Very high (safe)
        }
    
    async def check_liquidation_risk(self):
        """Check liquidation risk (always safe in paper trading)"""
        return {
            'at_risk': False,
            'margin_level': 999,
            'liquidation_price': 0,
        }
