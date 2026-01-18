
import asyncio
import os
import time
from dotenv import load_dotenv
from bitunix_exchange import BitunixExchange

# Load env/keys
load_dotenv()
API_KEY = os.getenv('BITUNIX_API_KEY')
API_SECRET = os.getenv('BITUNIX_API_SECRET')

async def run_debug():
    print("--- Debugging Bitunix Trade History ---")
    exchange = BitunixExchange({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
    })
    
    symbol = "SOL/USDT:USDT"
    print(f"Fetching trades for {symbol}...")
    
    # Try Endpoint 1: get_history_trades
    try:
        print("\n[Attempt 1] Calling fetch_my_trades (get_history_trades)...")
        trades = await exchange.fetch_my_trades(symbol, limit=20)
        print(f"Result Count: {len(trades)}")
        if len(trades) > 0:
            print(f"Sample Trade: {trades[0]}")
        else:
            print("No trades found.")
    except Exception as e:
        print(f"Error in fetch_my_trades: {e}")

    # Try Low-Level Request to see RAW response
    try:
        clean_symbol = "SOLUSDT"
        print(f"\n[Attempt 2] RAW Request to /futures/trade/get_history_trades for {clean_symbol}...")
        raw_data = await exchange._request('GET', '/futures/trade/get_history_trades', params={'symbol': clean_symbol, 'limit': 20}, signed=True)
        print(f"RAW TYPE: {type(raw_data)}")
        print(f"RAW DATA: {raw_data}")
        
    except Exception as e:
        print(f"RAW Request Error: {e}")
        
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(run_debug())
