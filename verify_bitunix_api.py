"""
Bitunix API Verification Script
Tests all critical API endpoints to ensure bot will work correctly
"""
import asyncio
import os
from dotenv import load_dotenv
from bitunix_exchange import BitunixExchange

load_dotenv()

async def main():
    print("=" * 80)
    print("🔍 BITUNIX API VERIFICATION")
    print("=" * 80)
    
    exchange = BitunixExchange({
        'apiKey': os.getenv('BITUNIX_API_KEY'),
        'secret': os.getenv('BITUNIX_API_SECRET'),
    })
    
    symbol = 'SOL/USDT:USDT'
    
    try:
        # Test 1: Fetch Ticker
        print("\n1️⃣ Testing fetch_ticker...")
        ticker = await exchange.fetch_ticker(symbol)
        print(f"   ✅ Ticker: bid={ticker.get('bid')}, ask={ticker.get('ask')}, last={ticker.get('last')}")
        
        # Test 2: Fetch Balance
        print("\n2️⃣ Testing fetch_balance...")
        balance = await exchange.fetch_balance()
        print(f"   ✅ Balance: {balance.get('USDT', {}).get('free', 0)} USDT free")
        
        # Test 3: Fetch Positions
        print("\n3️⃣ Testing fetch_positions...")
        positions = await exchange.fetch_positions([symbol])
        print(f"   ✅ Positions: {len(positions)} position(s)")
        for pos in positions:
            print(f"      - {pos.get('side')}: {pos.get('contracts')} contracts, value=${pos.get('notional', 0)}")
        
        # Test 4: Fetch Open Orders
        print("\n4️⃣ Testing fetch_open_orders...")
        orders = await exchange.fetch_open_orders(symbol)
        print(f"   ✅ Open Orders: {len(orders)} order(s)")
        if orders:
            print(f"      Sample order ID: {orders[0].get('id')}")
            print(f"      Sample order: {orders[0].get('side')} {orders[0].get('amount')} @ {orders[0].get('price')}")
        
        # Test 5: Fetch Order Book
        print("\n5️⃣ Testing fetch_order_book...")
        orderbook = await exchange.fetch_order_book(symbol)
        print(f"   ✅ Order Book: {len(orderbook.get('bids', []))} bids, {len(orderbook.get('asks', []))} asks")
        if orderbook.get('bids'):
            print(f"      Best bid: {orderbook['bids'][0][0]}")
        if orderbook.get('asks'):
            print(f"      Best ask: {orderbook['asks'][0][0]}")
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\n📊 Summary:")
        print(f"   - Ticker: OK")
        print(f"   - Balance: OK")
        print(f"   - Positions: OK ({len(positions)} position(s))")
        print(f"   - Open Orders: OK ({len(orders)} order(s))")
        print(f"   - Order Book: OK")
        print("\n🎯 Bot is ready to trade!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
