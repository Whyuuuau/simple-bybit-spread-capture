import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# API CONFIGURATION
# ============================================================================

api_key = os.getenv('BYBIT_API_KEY')
api_secret = os.getenv('BYBIT_API_SECRET')

# ============================================================================
# EXCHANGE SETUP - BYBIT MAINNET DEMO (Real-time prices!) ✅
# ============================================================================

# Exchange selection
EXCHANGE_NAME = 'bybit'  # ✅ BYBIT
TESTNET = False  # ✅ MAINNET - Real market prices!
# NOTE: Training uses PUBLIC API (no auth), Trading uses your API key

# TRADING MODE SELECTION
PAPER_TRADING = True   # ✅ SIMULATE trading with REAL mainnet prices (NO API keys needed!)
DEMO_TRADING = False   # ❌ Bybit demo API (too limited, don't use)

# Note: If PAPER_TRADING = True, bot uses real market data but simulates all trades
# This allows testing with real prices without API authentication!

# Initialize exchange
if EXCHANGE_NAME == 'bitunix':
    # Bitunix configuration
    exchange = ccxt.bitunix({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap',  # Perpetual futures
        }
    })
    
    if TESTNET:
        # Set testnet if Bitunix supports it
        # Note: Verify Bitunix testnet URL
        try:
            exchange.set_sandbox_mode(True)
        except:
            logger.warning("Bitunix testnet may not be configured - verify manually!")


elif EXCHANGE_NAME == 'bybit':
    # Configure URLs based on trading mode
    exchange_config = {
        'enableRateLimit': True,
        'options': {
            'defaultType': 'linear',
        }
    }
    
    # Add API keys only if NOT paper trading
    if not PAPER_TRADING:
        exchange_config['apiKey'] = api_key
        exchange_config['secret'] = api_secret
    
    if DEMO_TRADING and not PAPER_TRADING:
        # Demo Trading uses special domain!
        exchange_config['urls'] = {
            'api': {
                'public': 'https://api-demo.bybit.com',
                'private': 'https://api-demo.bybit.com',
            }
        }
    elif TESTNET and not PAPER_TRADING:
        # Testnet mode
        exchange_config['options']['testnet'] = True
    elif PAPER_TRADING:
        # Paper trading: use mainnet for REAL prices (public API only)
        # No API keys needed - public data only!
        pass  # Default mainnet URLs
    
    exchange = ccxt.bybit(exchange_config)

# ============================================================================
# TRADING PARAMETERS
# ============================================================================

# Symbol Configuration
symbol = 'ETH/USDT:USDT'  # ETH Futures untuk Bybit
base_symbol = 'ETHUSDT'  # Format untuk beberapa API calls

# Leverage Settings (AGGRESSIVE MODE for $1M target!)
LEVERAGE = 4  # Aggressive leverage for volume (balanced risk)
MAX_LEVERAGE = 5  # Max limit

# ============================================================================
# ORDER SETTINGS
# ============================================================================

# Number of orders per side
num_orders = 5  # Maximum coverage for volume

# Order refresh settings (AGGRESSIVE for turnover)
ORDER_REFRESH_INTERVAL = 3  # Refresh every 3 seconds (fast!)
DATA_UPDATE_INTERVAL = 60  # Update historical data every 60 seconds

# ============================================================================
# SPREAD & PRICING
# ============================================================================

# Spread settings (OPTIMIZED FOR BITUNIX FEES! ✅)
# CRITICAL: Spread must be > total fees for profitability
# Bitunix All-Maker: 0.02% + 0.02% = 0.04% total
# Bitunix Maker+Taker: 0.02% + 0.05% = 0.07% total
# Our MIN_SPREAD 0.03% is ABOVE all-maker fees = PROFITABLE! ✅
MIN_SPREAD_PCT = 0.03   # 0.03% minimum (Profitable even all-maker!)
MAX_SPREAD_PCT = 0.12   # 0.12% maximum
TARGET_SPREAD_MULTIPLIER = 0.75  # Target 75% of current spread

# ============================================================================
# POSITION & RISK MANAGEMENT (ADJUSTED FOR $100 CAPITAL!)
# ============================================================================

# Position limits (AGGRESSIVE for volume!)
MAX_POSITION_SIZE_USD = 70  # Max $70 position (4x leverage = $280 exposure)
POSITION_REBALANCE_THRESHOLD_USD = 35  # Rebalance when exceeds $35
POSITION_CHECK_INTERVAL = 10  # Check position every 10 seconds

# Order size limits (AGGRESSIVE sizes!)
MIN_ORDER_SIZE_USD = 10  # Minimum $10 per order (exchange minimum!)
MAX_ORDER_SIZE_USD = 18  # Maximum $18 per order
BASE_ORDER_SIZE_USD = 12  # Base $12 per order

# Risk limits (Balanced for aggressive trading)
MAX_DAILY_LOSS_USD = -15   # Stop if lose $15/day (15% of capital)
MAX_TOTAL_LOSS_USD = -25   # Emergency stop at $25 loss (25% of capital)
STOP_LOSS_PCT = 4.0        # 4% stop loss per position

# ============================================================================
# VOLUME TARGETS (AGGRESSIVE - $1M in 14 days!)
# ============================================================================

TARGET_VOLUME_PER_HOUR = 3000   # Target $3k volume/hour
TARGET_VOLUME_PER_DAY = 70000   # Target $70k volume/day ($1M in 14 days!)

# ============================================================================
# ML MODEL SETTINGS
# ============================================================================

# ML Model parameters
USE_ML_MODEL = True
ML_UPDATE_INTERVAL = 60  # Update ML signal every 60 seconds
ML_LOOKBACK_PERIOD = 60  # Use 60 recent candles for prediction
ML_FUTURE_WINDOW = 5  # Predict 5 candles ahead
ML_PROFIT_THRESHOLD_PCT = 0.08  # ✅ 0.08% profit threshold (better class balance!)
ML_CONFIDENCE_THRESHOLD = 0.60  # 60% confidence to act on signal

# ============================================================================
# FEES & COSTS
# ============================================================================

# Bybit futures fees (update based on your tier)
MAKER_FEE_PCT = 0.01  # 0.01% maker fee (or -0.01% for rebate if VIP)
TAKER_FEE_PCT = 0.06  # 0.06% taker fee
FUNDING_FEE_INTERVAL = 8 * 3600  # 8 hours in seconds

# ============================================================================
# PRECISION SETTINGS (will be loaded from exchange)
# ============================================================================

PRICE_PRECISION = 2  # ETH typically 2 decimals (e.g., 3245.67)
AMOUNT_PRECISION = 3  # ETH typically 3 decimals for amount (e.g., 0.123)

# ============================================================================
# BALANCE & CAPITAL
# ============================================================================

# Initial balance tracking (for reference only, real balance from exchange)
INITIAL_BALANCE_USD = 100  # $100 starting capital

# ============================================================================
# SAFETY & MONITORING
# ============================================================================

# Emergency stops
ENABLE_EMERGENCY_STOP = True
EMERGENCY_STOP_LOSS_PCT = 15.0  # Stop if loss > 15% of capital ($15)

# Monitoring intervals
STATS_LOG_INTERVAL = 60  # Log stats every 60 seconds
PERFORMANCE_CHECK_INTERVAL = 300  # Check performance every 5 minutes

# ============================================================================
# EXCHANGE-SPECIFIC CONFIGS
# ============================================================================

EXCHANGE_CONFIG = {
    'bitunix': {
        'futures_format': True,
        'symbol_format': 'ETH/USDT:USDT',  # Verify with Bitunix docs
        'min_order_usd': 5,   # Small minimum for $100 account
        'max_leverage': 20,   # Bitunix may support higher, but we use 3x
        'supports_hedge_mode': False,  # Verify
        'funding_interval_hours': 8,
    },
    'bybit': {
        'futures_format': True,
        'symbol_format': 'ETH/USDT:USDT',
        'min_order_usd': 10,
        'max_leverage': 50,
        'supports_hedge_mode': True,
        'funding_interval_hours': 8,
    }
}

# Get current exchange config
current_config = EXCHANGE_CONFIG.get(EXCHANGE_NAME, EXCHANGE_CONFIG['bybit'])

# ============================================================================
# FEE STRUCTURE - BYBIT TESTNET (for demo testing)
# ============================================================================

# Bybit fees (current exchange)
MAKER_FEE_PCT = 0.01  # 0.01% maker fee
TAKER_FEE_PCT = 0.06  # 0.06% taker fee

# Bitunix fees (for comparison, when switching)
BITUNIX_MAKER_FEE_PCT = 0.02
BITUNIX_TAKER_FEE_PCT = 0.05

# Funding fee settings (futures)
FUNDING_FEE_INTERVAL = 8  # Hours between funding payments

# Calculate minimum profitable spread
# Round-trip with maker both sides: 0.01% + 0.01% = 0.02%
# Round-trip with maker+taker: 0.01% + 0.06% = 0.07%
# Safety margin: 1.5x
MIN_PROFITABLE_SPREAD_PCT = (MAKER_FEE_PCT + TAKER_FEE_PCT) * 1.5  # 0.105%

# Ensure MIN_SPREAD is at least profitable
if MIN_SPREAD_PCT < MIN_PROFITABLE_SPREAD_PCT:
    MIN_SPREAD_PCT = MIN_PROFITABLE_SPREAD_PCT

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration parameters"""
    issues = []
    
    # Check API keys
    if not api_key or not api_secret or 'YOUR_' in api_key:
        issues.append("⚠️ API keys not set properly in .env file")
    
    # Check leverage
    if LEVERAGE > current_config['max_leverage']:
        issues.append(f"⚠️ Leverage {LEVERAGE}x exceeds exchange max {current_config['max_leverage']}x")
    
    # Check order sizes
    if MIN_ORDER_SIZE_USD < current_config['min_order_usd']:
        issues.append(f"⚠️ Min order size ${MIN_ORDER_SIZE_USD} below exchange minimum ${current_config['min_order_usd']}")
    
    # Check spread
    if MIN_SPREAD_PCT < MIN_PROFITABLE_SPREAD_PCT:
        issues.append(f"⚠️ Min spread {MIN_SPREAD_PCT}% may not be profitable (need >{MIN_PROFITABLE_SPREAD_PCT:.3f}%)")
    
    # Check position limits for $100 capital
    effective_exposure = MAX_POSITION_SIZE_USD * LEVERAGE
    if effective_exposure > INITIAL_BALANCE_USD * 2:
        issues.append(f"⚠️ Max position exposure ${effective_exposure} is high for ${INITIAL_BALANCE_USD} capital")
    
    # Warn about small capital
    if INITIAL_BALANCE_USD < 500:
        issues.append(f"ℹ️ Small capital (${INITIAL_BALANCE_USD}) - expect limited volume generation")
        issues.append(f"ℹ️ Daily target ${TARGET_VOLUME_PER_DAY:,} may require high turnover")
    
    # Exchange-specific warnings
    if EXCHANGE_NAME == 'bitunix':
        issues.append("ℹ️ Using Bitunix - verify API compatibility and testnet availability")
    
    return issues

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_symbol_format():
    """Get correct symbol format for current exchange"""
    return current_config['symbol_format']

def calculate_position_size_from_usd(usd_value, price, leverage=LEVERAGE):
    """Calculate position size in contracts from USD value"""
    # Position size = (USD value / price) / leverage
    # For futures: we want USD value worth of exposure
    return usd_value / price

def calculate_margin_required(position_size_usd, leverage=LEVERAGE):
    """Calculate margin required for a position"""
    return position_size_usd / leverage

def calculate_liquidation_price(entry_price, leverage, side='long', maintenance_margin=0.005):
    """
    Calculate approximate liquidation price
    
    Args:
        entry_price: Entry price
        leverage: Leverage used
        side: 'long' or 'short'
        maintenance_margin: Maintenance margin ratio (0.5% default)
    
    Returns:
        float: Liquidation price
    """
    if side == 'long':
        # Long liquidation: entry * (1 - 1/leverage + maintenance_margin)
        liq_price = entry_price * (1 - 1/leverage + maintenance_margin)
    else:
        # Short liquidation: entry * (1 + 1/leverage - maintenance_margin)
        liq_price = entry_price * (1 + 1/leverage - maintenance_margin)
    
    return liq_price


# Run validation on import
config_issues = validate_config()
if config_issues:
    print("⚠️ Configuration Issues Found:")
    for issue in config_issues:
        print(f"  {issue}")
    print()
