"""
Debug script to test fetch_open_orders endpoint
"""
import asyncio
import os
from dotenv import load_dotenv
from bitunix_exchange import BitunixExchange

load_dotenv()

async def test_fetch_orders():
    exchange = BitunixExchange({
        'apiKey': os.getenv('BITUNIX_API_KEY'),
        'secret': os.getenv('BITUNIX_API_SECRET'),
    })
    
    symbol = 'SOL/USDT:USDT'
    
    print("=" * 80)
    print("TESTING FETCH OPEN ORDERS")
    print("=" * 80)
    
    try:
        orders = await exchange.fetch_open_orders(symbol)
        print(f"\n✅ SUCCESS: Fetched {len(orders)} orders")
        
        if orders:
            print("\nFirst order sample:")
            print(orders[0])
        else:
            print("\n⚠️ No open orders found")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(test_fetch_orders())
