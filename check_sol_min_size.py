"""
Fetch SOL minimum order size from Bitunix
"""
import asyncio
import aiohttp

async def get_sol_min_size():
    url = "https://fapi.bitunix.com/api/v1/futures/market/trading_pairs"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            
            if data.get('code') == 0:
                pairs = data.get('data', [])
                for pair in pairs:
                    if pair.get('symbol') == 'SOLUSDT':
                        print("=" * 80)
                        print("SOL/USDT FUTURES SPECIFICATIONS")
                        print("=" * 80)
                        print(f"Symbol: {pair.get('symbol')}")
                        print(f"Min Trade Volume: {pair.get('minTradeVolume')} SOL")
                        print(f"Base Precision: {pair.get('basePrecision')}")
                        print(f"Quote Precision: {pair.get('quotePrecision')}")
                        print(f"Min Leverage: {pair.get('minLeverage')}")
                        print(f"Max Leverage: {pair.get('maxLeverage')}")
                        print("=" * 80)
                        return pair
                        
                print("⚠️ SOLUSDT not found in trading pairs")
            else:
                print(f"❌ API Error: {data}")

if __name__ == "__main__":
    asyncio.run(get_sol_min_size())
