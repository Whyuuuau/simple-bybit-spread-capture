import json
import time
import os
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

print("Initializing Monitor...")
time.sleep(1)

while True:
    try:
        if os.path.exists('dashboard.json'):
            with open('dashboard.json', 'r') as f:
                data = json.load(f)
            
            clear_screen()
            print("\033[92m" + "="*50 + "\033[0m")  # Green line
            print(f" 🚀 BYBIT VOLUME BOT STATUS      \033[93m{data['last_update']}\033[0m")
            print("\033[92m" + "="*50 + "\033[0m")
            
            # Big Stats
            print(f"\n 💰 NET PNL:        \033[96m{data['pnl']}\033[0m")
            print(f" 📈 TOTAL VOLUME:   \033[96m{data['volume']}\033[0m")
            print(f" 🔄 TOTAL TRADES:   \033[93m{data['trades']}\033[0m")
            
            print("\n" + "-"*50)
            
            # Position Info
            pos_color = "\033[91m" if "SHORT" in data['position'] else "\033[92m"
            if "FLAT" in data['position']: pos_color = "\033[90m"
            
            print(f" 📡 POSITION:       {pos_color}{data['position']}\033[0m")
            
            # ML Info
            print(f" 🧠 ML SIGNAL:      {data['ml_signal']}")
            print(f" ⏱️ RUNTIME:        {data['runtime']}")
            
            print("\n" + "="*50)
            print("\033[90m Press Ctrl+C to stop monitor (Bot keeps running)\033[0m")
            
        else:
            print(" Waiting for bot to generate stats...", end='\r')
            
    except json.JSONDecodeError:
        pass # File being written to
    except Exception as e:
        # print(f"Error: {e}")
        pass
        
    time.sleep(1)
