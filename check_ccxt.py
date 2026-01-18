import ccxt
import sys

print("Checking CCXT support for Bitunix...")
try:
    if 'bitunix' in ccxt.exchanges:
        print("✅ Bitunix IS supported by CCXT!")
        
        # Try to instantiate to check for 'linear' support (features)
        try:
            ex = ccxt.bitunix()
            print("  Instance created successfully.")
            # print(f"  Supported API: {ex.urls}")
        except Exception as e:
            print(f"  Instance creation failed: {e}")
            
    else:
        print("❌ Bitunix is NOT in CCXT exchanges list.")
        print("   Exchanges available: " + ", ".join(ccxt.exchanges[:10]) + "...")
        
except Exception as e:
    print(f"Error checking CCXT: {e}")
