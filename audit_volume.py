import os
import glob
import re

def audit_total_volume(log_dir='logs'):
    total_volume = 0.0
    total_trades = 0
    
    print(f"📂 Auditing logs in '{log_dir}'...")
    
    # Pattern to match trade logs
    # Format: TRADE FILLED | SYMBOL | SIDE | Price: 123.45 | Size: 0.123
    log_files = glob.glob(os.path.join(log_dir, 'trades_*.log'))
    
    if not log_files:
        print("❌ No trade logs found!")
        return
        
    for log_file in log_files:
        print(f"  - Scanning {os.path.basename(log_file)}...", end='')
        file_vol = 0.0
        file_trades = 0
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'FILLED' in line:
                        # Extract Price
                        price_match = re.search(r'Price:\s*(\d+\.?\d*)', line)
                        # Extract Size
                        size_match = re.search(r'Size:\s*(\d+\.?\d*)', line)
                        
                        if price_match and size_match:
                            price = float(price_match.group(1))
                            size = float(size_match.group(1))
                            
                            trade_val = price * size
                            file_vol += trade_val
                            file_trades += 1
                            
            print(f" -> ${file_vol:,.2f} ({file_trades} trades)")
            total_volume += file_vol
            total_trades += total_trades
            
        except Exception as e:
            print(f" Error: {e}")
            
    print("\n" + "="*50)
    print("📊 GRAND TOTAL VOLUME REPORT")
    print("="*50)
    print(f"💰 Total Volume:   ${total_volume:,.2f}")
    print(f"🔄 Total Trades:   {total_trades}")
    
    target = 1000000 # $1M
    progress = (total_volume / target) * 100
    print(f"🎯 Target ($1M):    {progress:.2f}% Complete")
    print("="*50)

if __name__ == "__main__":
    audit_total_volume()
