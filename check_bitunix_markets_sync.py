
import requests
import json

def check_markets():
    try:
        print("Fetching Bitunix Futures Markets (Sync)...")
        # Try finding the tickers list
        url = "https://fapi.bitunix.com/api/v1/futures/market/tickers"
        
        headers = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
        except:
            print("Failed to parse JSON")
            print(response.text[:200])
            return

        if data.get('code') != 0:
            print(f"Error fetching markets: {data}")
            return

        tickers = data.get('data', [])
        print(f"Found {len(tickers)} active futures pairs.")
        
        sol_pairs = [t for t in tickers if 'SOL' in t.get('symbol', '')]
        print(f"\nSOL Pairs found:")
        for p in sol_pairs:
            print(f" - Symbol: {p['symbol']} | Price: {p.get('price', 0)}")
            
        # Check specific order book
        print("\nChecking Order Book for 'SOLUSDT'...")
        url = "https://fapi.bitunix.com/api/v1/futures/market/depth?symbol=SOLUSDT"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Depth Response Code: {response.status_code}")
        print(f"Depth Response: {response.text[:100]}...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_markets()
