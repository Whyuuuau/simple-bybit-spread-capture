"""Utility functions for volume + profit hybrid bot"""
import math


def adjust_spread(volatility, base_spread=0.008, max_spread=0.05):
    """
    Adjust spread based on volatility
    
    Args:
        volatility: Current volatility metric
        base_spread: Base spread in decimal (0.008 = 0.8%)
        max_spread: Maximum spread in decimal
    
    Returns:
        float: Adjusted spread
    """
    spread = base_spread + (volatility * (max_spread - base_spread))
    return min(spread, max_spread)


def adjust_order_size(probability, base_size=20, max_size=50):
    """
    Adjust order size based on ML model probability
    
    Args:
        probability: Model prediction probability (0-1)
        base_size: Base order size in USD
        max_size: Maximum order size in USD
    
    Returns:
        float: Adjusted order size
    """
    # For profitable signals, size up
    # For neutral signals, use base size
    if probability > 0.65 or probability < 0.35:
        # Confident signal - size up
        confidence = abs(probability - 0.5) * 2  # 0 to 1
        size = base_size + (confidence * (max_size - base_size))
    else:
        # Neutral - use base size
        size = base_size
    
    return size


def calculate_volume_optimal_size(target_volume_per_hour, fills_per_hour_estimate=100):
    """
    Calculate optimal order size to hit volume target
    
    Args:
        target_volume_per_hour: Target volume in USD/hour
        fills_per_hour_estimate: Estimated fills per hour
    
    Returns:
        float: Optimal order size in USD
    """
    return target_volume_per_hour / fills_per_hour_estimate


def calculate_min_spread_for_profit(maker_fee_pct, taker_fee_pct):
    """
    Calculate minimum spread needed to be profitable after fees
    
    Args:
        maker_fee_pct: Maker fee percentage (e.g., 0.01 for 0.01%)
        taker_fee_pct: Taker fee percentage
    
    Returns:
        float: Minimum spread percentage
    """
    # Need spread > total fees
    return (abs(maker_fee_pct) + abs(taker_fee_pct)) * 1.5  # 1.5x safety margin


def round_to_precision(value, precision):
    """
    Round value to exchange precision
    
    Args:
        value: Value to round
        precision: Number of decimal places
    
    Returns:
        float: Rounded value
    """
    if precision == 0:
        return int(value)
    return round(value, precision)


def round_to_tick_size(price, tick_size):
    """
    Round price to exchange tick size
    
    Args:
        price: Price to round
        tick_size: Minimum price increment
    
    Returns:
        float: Rounded price
    """
    return round(price / tick_size) * tick_size


def calculate_position_size_usd(amount, price):
    """
    Calculate position size in USD
    
    Args:
        amount: Amount in contracts/coins
        price: Price per unit
    
    Returns:
        float: Position value in USD
    """
    return amount * price


def calculate_amount_from_usd(usd_value, price, amount_precision=0):
    """
    Calculate amount from USD value
    
    Args:
        usd_value: Value in USD
        price: Current price
        amount_precision: Precision for amount
    
    Returns:
        float: Amount in contracts/coins
    """
    amount = usd_value / price
    return round_to_precision(amount, amount_precision)


def calculate_fees(volume_usd, maker_fee_pct, taker_fee_pct, maker_ratio=0.8):
    """
    Calculate expected trading fees
    
    Args:
        volume_usd: Total volume in USD
        maker_fee_pct: Maker fee percentage
        taker_fee_pct: Taker fee percentage
        maker_ratio: Ratio of maker orders (0-1)
    
    Returns:
        float: Total fees in USD
    """
    maker_volume = volume_usd * maker_ratio
    taker_volume = volume_usd * (1 - maker_ratio)
    
    total_fees = (maker_volume * maker_fee_pct / 100 + 
                  taker_volume * taker_fee_pct / 100)
    
    return total_fees


def calculate_liquidation_price(entry_price, leverage, side='long', maintenance_margin_pct=0.5):
    """
    Calculate approximate liquidation price for futures
    
    Args:
        entry_price: Entry price
        leverage: Leverage used
        side: 'long' or 'short'
        maintenance_margin_pct: Maintenance margin percentage
    
    Returns:
        float: Liquidation price
    """
    mm = maintenance_margin_pct / 100
    
    if side == 'long':
        # Long: liq price = entry * (1 - 1/leverage + mm)
        liq_price = entry_price * (1 - 1/leverage + mm)
    else:
        # Short: liq price = entry * (1 + 1/leverage - mm)
        liq_price = entry_price * (1 + 1/leverage - mm)
    
    return liq_price


def calculate_margin_required(position_size_usd, leverage):
    """
    Calculate margin required for a position
    
    Args:
        position_size_usd: Position size in USD
        leverage: Leverage multiplier
    
    Returns:
        float: Margin required in USD
    """
    return position_size_usd / leverage


def calculate_pnl_pct(entry_price, exit_price, side='long'):
    """
    Calculate PnL percentage
    
    Args:
        entry_price: Entry price
        exit_price: Exit price
        side: 'long' or 'short'
    
    Returns:
        float: PnL percentage
    """
    if side == 'long':
        return ((exit_price - entry_price) / entry_price) * 100
    else:
        return ((entry_price - exit_price) / entry_price) * 100


def is_safe_leverage(leverage, max_leverage=10):
    """
    Check if leverage is within safe limits
    
    Args:
        leverage: Leverage to check
        max_leverage: Maximum safe leverage
    
    Returns:
        bool: True if safe
    """
    return 1 <= leverage <= max_leverage


def calculate_risk_reward_ratio(entry_price, take_profit_price, stop_loss_price, side='long'):
    """
    Calculate risk/reward ratio
    
    Args:
        entry_price: Entry price
        take_profit_price: Take profit price
        stop_loss_price: Stop loss price
        side: 'long' or 'short'
    
    Returns:
        float: Risk/reward ratio
    """
    if side == 'long':
        reward = take_profit_price - entry_price
        risk = entry_price - stop_loss_price
    else:
        reward = entry_price - take_profit_price
        risk = stop_loss_price - entry_price
    
    if risk == 0:
        return 0
    
    return reward / risk


def format_usd(amount):
    """Format USD amount for display"""
    return f"${amount:,.2f}"


def format_percent(value):
    """Format percentage for display"""
    return f"{value:.2f}%"


def clamp(value, min_value, max_value):
    """
    Clamp value between min and max
    
    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value
    
    Returns:
        float: Clamped value
    """
    return max(min_value, min(value, max_value))

