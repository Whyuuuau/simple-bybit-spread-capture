
import asyncio
import aiohttp
import json

async def check_markets():
    try:
        async with aiohttp.ClientSession() as session:
            # 1. Fetch Tickers/Markets to see available symbols
            print("Fetching Bitunix Futures Markets...")
            url = "https://fapi.bitunix.com/api/v1/futures/market/tickers"
            async with session.get(url) as response:
                text = await response.text()
                data = json.loads(text)
                
                if data.get('code') != 0:
                    print(f"Error fetching markets: {data}")
                    return

                tickers = data.get('data', [])
                print(f"Found {len(tickers)} active futures pairs.")
                
                sol_pairs = [t for t in tickers if 'SOL' in t['symbol']]
                print(f"\nSOL Pairs found:")
                for p in sol_pairs:
                    print(f" - Symbol: {p['symbol']} | Price: {p['price']}")
                    
            # 2. Check Order Book for SOLUSDT explicitly
            print("\nChecking Order Book for 'SOLUSDT'...")
            url_depth = "https://fapi.bitunix.com/api/v1/futures/market/depth?symbol=SOLUSDT"
            async with session.get(url_depth) as response:
                text = await response.text()
                print(f"Order Book Response: {text[:200]}...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_markets())
