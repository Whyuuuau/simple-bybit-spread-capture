"""Trading module with proper order management, PnL calculation, and profit-taking"""
import asyncio
from datetime import datetime, timedelta
from logger_config import setup_logger, log_trade

logger = setup_logger('Trading')


def round_order_amount(amount_eth, current_price):
    """
    Round order amount to meet exchange requirements
    
    Args:
def round_order_amount(amount_crypto, current_price):
    """
    Round order amount to meet exchange requirements (generic)
    
    Args:
        amount_crypto: Raw crypto amount
        current_price: Current price
        
    Returns:
        float: Properly rounded amount that meets:
            - Min value: 0.1 (for SOL) or from config
            - Min notional: $10
    """
    # Precision based on TICK_SIZE logic
    # For SOL, precision is 0.01 or 0.1
    precision = 2 # 0.01
    
    rounded_amount = round(amount_crypto, precision)
    
    # Ensure minimum amount (0.1 for SOL, safe default)
    if rounded_amount < 0.1:
        rounded_amount = 0.1
    
    # Check notional value
    notional_value = rounded_amount * current_price
    
    # If notional < $10, increase amount
    if notional_value < 10:
        # Calculate needed amount for $10
        min_crypto_for_10_usd = 10 / current_price
        rounded_amount = max(round(min_crypto_for_10_usd, precision), 0.1)
    
    return rounded_amount


# ============================================================================
# MARKET DATA FUNCTIONS
# ============================================================================

async def get_market_price(exchange, symbol):
    """
    Get current market prices with error handling
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
    
    Returns:
        tuple: (bid, ask) or (0, 0) on error
    """
    try:
        ticker = await exchange.fetch_ticker(symbol)
        return ticker['bid'], ticker['ask']
    except Exception as e:
        logger.error(f"Error fetching market price: {e}")
        return 0, 0


async def get_current_balance(exchange, currency):
    """
    Get current balance for a currency
    
    Args:
        exchange: CCXT exchange instance
        currency: Currency symbol (e.g., 'USDT')
    
    Returns:
        dict: Balance info (total, free, used)
    """
    try:
        balance = await exchange.fetch_balance()
        return balance.get(currency, {'total': 0, 'free': 0, 'used': 0})
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        return {'total': 0, 'free': 0, 'used': 0}


# ============================================================================
# ORDER MANAGEMENT FUNCTIONS
# ============================================================================

async def place_order(exchange, symbol, side, price, size, retry_count=3):
    """
    Place limit order with retry mechanism
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
        side: 'buy' or 'sell'
        price: Limit price
        size: Order size
        retry_count: Number of retries on failure
    
    Returns:
        dict: Order info or None on failure
    """
    for attempt in range(retry_count):
        try:
            # Use CCXT's built-in precision handling (returns string)
            # This is safer than manual int/float casting for Bybit V5
            formatted_size = exchange.amount_to_precision(symbol, size)
            formatted_price = exchange.price_to_precision(symbol, price)
            
            logger.info(f"DEBUG PLACE ORDER: {side} {formatted_size} @ {formatted_price}")
            
            if side == 'buy':
                order = await exchange.create_limit_buy_order(symbol, formatted_size, formatted_price)
            elif side == 'sell':
                order = await exchange.create_limit_sell_order(symbol, formatted_size, formatted_price)
            else:
                logger.error(f"Invalid order side: {side}")
                return None
            
            log_trade(logger, 'PLACED', symbol, side, price, size, order.get('id'))
            return order
            
        except Exception as e:
            logger.error(f"Error placing {side} order (attempt {attempt + 1}/{retry_count}): {e}")
            
            if attempt < retry_count - 1:
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"Failed to place order after {retry_count} attempts")
                return None


async def cancel_order(exchange, symbol, order_id, retry_count=2):
    """
    Cancel order with retry mechanism
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
        order_id: Order ID to cancel
        retry_count: Number of retries
    
    Returns:
        dict: Cancelled order info or None
    """
    for attempt in range(retry_count):
        try:
            result = await exchange.cancel_order(order_id, symbol)
            logger.info(f"ORDER CANCELLED | ID: {order_id}")
            return result
        except Exception as e:
            error_msg = str(e).lower()
            
            # If order already cancelled or doesn't exist, that's okay
            if 'not found' in error_msg or 'does not exist' in error_msg:
                logger.debug(f"Order {order_id} already cancelled or doesn't exist")
                return None
            
            logger.error(f"Error cancelling order {order_id} (attempt {attempt + 1}/{retry_count}): {e}")
            
            if attempt < retry_count - 1:
                await asyncio.sleep(0.5)
            else:
                return None


async def cancel_all_orders(exchange, symbol):
    """
    Cancel all open orders for a symbol
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
    
    Returns:
        int: Number of orders cancelled
    """
    try:
        open_orders = await get_open_orders(exchange, symbol)
        
        if not open_orders:
            logger.debug("No open orders to cancel")
            return 0
        
        logger.info(f"Cancelling {len(open_orders)} open orders...")
        
        # Cancel all orders concurrently
        tasks = [cancel_order(exchange, symbol, order['id']) for order in open_orders]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if r is not None and not isinstance(r, Exception))
        
        logger.info(f"✅ Cancelled {success_count}/{len(open_orders)} orders")
        return success_count
        
    except Exception as e:
        logger.error(f"Error in cancel_all_orders: {e}")
        return 0


async def get_open_orders(exchange, symbol):
    """
    Get all open orders for a symbol
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
    
    Returns:
        list: Open orders
    """
    try:
        orders = await exchange.fetch_open_orders(symbol)
        return orders
    except Exception as e:
        logger.error(f"Error fetching open orders: {e}")
        return []


async def get_closed_orders(exchange, symbol, since=None, limit=100):
    """
    Get closed (filled/cancelled) orders
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
        since: Timestamp to fetch from
        limit: Max number of orders
    
    Returns:
        list: Closed orders
    """
    try:
        orders = await exchange.fetch_closed_orders(symbol, since=since, limit=limit)
        return orders
    except Exception as e:
        logger.error(f"Error fetching closed orders: {e}")
        return []


async def get_filled_orders(exchange, symbol, since=None):
    """
    Get only filled orders (exclude cancelled)
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
        since: Timestamp to fetch from
    
    Returns:
        list: Filled orders
    """
    try:
        closed_orders = await get_closed_orders(exchange, symbol, since=since)
        filled_orders = [o for o in closed_orders if o['status'] == 'closed' and o['filled'] > 0]
        return filled_orders
    except Exception as e:
        logger.error(f"Error getting filled orders: {e}")
        return []


# ============================================================================
# SMART ORDER MANAGEMENT
# ============================================================================

def should_cancel_order(order, target_orders, price_tolerance_pct=0.1):
    """
    Determine if an order should be cancelled
    
    Args:
        order: Existing order dict
        target_orders: List of target order dicts
        price_tolerance_pct: Price tolerance percentage
    
    Returns:
        bool: True if should cancel
    """
    for target in target_orders:
        if order['side'] == target['side']:
            price_diff_pct = abs(order['price'] - target['price']) / order['price'] * 100
            
            if price_diff_pct < price_tolerance_pct:
                # Order is close enough to target, keep it
                return False
    
    # No matching target found, cancel this order
    return True


async def smart_order_management(exchange, symbol, target_orders, price_tolerance_pct=0.1):
    """
    Efficiently manage orders - only cancel/place what's needed
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
        target_orders: List of target orders to achieve
        price_tolerance_pct: Price tolerance for keeping existing orders
    
    Returns:
        dict: Statistics (cancelled, placed, kept)
    """
    open_orders = await get_open_orders(exchange, symbol)
    
    stats = {'cancelled': 0, 'placed': 0, 'kept': 0}
    
    # Cancel orders that don't match targets
    cancel_tasks = []
    for order in open_orders:
        if should_cancel_order(order, target_orders, price_tolerance_pct):
            cancel_tasks.append(cancel_order(exchange, symbol, order['id']))
        else:
            stats['kept'] += 1
    
    if cancel_tasks:
        results = await asyncio.gather(*cancel_tasks, return_exceptions=True)
        stats['cancelled'] = sum(1 for r in results if r is not None and not isinstance(r, Exception))
    
    # Place missing orders
    await asyncio.sleep(0.5)  # Small delay after cancellations
    
    place_tasks = []
    for target in target_orders:
        # Check if this order already exists
        exists = False
        for order in open_orders:
            if order['side'] == target['side']:
                price_diff_pct = abs(order['price'] - target['price']) / order['price'] * 100
                if price_diff_pct < price_tolerance_pct:
                    exists = True
                    break
        
        if not exists:
            place_tasks.append(
                place_order(exchange, symbol, target['side'], target['price'], target['size'])
            )
    
    if place_tasks:
        results = await asyncio.gather(*place_tasks, return_exceptions=True)
        stats['placed'] = sum(1 for r in results if r is not None and not isinstance(r, Exception))
    
    logger.debug(f"Order management | Kept: {stats['kept']} | Cancelled: {stats['cancelled']} | Placed: {stats['placed']}")
    
    return stats


# ============================================================================
# PNL CALCULATION (FIXED!)
# ============================================================================

class PnLTracker:
    """Track PnL properly without double counting - IMPROVED VERSION ✅"""
    
    def __init__(self):
        self.processed_order_ids = set()
        self.trades_history = []
        self.buy_positions = []
        self.sell_positions = []
    
    async def calculate_pnl(self, exchange, symbol):
        """
        Calculate PnL from filled orders - ENHANCED with matched trades
        
        Args:
            exchange: CCXT exchange
            symbol: Trading symbol
        
        Returns:
            dict: PnL metrics including matched trade profit
        """
        try:
            # Get trades (more accurate than orders)
            trades = await exchange.fetch_my_trades(symbol, limit=500)
            
            total_volume = 0
            trade_count = 0
            total_fees_paid = 0
            
            new_buy_positions = []
            new_sell_positions = []
            
            for trade in trades:
                # Create unique trade ID (IMPROVED - prevents collisions!)
                trade_id = f"{trade.get('id', '')}{trade.get('order', '')}_{trade.get('timestamp', '')}_{trade.get('side', '')}_{trade.get('amount', 0)}"
                
                # Skip if already processed
                if trade_id in self.processed_order_ids:
                    continue
                
                # Calculate trade value
                cost = trade['cost']  # Already includes price × amount
                fee = trade.get('fee', {}).get('cost', 0) if trade.get('fee') else 0
                
                # Add to volume
                total_volume += cost
                total_fees_paid += fee
                
                # Store for matching
                trade_data = {
                    'id': trade_id,
                    'timestamp': trade['timestamp'],
                    'side': trade['side'],
                    'price': trade['price'],
                    'amount': trade['amount'],
                    'cost': cost,
                    'fee': fee,
                    'remaining_amount': trade['amount']  # For matching
                }
                
                if trade['side'] == 'buy':
                    new_buy_positions.append(trade_data)
                else:
                    new_sell_positions.append(trade_data)
                
                # Track for future
                self.trades_history.append(trade_data)
                self.processed_order_ids.add(trade_id)
                trade_count += 1
            
            # Add to position lists
            self.buy_positions.extend(new_buy_positions)
            self.sell_positions.extend(new_sell_positions)
            
            # Calculate matched PnL (IMPROVED!)
            matched_pnl = self._calculate_matched_pnl()
            
            # Estimate unmatched PnL (for futures with floating positions)
            unmatched_value = self._calculate_unmatched_value()
            
            return {
                'total_volume': total_volume,
                'trade_count': trade_count,
                'total_fees': total_fees_paid,
                'matched_pnl': matched_pnl,  # From completed round-trips
                'unmatched_value': unmatched_value,  # From open positions
                'estimated_pnl': matched_pnl - total_fees_paid,  # Conservative estimate
                'trades_processed': len(self.processed_order_ids)
            }
            
        except Exception as e:
            logger.error(f"Error calculating PnL: {e}", exc_info=True)
            return {
                'total_volume': 0,
                'trade_count': 0,
                'total_fees': 0,
                'matched_pnl': 0,
                'unmatched_value': 0,
                'estimated_pnl': 0,
                'trades_processed': 0
            }
    
    def _calculate_matched_pnl(self):
        """
        Calculate PnL from matched buy/sell pairs (FIFO)
        This is the REAL profit tracking ✅
        """
        total_matched_pnl = 0
        
        # Use copies to avoid modifying original lists
        buys = [b.copy() for b in self.buy_positions if b['remaining_amount'] > 0]
        sells = [s.copy() for s in self.sell_positions if s['remaining_amount'] > 0]
        
        # Match FIFO (first in, first out)
        for buy in buys:
            for sell in sells:
                if buy['remaining_amount'] <= 0 or sell['remaining_amount'] <= 0:
                    continue
                
                # Match amount
                matched_amount = min(buy['remaining_amount'], sell['remaining_amount'])
                
                # Calculate spread profit
                spread_profit = (sell['price'] - buy['price']) * matched_amount
                
                # Calculate proportional fees
                buy_fee_portion = buy['fee'] * (matched_amount / buy['amount'])
                sell_fee_portion = sell['fee'] * (matched_amount / sell['amount'])
                total_fee = buy_fee_portion + sell_fee_portion
                
                # Net PnL for this match
                net_pnl = spread_profit - total_fee
                total_matched_pnl += net_pnl
                
                # Update remaining amounts
                buy['remaining_amount'] -= matched_amount
                sell['remaining_amount'] -= matched_amount
                
                # Update in original lists
                for b in self.buy_positions:
                    if b['id'] == buy['id']:
                        b['remaining_amount'] = buy['remaining_amount']
                
                for s in self.sell_positions:
                    if s['id'] == sell['id']:
                        s['remaining_amount'] = sell['remaining_amount']
        
        return total_matched_pnl
    
    def _calculate_unmatched_value(self):
        """Calculate value of unmatched positions"""
        unmatched_buy_value = sum(
            b['price'] * b['remaining_amount'] 
            for b in self.buy_positions 
            if b['remaining_amount'] > 0
        )
        
        unmatched_sell_value = sum(
            s['price'] * s['remaining_amount']
            for s in self.sell_positions
            if s['remaining_amount'] > 0
        )
        
        # Net unmatched (positive = more buys, negative = more sells)
        return unmatched_sell_value - unmatched_buy_value


# ============================================================================
# PROFIT TAKING
# ============================================================================

async def find_profitable_opportunities(exchange, symbol, min_profit_pct=0.1):
    """
    Find opportunities to close positions for profit
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
        min_profit_pct: Minimum profit percentage to take
    
    Returns:
        list: Profitable opportunities
    """
    try:
        # Get recent filled orders
        filled_orders = await get_filled_orders(exchange, symbol)
        
        if not filled_orders:
            return []
        
        # Get current market price
        bid, ask = await get_market_price(exchange, symbol)
        mid_price = (bid + ask) / 2
        
        opportunities = []
        
        for order in filled_orders:
            fill_price = order.get('average', order.get('price', 0))
            side = order['side']
            amount = order['filled']
            
            if side == 'buy':
                # Can we sell for profit?
                profit_pct = ((mid_price - fill_price) / fill_price) * 100
                
                if profit_pct >= min_profit_pct:
                    opportunities.append({
                        'original_order_id': order['id'],
                        'action': 'sell',
                        'entry_price': fill_price,
                        'current_price': mid_price,
                        'profit_pct': profit_pct,
                        'amount': amount,
                        'timestamp': order['timestamp']
                    })
            
            elif side == 'sell':
                # Can we buy back for profit?
                profit_pct = ((fill_price - mid_price) / fill_price) * 100
                
                if profit_pct >= min_profit_pct:
                    opportunities.append({
                        'original_order_id': order['id'],
                        'action': 'buy',
                        'entry_price': fill_price,
                        'current_price': mid_price,
                        'profit_pct': profit_pct,
                        'amount': amount,
                        'timestamp': order['timestamp']
                    })
        
        if opportunities:
            logger.info(f"💰 Found {len(opportunities)} profitable opportunities")
        
        return opportunities
        
    except Exception as e:
        logger.error(f"Error finding profitable opportunities: {e}")
        return []


async def execute_profit_take(exchange, symbol, opportunity):
    """
    Execute a profit-taking trade
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
        opportunity: Opportunity dict from find_profitable_opportunities
    
    Returns:
        dict: Executed order or None
    """
    try:
        side = opportunity['action']
        amount = opportunity['amount']
        
        logger.info(f"💰 Taking profit: {side.upper()} {amount} | Profit: {opportunity['profit_pct']:.2f}%")
        
        # Use market order for quick execution
        if side == 'buy':
            order = await exchange.create_market_buy_order(symbol, amount)
        else:
            order = await exchange.create_market_sell_order(symbol, amount)
        
        logger.info(f"✅ Profit taken: ${opportunity['profit_pct']:.2f}% | Order ID: {order.get('id')}")
        
        return order
        
    except Exception as e:
        logger.error(f"❌ Failed to execute profit take: {e}")
        return None
