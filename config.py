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
# BYBIT DEMO MAINNET SETUP
# ============================================================================

# Exchange selection
EXCHANGE_NAME = 'bybit'  # ✅ BYBIT DEMO MAINNET

# Demo Trading Configuration
# Uses Bybit Demo environment with virtual balance
# Domain: https://api-demo.bybit.com
# Get API keys from: https://demo.bybit.com/app/user/api-management

# Initialize exchange with demo configuration
# CRITICAL: Demo API has limited endpoints compared to mainnet
# We must skip auto market loading to avoid error 10032
exchange = ccxt.bybit({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'linear',  # Perpetual futures
        'loadMarkets': False,  # Skip auto-loading to avoid /v5/asset/* endpoints
        'fetchCurrencies': False,  # Skip currency fetching (not available in demo)
    },
    'urls': {
        'api': {
            'public': 'https://api-demo.bybit.com',
            'private': 'https://api-demo.bybit.com',
        }
    }
})

# Note: Demo API limitations
# ✅ Available: Order, Position, Account wallet, Execution endpoints
# ❌ Not available: Asset management, Coin info endpoints
# See: https://bybit-exchange.github.io/docs/v5/demo

# Manual market setup for demo (bypass auto-loading)
# CRITICAL: Use set_markets to populate all internal structures (ids, symbols, etc.) correctly
# This fixes the 'KeyError: 0' issue in safe_market
market_info = {
    'id': 'SOLUSDT',
    'symbol': 'SOL/USDT:USDT',
    'base': 'SOL',
    'quote': 'USDT',
    'settle': 'USDT',
    'baseId': 'SOL',
    'quoteId': 'USDT',
    'settleId': 'USDT',
    'type': 'swap',
    'spot': False,
    'margin': False,
    'swap': True,
    'future': False,
    'option': False,
    'active': True,
    'contract': True,
    'linear': True,
    'inverse': False,
    'taker': 0.0006,
    'maker': 0.0001,
    'contractSize': 1.0,
    'expiry': None,
    'expiryDatetime': None,
    'strike': None,
    'optionType': None,
    'precision': {
        'amount': 0.01,  # Tick size for SOL amount
        'price': 0.01,   # Tick size for SOL price
        'base': 8,
        'quote': 8,
    },
    'limits': {
        'leverage': {
            'min': 1,
            'max': 50,
        },
        'amount': {
            'min': 0.1,  # Minimum 0.1 SOL (~$14)
            'max': 1000000,
        },
        'price': {
            'min': 0.01,
            'max': 1000000,
        },
        'cost': {
            'min': 10,  # Minimum $10 notional
            'max': None,
        },
    },
    'info': {}
}

# Apply market structure
# set_markets expects a LIST of market dictionaries
exchange.set_markets([market_info])

# Mark as loaded to prevent auto-loading attempts
exchange.has['fetchMarkets'] = False

# ============================================================================
# TRADING PARAMETERS
# ============================================================================

# Symbol Configuration
symbol = 'SOL/USDT:USDT'  # ETH Futures
base_symbol = 'ETHUSDT'  # Format untuk beberapa API calls

# Leverage Settings
# Leverage Settings
LEVERAGE = 10  # Increased to 10x (User Request)
MAX_LEVERAGE = 12  # Max limit

# ============================================================================
# ORDER SETTINGS
# ============================================================================

# Number of orders per side
# Number of orders per side
num_orders = 5  # Reduced to 5 (Lighter payload for 3s Speed)

# Order book depth
ORDER_BOOK_DEPTH = 20  # Number of levels to fetch from order book

# Order refresh settings
# Order refresh settings
ORDER_REFRESH_INTERVAL = 3   # Refresh every 3 seconds (TURBO MODE)
DATA_UPDATE_INTERVAL = 60  # Update historical data every 60 seconds

# ============================================================================
# SPREAD & PRICING
# ============================================================================

# Spread settings (optimized for fees)
# Spread settings (optimized for fees)
# Fees: Maker 0.02% x 2 = 0.04% Roundtrip.
# Target: 0.06% Spread gives 0.02% Net Profit per trade.
MIN_SPREAD_PCT = 0.06   # 0.06% minimum (Tight & Profitable)
MAX_SPREAD_PCT = 0.25   # 0.25% maximum
TARGET_SPREAD_MULTIPLIER = 1.0  # Use full spread width

# ============================================================================
# POSITION & RISK MANAGEMENT
# ============================================================================

# Position limits
# Position limits
MAX_POSITION_SIZE_USD = 200  # Increased to $200 (Allows ~13 orders of 0.1 SOL)
POSITION_REBALANCE_THRESHOLD_USD = 100  # Rebalance when exceeds $100
POSITION_CHECK_INTERVAL = 10  # Check position every 10 seconds

# Order size limits
# Order size limits
MIN_ORDER_SIZE_USD = 15   # Must be >= 0.1 SOL (~$15)
MAX_ORDER_SIZE_USD = 25  # Increased slightly
BASE_ORDER_SIZE_USD = 15  # Base 0.1 SOL

# Risk limits
# Risk limits
MAX_DAILY_LOSS_USD = -50   # Increased risk tolerance
MAX_TOTAL_LOSS_USD = -80   # Emergency stop at $80 loss
STOP_LOSS_PCT = 4.0        # 4% stop loss per position
TAKE_PROFIT_PCT = 0.002    # 0.2% Take Profit (Covers ~0.12% fees + profit)

# ============================================================================
# VOLUME TARGETS
# ============================================================================

TARGET_VOLUME_PER_HOUR = 3000   # Target $3k volume/hour
TARGET_VOLUME_PER_DAY = 70000   # Target $70k volume/day

# ============================================================================
# ML MODEL SETTINGS
# ============================================================================

# ML Model parameters
USE_ML_MODEL = True
ML_UPDATE_INTERVAL = 60
ML_LOOKBACK_PERIOD = 60
ML_FUTURE_WINDOW = 5
ML_PROFIT_THRESHOLD_PCT = 0.08
ML_CONFIDENCE_THRESHOLD = 0.60

# ============================================================================
# FEES & COSTS
# ============================================================================

# Bybit futures fees
MAKER_FEE_PCT = 0.01  # 0.01% maker fee
TAKER_FEE_PCT = 0.06  # 0.06% taker fee
FUNDING_FEE_INTERVAL = 8 * 3600  # 8 hours in seconds

# ============================================================================
# PRECISION SETTINGS
# ============================================================================

PRICE_PRECISION = 2  # ETH typically 2 decimals
AMOUNT_PRECISION = 3  # ETH typically 3 decimals

# ============================================================================
# BALANCE & CAPITAL
# ============================================================================

# Initial balance tracking
INITIAL_BALANCE_USD = 100  # $100 starting capital

# ============================================================================
# SAFETY & MONITORING
# ============================================================================

# Emergency stops
ENABLE_EMERGENCY_STOP = True
EMERGENCY_STOP_LOSS_PCT = 15.0

# Monitoring intervals
STATS_LOG_INTERVAL = 60
PERFORMANCE_CHECK_INTERVAL = 300

# ============================================================================
# EXCHANGE-SPECIFIC CONFIGS
# ============================================================================

EXCHANGE_CONFIG = {
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

# Calculate minimum profitable spread
# Round-trip with maker both sides: 0.01% + 0.01% = 0.02%
# Round-trip with maker+taker: 0.01% + 0.06% = 0.07%
# Safety margin: 1.5x
MIN_PROFITABLE_SPREAD_PCT = (MAKER_FEE_PCT + TAKER_FEE_PCT) * 1.5  # 0.105%

# Ensure MIN_SPREAD is at least profitable
if MIN_SPREAD_PCT < MIN_PROFITABLE_SPREAD_PCT:
    MIN_SPREAD_PCT = MIN_PROFITABLE_SPREAD_PCT

# ============================================================================
# DEMO MONEY APPLICATION
# ============================================================================

async def apply_demo_money(coin='USDT', amount='100000'):
    """
    Apply for demo trading money
    
    Endpoint: POST /v5/account/demo-apply-money
    Max amounts per request:
    - BTC: "15"
    - ETH: "200"
    - USDT: "100000"
    - USDC: "100000"
    
    Args:
        coin: Coin to add (BTC, ETH, USDT, USDC)
        amount: Amount string
        
    Returns:
        bool: Success status
    """
    try:
        params = {
            'adjustType': 0,  # Add demo funds
            'utaDemoApplyMoney': [
                {
                    'coin': coin,
                    'amountStr': amount
                }
            ]
        }
        result = await exchange.privatePostV5AccountDemoApplyMoney(params)
        logger.info(f"✅ Demo money applied: {amount} {coin}")
        return True
    except Exception as e:
        logger.error(f"Failed to apply demo money: {e}")
        return False

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration parameters"""
    issues = []
    
    # Check API keys
    if not api_key or not api_secret or 'YOUR_' in api_key:
        issues.append("⚠️ Demo API keys not set in .env file")
        issues.append("   Get keys from: https://demo.bybit.com/app/user/api-management")
    
    # Check leverage
    if LEVERAGE > current_config['max_leverage']:
        issues.append(f"⚠️ Leverage {LEVERAGE}x exceeds max {current_config['max_leverage']}x")
    
    # Check order sizes
    if MIN_ORDER_SIZE_USD < current_config['min_order_usd']:
        issues.append(f"⚠️ Min order size ${MIN_ORDER_SIZE_USD} below minimum ${current_config['min_order_usd']}")
    
    # Check spread
    if MIN_SPREAD_PCT < MIN_PROFITABLE_SPREAD_PCT:
        issues.append(f"⚠️ Min spread {MIN_SPREAD_PCT}% may not be profitable (need >{MIN_PROFITABLE_SPREAD_PCT:.3f}%)")
    
    # Demo-specific notes
    issues.append("ℹ️ Using Bybit Demo Mainnet (https://api-demo.bybit.com)")
    issues.append("ℹ️ Note: Leverage setting may be pre-configured in demo (error 10032 is normal)")
    
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
