
import requests
import json
import logging

logging.basicConfig(filename='debug_markets.log', level=logging.INFO)

def check_markets():
    try:
        print("Fetching Bitunix Futures Markets...")
        logging.info("Fetching markets...")
        
        url = "https://fapi.bitunix.com/api/v1/futures/market/tickers"
        response = requests.get(url, timeout=15)
        
        logging.info(f"Response Status: {response.status_code}")
        
        if response.status_code != 200:
            logging.error(f"Error: {response.text}")
            return

        data = response.json()
        if data.get('code') != 0:
            logging.error(f"API Error: {data}")
            return
            
        tickers = data.get('data', [])
        logging.info(f"Found {len(tickers)} tickers")
        
        with open('tickers_dump.json', 'w') as f:
            json.dump(tickers, f, indent=2)
            
        logging.info("Saved to tickers_dump.json")
        
        # Filter for SOL
        sol_tickers = [t for t in tickers if 'SOL' in t.get('symbol', '').upper()]
        logging.info(f"SOL Tickers: {sol_tickers}")
        print(f"Found {len(sol_tickers)} SOL tickers. Check debug_markets.log")

    except Exception as e:
        logging.error(f"Exception: {e}")
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_markets()
