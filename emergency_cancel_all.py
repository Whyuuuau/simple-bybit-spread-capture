"""
EMERGENCY: Cancel ALL open orders manually
Run this ONCE to clear all stacked orders
"""
import asyncio
import os
from dotenv import load_dotenv
from bitunix_exchange import BitunixExchange

load_dotenv()

async def emergency_cancel_all():
    print("=" * 80)
    print("🚨 EMERGENCY ORDER CANCELLATION")
    print("=" * 80)
    
    exchange = BitunixExchange({
        'apiKey': os.getenv('BITUNIX_API_KEY'),
        'secret': os.getenv('BITUNIX_API_SECRET'),
    })
    
    symbol = 'SOL/USDT:USDT'
    
    try:
        # Fetch all open orders
        print("\n1️⃣ Fetching open orders...")
        orders = await exchange.fetch_open_orders(symbol)
        print(f"   Found {len(orders)} open orders")
        
        if not orders:
            print("\n✅ No orders to cancel!")
            return
        
        # Show first few orders
        print("\n📋 Sample orders:")
        for i, order in enumerate(orders[:5]):
            print(f"   {i+1}. ID: {order['id']} | {order['side'].upper()} {order['amount']} @ {order['price']}")
        
        if len(orders) > 5:
            print(f"   ... and {len(orders) - 5} more")
        
        # Confirm
        print(f"\n⚠️  About to cancel {len(orders)} orders!")
        confirm = input("Type 'YES' to proceed: ")
        
        if confirm != 'YES':
            print("❌ Cancelled by user")
            return
        
        # Cancel in batches of 10
        print("\n2️⃣ Cancelling orders in batches...")
        order_ids = [o['id'] for o in orders]
        
        cancelled = 0
        for i in range(0, len(order_ids), 10):
            batch = order_ids[i:i+10]
            print(f"   Batch {i//10 + 1}: Cancelling {len(batch)} orders...")
            
            try:
                await exchange.cancel_orders(batch, symbol)
                cancelled += len(batch)
                print(f"   ✅ Cancelled {len(batch)} orders")
                await asyncio.sleep(0.5)  # Rate limit
            except Exception as e:
                print(f"   ❌ Batch failed: {e}")
                # Try individual
                for oid in batch:
                    try:
                        await exchange.cancel_order(oid, symbol)
                        cancelled += 1
                        print(f"   ✅ Cancelled order {oid}")
                    except Exception as e2:
                        print(f"   ❌ Failed to cancel {oid}: {e2}")
        
        print(f"\n✅ DONE! Cancelled {cancelled}/{len(orders)} orders")
        
        # Verify
        print("\n3️⃣ Verifying...")
        remaining = await exchange.fetch_open_orders(symbol)
        print(f"   Remaining orders: {len(remaining)}")
        
        if len(remaining) == 0:
            print("\n🎉 SUCCESS! All orders cancelled!")
        else:
            print(f"\n⚠️  {len(remaining)} orders still remain. Run script again if needed.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(emergency_cancel_all())
