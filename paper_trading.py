"""
Paper Trading Engine - Simulate trading with REAL mainnet prices!

Uses real-time market data from Bybit mainnet (public API, no auth)
Simulates order execution, position tracking, and PnL calculation
"""

import time
from logger_config import setup_logger

logger = setup_logger('PaperTrading')


class PaperTradingEngine:
    """
    Simulates trading with real market prices
    - No API keys needed (uses public data)
    - Real mainnet prices
    - Realistic order matching
    - Full PnL tracking
    """
    
    def __init__(self, initial_balance=100, leverage=4):
        """
        Initialize paper trading engine
        
        Args:
            initial_balance: Starting balance in USD
            leverage: Trading leverage
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.leverage = leverage
        
        # Trading state
        self.positions = {}  # {symbol: {'size': amount, 'entry_price': price, 'side': 'long/short'}}
        self.orders = []  # All orders placed
        self.trades = []  # All executed trades
        
        # Statistics
        self.total_volume = 0
        self.total_trades = 0
        self.total_fees = 0
        self.realized_pnl = 0
        self.peak_balance = initial_balance
        self.lowest_balance = initial_balance
        
        logger.info("=" * 80)
        logger.info("🎯 PAPER TRADING ENGINE INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"Initial Balance: ${initial_balance}")
        logger.info(f"Leverage: {leverage}x")
        logger.info(f"Mode: Simulated trading with REAL mainnet prices")
        logger.info("=" * 80)
    
    async def place_order(self, exchange, symbol, side, amount, price, order_type='limit'):
        """
        Simulate placing an order
        
        Args:
            exchange: CCXT exchange instance (for market data)
            symbol: Trading symbol
            side: 'buy' or 'sell'
            amount: Order amount in USD
            price: Limit price
            order_type: 'limit' or 'market'
        
        Returns:
            Simulated order dict
        """
        order_id = f'paper_{len(self.orders) + 1}_{int(time.time())}'
        
        order = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'amount': amount,
            'price': price,
            'status': 'open',
            'timestamp': time.time(),
            'filled': 0,
        }
        
        self.orders.append(order)
        
        logger.info(f"📝 Paper Order Placed: {side.upper()} ${amount} @ ${price:.2f}")
        
        # Try to match immediately
        filled = await self.try_fill_order(exchange, order)
        
        if filled:
            logger.info(f"✅ Paper Order Filled: {order_id}")
        
        return order
    
    async def try_fill_order(self, exchange, order):
        """
        Try to fill order against real market
        
        Uses real orderbook to determine if order would fill
        """
        try:
            # Fetch real orderbook
            orderbook = await exchange.fetch_order_book(order['symbol'])
            
            filled = False
            fill_price = order['price']
            
            if order['type'] == 'market':
                # Market order - instant fill at best price
                if order['side'] == 'buy':
                    fill_price = orderbook['asks'][0][0]  # Best ask
                else:
                    fill_price = orderbook['bids'][0][0]  # Best bid
                filled = True
            
            elif order['type'] == 'limit':
                # Limit order - check if price would fill
                if order['side'] == 'buy':
                    best_ask = orderbook['asks'][0][0]
                    if order['price'] >= best_ask:
                        fill_price = best_ask  # Filled at best ask
                        filled = True
                else:  # sell
                    best_bid = orderbook['bids'][0][0]
                    if order['price'] <= best_bid:
                        fill_price = best_bid  # Filled at best bid
                        filled = True
            
            if filled:
                await self.execute_trade(order, fill_price)
                order['status'] = 'filled'
                order['filled'] = order['amount']
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error matching order: {e}")
            return False
    
    async def execute_trade(self, order, fill_price):
        """
        Execute a simulated trade
        
        Updates position, calculates fees, tracks PnL
        """
        # Calculate fee (Bybit: 0.06% taker)
        fee = order['amount'] * 0.0006
        
        trade = {
            'id': f'trade_{len(self.trades) + 1}',
            'order_id': order['id'],
            'symbol': order['symbol'],
            'side': order['side'],
            'amount': order['amount'],
            'price': fill_price,
            'fee': fee,
            'timestamp': time.time(),
        }
        
        self.trades.append(trade)
        self.total_trades += 1
        self.total_volume += order['amount']
        self.total_fees += fee
        
        # Update position
        self.update_position(trade)
        
        logger.info("=" * 80)
        logger.info(f"💰 PAPER TRADE EXECUTED:")
        logger.info(f"   Side: {trade['side'].upper()}")
        logger.info(f"   Amount: ${trade['amount']:.2f}")
        logger.info(f"   Price: ${fill_price:.2f}")
        logger.info(f"   Fee: ${fee:.4f}")
        logger.info(f"   Total Volume: ${self.total_volume:.2f}")
        logger.info("=" * 80)
    
    def update_position(self, trade):
        """Update virtual position"""
        symbol = trade['symbol']
        
        if symbol not in self.positions:
            self.positions[symbol] = {
                'size': 0,
                'entry_price': 0,
                'side': None,
            }
        
        pos = self.positions[symbol]
        
        if trade['side'] == 'buy':
            if pos['size'] < 0:  # Closing short
                # Calculate PnL
                pnl = (pos['entry_price'] - trade['price']) * min(abs(pos['size']), trade['amount'])
                self.realized_pnl += pnl - trade['fee']
                pos['size'] += trade['amount']
            else:  # Opening/adding long
                total_cost = abs(pos['size']) * pos['entry_price'] if pos['size'] else 0
                total_cost += trade['amount'] * trade['price']
                pos['size'] += trade['amount']
                pos['entry_price'] = total_cost / pos['size'] if pos['size'] else 0
                pos['side'] = 'long'
        
        else:  # sell
            if pos['size'] > 0:  # Closing long
                # Calculate PnL
                pnl = (trade['price'] - pos['entry_price']) * min(pos['size'], trade['amount'])
                self.realized_pnl += pnl - trade['fee']
                pos['size'] -= trade['amount']
            else:  # Opening/adding short
                total_cost = abs(pos['size']) * pos['entry_price'] if pos['size'] else 0
                total_cost += trade['amount'] * trade['price']
                pos['size'] -= trade['amount']
                pos['entry_price'] = total_cost / abs(pos['size']) if pos['size'] else 0
                pos['side'] = 'short'
        
        # Clean up zero positions
        if abs(pos['size']) < 0.01:
            pos['size'] = 0
            pos['side'] = None
        
        # Update balance
        self.balance = self.initial_balance + self.realized_pnl
        self.peak_balance = max(self.peak_balance, self.balance)
        self.lowest_balance = min(self.lowest_balance, self.balance)
    
    async def get_position(self, symbol):
        """Get current position for symbol"""
        if symbol not in self.positions:
            return {'size': 0, 'entry_price': 0, 'side': None}
        return self.positions[symbol]
    
    async def get_unrealized_pnl(self, exchange, symbol):
        """Calculate unrealized PnL based on current market price"""
        if symbol not in self.positions or self.positions[symbol]['size'] == 0:
            return 0
        
        try:
            ticker = await exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            pos = self.positions[symbol]
            
            if pos['size'] > 0:  # Long
                unrealized = (current_price - pos['entry_price']) * pos['size']
            else:  # Short
                unrealized = (pos['entry_price'] - current_price) * abs(pos['size'])
            
            return unrealized
        except:
            return 0
    
    def get_stats(self):
        """Get trading statistics"""
        return {
            'balance': self.balance,
            'realized_pnl': self.realized_pnl,
            'total_volume': self.total_volume,
            'total_trades': self.total_trades,
            'total_fees': self.total_fees,
            'peak_balance': self.peak_balance,
            'lowest_balance': self.lowest_balance,
            'return_pct': (self.balance - self.initial_balance) / self.initial_balance * 100,
        }
    
    def print_status(self):
        """Print current status"""
        stats = self.get_stats()
        
        logger.info("=" * 80)
        logger.info("📊 PAPER TRADING STATUS")
        logger.info("=" * 80)
        logger.info(f"Balance: ${stats['balance']:.2f} (Start: ${self.initial_balance})")
        logger.info(f"Realized PnL: ${stats['realized_pnl']:.2f} ({stats['return_pct']:.2f}%)")
        logger.info(f"Total Volume: ${stats['total_volume']:.2f}")
        logger.info(f"Total Trades: {stats['total_trades']}")
        logger.info(f"Total Fees: ${stats['total_fees']:.4f}")
        logger.info(f"Peak Balance: ${stats['peak_balance']:.2f}")
        logger.info(f"Drawdown: ${stats['peak_balance'] - stats['balance']:.2f}")
        logger.info("=" * 80)
