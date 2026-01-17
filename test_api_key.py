"""Quick API Key Test - Diagnose Bybit Authentication"""
import os
import ccxt
from dotenv import load_dotenv

# Load environment
load_dotenv()

api_key = os.getenv('BYBIT_API_KEY')
api_secret = os.getenv('BYBIT_API_SECRET')

print("=" * 80)
print("🔍 BYBIT API KEY DIAGNOSTIC TEST")
print("=" * 80)

# Check if keys loaded
if not api_key or not api_secret:
    print("❌ API keys NOT loaded from .env!")
    print(f"   BYBIT_API_KEY: {api_key}")
    print(f"   BYBIT_API_SECRET: {api_secret}")
    exit(1)

print(f"✅ API Key loaded: {api_key[:15]}...")
print(f"✅ Secret loaded: {api_secret[:15]}...")
print()

# Test 1: Public API (no auth needed)
print("TEST 1: Public API (No Authentication)")
print("-" * 80)
try:
    exchange = ccxt.bybit()
    ticker = exchange.fetch_ticker('ETH/USDT')
    print(f"✅ Public API works! ETH price: ${ticker['last']}")
except Exception as e:
    print(f"❌ Public API failed: {e}")

print()

# Test 2: Private API with credentials
print("TEST 2: Private API (With Authentication - MAINNET)")
print("-" * 80)
try:
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
    })
    
    # Try to fetch balance
    balance = exchange.fetch_balance()
    print("✅ Authentication SUCCESS!")
    print(f"   Total balance: {balance.get('total', {})}")
    
except ccxt.AuthenticationError as e:
    print(f"❌ Authentication FAILED: {e}")
    print()
    print("POSSIBLE CAUSES:")
    print("1. API key not enabled for trading")
    print("2. API permissions insufficient")
    print("3. IP whitelist blocking")
    print("4. API key from wrong account type")
    
except Exception as e:
    print(f"❌ Other error: {e}")

print()

# Test 3: Futures/Derivatives specific
print("TEST 3: Futures Market Data")
print("-" * 80)
try:
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
        }
    })
    
    # Try futures ticker
    ticker = exchange.fetch_ticker('ETH/USDT:USDT')
    print(f"✅ Futures API works! ETH perpetual: ${ticker['last']}")
    
except Exception as e:
    print(f"❌ Futures API failed: {e}")

print()
print("=" * 80)
print("🎯 RECOMMENDATION:")
print("=" * 80)
print("If TEST 1 passes but TEST 2/3 fail:")
print("→ Check API key permissions in Bybit")
print("→ Make sure 'Contract Trading' is enabled")
print("→ Disable IP whitelist (or add VPS IP)")
print("→ Ensure API key is ACTIVE (not expired)")
print()
print("Go to: bybit.com → Account → API Management")
print("=" * 80)
