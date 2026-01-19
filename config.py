import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Bitunix Keys (NEW)
bitunix_api_key = os.getenv('BITUNIX_API_KEY')
bitunix_api_secret = os.getenv('BITUNIX_API_SECRET')

# Exchange selection
EXCHANGE_NAME = 'bitunix'
 





# ============================================================================
# TRADING PARAMETERS
# ============================================================================

# Symbol Configuration
symbol = 'SOL/USDT:USDT'  # Internal format
base_symbol = 'SOLUSDT'   # API format

# Leverage Settings
LEVERAGE = 10  
MAX_LEVERAGE = 50 

# ============================================================================
# ORDER SETTINGS
# ============================================================================

num_orders = 4  # Hybrid: Balance between coverage and management
ORDER_BOOK_DEPTH = 20 

ORDER_REFRESH_INTERVAL = 3   # Reduced from 1 to avoid rate limits (10 req/sec)
DATA_UPDATE_INTERVAL = 120  # Reduced from 60 to minimize API calls  

# ============================================================================
# SPREAD & PRICING (HYBRID STRATEGY: Volume + Profit Optimized)
MIN_SPREAD_PCT = 0.12   # Hybrid: Profitable in all scenarios, good fill rate
MAX_SPREAD_PCT = 0.20   # Adaptive ceiling for volatile markets
TARGET_SPREAD_MULTIPLIER = 1.0  # Base multiplier  

# ============================================================================
# POSITION & RISK MANAGEMENT
# ============================================================================

MAX_POSITION_SIZE_USD = 200  # Lowered from 450 to prevent margin lock with small equity
POSITION_REBALANCE_THRESHOLD_USD = 100  # Lowered from 250 to trigger earlier rebalance
POSITION_CHECK_INTERVAL = 5  

MIN_ORDER_SIZE_USD = 5    # Minimum notional
MAX_ORDER_SIZE_USD = 150  # Increased for volume acceleration
BASE_ORDER_SIZE_USD = 120  # HYBRID: Optimized for volume + profit (was 80)

MAX_DAILY_LOSS_USD = -10   # SAFETY: Stop if lose $10
MAX_TOTAL_LOSS_USD = -20   # SAFETY: Stop if total loss > $20
STOP_LOSS_PCT = 4.0        
TAKE_PROFIT_PCT = 0.0015   

# ============================================================================
# VOLUME TARGETS
# ============================================================================

TARGET_VOLUME_PER_HOUR = 40000   
TARGET_VOLUME_PER_DAY = 1000000   

# ============================================================================
# ML MODEL SETTINGS
# ============================================================================

USE_ML_MODEL = True
ML_UPDATE_INTERVAL = 60
ML_LOOKBACK_PERIOD = 60
ML_FUTURE_WINDOW = 5
ML_PROFIT_THRESHOLD_PCT = 0.08
ML_CONFIDENCE_THRESHOLD = 0.60

# ============================================================================
# FEES & COSTS
# ============================================================================

MAKER_FEE_PCT = 0.02 
TAKER_FEE_PCT = 0.05 
FUNDING_FEE_INTERVAL = 8 * 3600 

# ============================================================================
# PRECISION SETTINGS
# ============================================================================

PRICE_PRECISION = 3   # SOL needs 3 decimals usually (e.g. 143.505)
AMOUNT_PRECISION = 1  # SOL quantity usually 1 decimal (e.g. 0.1 SOL)

# ============================================================================
# BALANCE & CAPITAL
# ============================================================================

INITIAL_BALANCE_USD = 100  

# ============================================================================
# SAFETY & MONITORING
# ============================================================================

ENABLE_EMERGENCY_STOP = True
EMERGENCY_STOP_LOSS_PCT = 15.0

STATS_LOG_INTERVAL = 10    # Reduced from 5 to minimize API calls
PERFORMANCE_CHECK_INTERVAL = 300

# ============================================================================
# EXCHANGE-SPECIFIC CONFIGS
# ============================================================================

EXCHANGE_CONFIG = {
    'bitunix': {
        'futures_format': True,
        'symbol_format': 'ETH/USDT:USDT', 
        'min_order_usd': 5, # Bitunix might allow smaller? Keeping safe.
        'max_leverage': 125,
        'supports_hedge_mode': True, 
        'funding_interval_hours': 8,
    }
}

# Get current exchange config
current_config = EXCHANGE_CONFIG.get(EXCHANGE_NAME, EXCHANGE_CONFIG['bitunix'])

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_symbol_format():
    return current_config['symbol_format']

def calculate_position_size_from_usd(usd_value, price, leverage=LEVERAGE):
    return usd_value / price

def calculate_margin_required(position_size_usd, leverage=LEVERAGE):
    return position_size_usd / leverage

def calculate_liquidation_price(entry_price, leverage, side='long', maintenance_margin=0.005):
    if side == 'long':
        liq_price = entry_price * (1 - 1/leverage + maintenance_margin)
    else:
        liq_price = entry_price * (1 + 1/leverage - maintenance_margin)
    return liq_price

def validate_config():
    issues = []
    
    if EXCHANGE_NAME == 'bitunix':
        if not bitunix_api_key or not bitunix_api_secret:
             issues.append("⚠️ Bitunix API keys not set in .env (BITUNIX_API_KEY, BITUNIX_API_SECRET)")
    
    return issues

config_issues = validate_config()
if config_issues:
    print("⚠️ Configuration Issues Found:")
    for issue in config_issues:
        print(f"  {issue}")
    print()


# ============================================================================
# EXCHANGE INITIALIZATION (MOVED TO BOTTOM)
# ============================================================================

# Keys loaded at top


# Initialize exchange
exchange = None

try:
    if EXCHANGE_NAME == 'bitunix':
        from bitunix_exchange import BitunixExchange
        exchange = BitunixExchange({
            'apiKey': bitunix_api_key,
            'secret': bitunix_api_secret,
            'options': {
                'defaultType': 'swap',
                'price_precision': PRICE_PRECISION,
                'amount_precision': AMOUNT_PRECISION,
            }
        })
        print("✅ Initialized Bitunix Exchange")
        
except Exception as e:
    print(f"❌ Error initializing exchange: {e}")
    # Fallback/Safety
    exchange = None
