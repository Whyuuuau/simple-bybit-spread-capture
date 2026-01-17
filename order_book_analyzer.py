"""Order book analysis module for optimal order placement"""
import asyncio
from logger_config import setup_logger

logger = setup_logger('OrderBookAnalyzer')


async def fetch_order_book(exchange, symbol, depth=20):
    """
    Fetch current order book from exchange
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
        depth: Number of levels to fetch
    
    Returns:
        dict: Order book with bids and asks
    """
    try:
        order_book = await exchange.fetch_order_book(symbol, limit=depth)
        return order_book
    except Exception as e:
        logger.error(f"Error fetching order book: {e}")
        return {'bids': [], 'asks': []}


def calculate_spread_metrics(order_book):
    """
    Calculate various spread metrics from order book
    
    Args:
        order_book: Order book dict with bids/asks
    
    Returns:
        dict: Spread metrics
    """
    if not order_book['bids'] or not order_book['asks']:
        return {
            'spread_abs': 0,
            'spread_pct': 0,
            'mid_price': 0,
            'best_bid': 0,
            'best_ask': 0
        }
    
    best_bid = order_book['bids'][0][0]
    best_ask = order_book['asks'][0][0]
    
    spread_abs = best_ask - best_bid
    spread_pct = (spread_abs / best_bid) * 100
    mid_price = (best_bid + best_ask) / 2
    
    return {
        'spread_abs': spread_abs,
        'spread_pct': spread_pct,
        'mid_price': mid_price,
        'best_bid': best_bid,
        'best_ask': best_ask
    }


def calculate_optimal_spread(order_book, min_spread_pct, max_spread_pct, volatility=None):
    """
    Calculate optimal spread for order placement
    
    Strategy:
    - Start with current market spread
    - Adjust based on volatility if provided
    - Ensure within min/max bounds
    - Target slightly inside the spread for better fills
    
    Args:
        order_book: Order book dict
        min_spread_pct: Minimum spread percentage (e.g., 0.05 for 0.05%)
        max_spread_pct: Maximum spread percentage
        volatility: Optional volatility metric for adjustment
    
    Returns:
        float: Optimal spread percentage
    """
    metrics = calculate_spread_metrics(order_book)
    current_spread_pct = metrics['spread_pct']
    
    if current_spread_pct == 0:
        return min_spread_pct
    
    # Target 50-70% of current spread for volume mode
    # This helps us get filled while still maintaining some profit margin
    target_multiplier = 0.6
    
    # Adjust based on volatility if provided
    if volatility is not None:
        # Higher volatility = wider spread
        target_multiplier += (volatility * 0.2)
        target_multiplier = min(target_multiplier, 0.9)
    
    target_spread = current_spread_pct * target_multiplier
    
    # Ensure within bounds
    target_spread = max(min_spread_pct, min(target_spread, max_spread_pct))
    
    logger.debug(f"Spread | Current: {current_spread_pct:.4f}% | Target: {target_spread:.4f}%")
    
    return target_spread


def get_liquidity_at_level(order_book, price, side, tolerance_pct=0.01):
    """
    Get total liquidity near a specific price level
    
    Args:
        order_book: Order book dict
        price: Target price
        side: 'buy' or 'sell'
        tolerance_pct: Price tolerance percentage (e.g., 0.01 for 1%)
    
    Returns:
        float: Total liquidity in USD at that level
    """
    levels = order_book['bids'] if side == 'buy' else order_book['asks']
    
    total_liquidity_usd = 0
    
    for level_price, level_size in levels:
        price_diff_pct = abs(level_price - price) / price
        
        if price_diff_pct <= tolerance_pct / 100:
            total_liquidity_usd += level_price * level_size
    
    return total_liquidity_usd


def find_optimal_price_levels(order_book, num_orders, spread_pct, symbol_precision=None):
    """
    Find optimal price levels for order placement
    
    Strategy:
    - Place orders distributed across the spread
    - Position them to maximize fill probability
    - Respect exchange price precision
    
    Args:
        order_book: Order book dict
        num_orders: Number of orders per side
        spread_pct: Target spread percentage
        symbol_precision: Price precision for the symbol
    
    Returns:
        tuple: (buy_prices, sell_prices)
    """
    metrics = calculate_spread_metrics(order_book)
    mid_price = metrics['mid_price']
    
    if mid_price == 0:
        return [], []
    
    # Convert spread percentage to decimal
    spread_decimal = spread_pct / 100
    
    buy_prices = []
    sell_prices = []
    
    for i in range(num_orders):
        # Distribute orders across the spread
        # First order closest to mid, last order furthest
        step = (i + 0.5) / num_orders
        
        buy_price = mid_price * (1 - spread_decimal * step)
        sell_price = mid_price * (1 + spread_decimal * step)
        
        # Round to exchange precision if provided
        if symbol_precision:
            buy_price = round(buy_price, symbol_precision)
            sell_price = round(sell_price, symbol_precision)
        
        buy_prices.append(buy_price)
        sell_prices.append(sell_price)
    
    logger.debug(f"Order levels | Buy: {buy_prices[0]:.6f}-{buy_prices[-1]:.6f} | "
                f"Sell: {sell_prices[0]:.6f}-{sell_prices[-1]:.6f}")
    
    return buy_prices, sell_prices


def analyze_order_book_imbalance(order_book, depth=10):
    """
    Analyze order book imbalance to detect potential price movements
    
    Args:
        order_book: Order book dict
        depth: Number of levels to analyze
    
    Returns:
        dict: Imbalance metrics
    """
    bids = order_book['bids'][:depth]
    asks = order_book['asks'][:depth]
    
    # Calculate total volume on each side
    total_bid_volume = sum(price * size for price, size in bids)
    total_ask_volume = sum(price * size for price, size in asks)
    
    total_volume = total_bid_volume + total_ask_volume
    
    if total_volume == 0:
        return {
            'imbalance_ratio': 0.5,
            'imbalance_pct': 0,
            'signal': 'NEUTRAL'
        }
    
    # Calculate imbalance
    # > 0.5 = more bids (bullish)
    # < 0.5 = more asks (bearish)
    imbalance_ratio = total_bid_volume / total_volume
    imbalance_pct = (imbalance_ratio - 0.5) * 200  # -100 to +100
    
    # Determine signal
    if imbalance_pct > 20:
        signal = 'BULLISH'
    elif imbalance_pct < -20:
        signal = 'BEARISH'
    else:
        signal = 'NEUTRAL'
    
    return {
        'imbalance_ratio': imbalance_ratio,
        'imbalance_pct': imbalance_pct,
        'signal': signal,
        'bid_volume_usd': total_bid_volume,
        'ask_volume_usd': total_ask_volume
    }


def get_market_depth_pressure(order_book, price_levels=5):
    """
    Calculate market depth pressure
    
    Measures how much volume is stacked on each side
    Can indicate potential support/resistance levels
    
    Args:
        order_book: Order book dict
        price_levels: Number of levels to analyze
    
    Returns:
        float: Pressure ratio (-1 to 1, negative = sell pressure, positive = buy pressure)
    """
    bids = order_book['bids'][:price_levels]
    asks = order_book['asks'][:price_levels]
    
    bid_sizes = [size for price, size in bids]
    ask_sizes = [size for price, size in asks]
    
    total_bid_size = sum(bid_sizes)
    total_ask_size = sum(ask_sizes)
    
    if total_bid_size + total_ask_size == 0:
        return 0
    
    pressure = (total_bid_size - total_ask_size) / (total_bid_size + total_ask_size)
    
    return pressure


async def get_comprehensive_market_analysis(exchange, symbol, depth=20):
    """
    Get comprehensive market analysis from order book
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
        depth: Order book depth
    
    Returns:
        dict: Comprehensive market analysis
    """
    order_book = await fetch_order_book(exchange, symbol, depth)
    
    spread_metrics = calculate_spread_metrics(order_book)
    imbalance = analyze_order_book_imbalance(order_book)
    pressure = get_market_depth_pressure(order_book)
    
    analysis = {
        'timestamp': asyncio.get_event_loop().time(),
        'spread': spread_metrics,
        'imbalance': imbalance,
        'pressure': pressure,
        'order_book': order_book
    }
    
    logger.debug(f"Market analysis | Spread: {spread_metrics['spread_pct']:.4f}% | "
                f"Imbalance: {imbalance['signal']} | Pressure: {pressure:.2f}")
    
    return analysis
