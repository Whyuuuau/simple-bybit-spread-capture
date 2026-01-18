import os
import glob
import re

def audit_debug(log_dir='logs'):
    print(f"📂 DEBUG AUDIT in '{log_dir}'...")
    log_files = glob.glob(os.path.join(log_dir, 'trades_*.log'))
    
    if not log_files:
        print("❌ No log files found.")
        return

    for log_file in log_files:
        print(f"\n--- Reading {os.path.basename(log_file)} (First 20 lines) ---")
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if not lines:
                    print("(File is Empty)")
                for i, line in enumerate(lines[:20]):
                    print(f"{i+1}: {line.strip()}")
                    
                # Check for "FILLED" counts
                filled_count = sum(1 for l in lines if 'FILLED' in l)
                print(f"\n[Stats] 'FILLED' keyword found: {filled_count} times")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    audit_debug()
