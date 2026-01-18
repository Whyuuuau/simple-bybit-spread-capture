
import requests

try:
    print("Testing SOLUSDT Kline...")
    url = "https://fapi.bitunix.com/api/v1/futures/market/kline"
    params = {'symbol': 'SOLUSDT', 'interval': '1m', 'limit': 5}
    response = requests.get(url, params=params, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
