# 🧪 BYBIT TESTNET DEMO - Quick Test Guide

## ✅ SETUP UNTUK BYBIT TESTNET DEMO

**Config sudah diset untuk Bybit Testnet! ✅**

---

## 📋 STEP 1: Daftar Bybit Testnet

### 1.1 Create Account

```
1. Buka: https://testnet.bybit.com
2. Register account (GRATIS!)
3. Login & dapatkan test funds
```

### 1.2 Get API Keys

```
1. Go to: Account → API Management
2. Create New Key
   Name: "Trading Bot Test"
   Permissions:
   - ✅ Contract - Account (Read)
   - ✅ Contract - Position (Read/Write)
   - ✅ Contract - Trading (Read/Write)
   - ❌ Wallet (JANGAN!)
   - ❌ Withdraw (JANGAN!)
3. SAVE API Key & Secret!
```

---

## 📋 STEP 2: Setup .env File

```powershell
# Edit file .env (sudah ada .env.example)
notepad .env
```

**Isi dengan:**

```env
BYBIT_API_KEY=your_testnet_api_key_here
BYBIT_API_SECRET=your_testnet_secret_here
```

**SAVE file!**

---

## 📋 STEP 3: Install Dependencies

```powershell
# Make sure di folder project
cd e:\TRADE\simple-bybit-spread-capture

# Install semua requirements
pip install -r requirements.txt

# Tunggu sampai selesai (1-2 menit)
```

**Verify installation:**

```powershell
python -c "import ccxt; print('CCXT:', ccxt.__version__)"
python -c "import xgboost; print('XGBoost: OK')"
```

---

## 📋 STEP 4: Train ML Model (WAJIB!)

```powershell
# Train XGBoost model
python train_xgboost.py

# Tunggu 2-5 menit
# Progress akan tampil di console
```

**Expected Output:**

```
🚀 STARTING XGBOOST MODEL TRAINING
Fetching historical data for ETH/USDT:USDT...
✅ Fetched 10000 candles
✅ Added features, 9981 rows after cleaning
✅ Data prepared:
   Training samples: 7985
   Test samples: 1996
   Features: 19

Starting XGBoost training...
...
✅ XGBOOST MODEL TRAINING COMPLETE!
Model saved to: models/xgboost_model.json
```

---

## 📋 STEP 5: Verify Config

```powershell
# Quick check config
python -c "from config import *; print(f'Exchange: {EXCHANGE_NAME}'); print(f'Testnet: {TESTNET}'); print(f'Symbol: {symbol}')"
```

**Expected:**

```
Exchange: bybit
Testnet: True
Symbol: ETH/USDT:USDT
```

---

## 🚀 STEP 6: RUN BOT!

```powershell
python main.py
```

### Apa yang Akan Terjadi:

**1. Startup (0-10 detik):**

```
================================================================================
🚀 HYBRID VOLUME + PROFIT BOT INITIALIZED
================================================================================
Symbol: ETH/USDT:USDT
Leverage: 4x
Max Position: $70
ML Model: MANDATORY ✅
Testnet: YES
================================================================================

🔧 Initializing bot...
Setting leverage to 4x...
✅ Leverage set successfully

Loading ML model (REQUIRED)...
🚀 XGBoost model detected!
✅ XGBoost model loaded successfully!
```

**2. Main Loop (setelah 10 detik):**

```
🚀 Bot starting main loop...

[Setiap 3 detik akan place orders]
Orders | Kept: 5 | Cancelled: 3 | Placed: 5

[Setiap 60 detik akan show stats]
================================================================================
📊 BOT STATISTICS
================================================================================
Runtime:        0.02 hours
Total Volume:   $124.50
Volume/Hour:    $6,225.00
Total Trades:   6
Net PnL:        $-0.12
Position:       $3.20 LONG
ML Signal:      BULLISH (68%)
================================================================================
```

---

## 👀 STEP 7: Monitor (5-10 Menit)

### What to Watch:

**✅ GOOD Signs:**

- Orders being placed every 3 seconds
- Some orders getting filled
- Volume increasing
- Position staying < $70
- ML signals changing (BULLISH/BEARISH/NEUTRAL)
- No error messages

**⚠️ WARNING Signs:**

- "Failed to place order" errors
- Position > $70
- Liquidation warnings
- Crashes/exceptions

**❌ BAD Signs:**

- "Insufficient margin"
- "API key invalid"
- Bot crashes repeatedly
- No orders being placed

---

## 🛑 STEP 8: Stop Bot (Ctrl+C)

**Press:** `Ctrl+C`

**Expected:**

```
⚠️ Bot stopped by user (Ctrl+C)
🚨 EMERGENCY SHUTDOWN INITIATED!
Generating session recap...

================================================================================
🎯 SESSION RECAP - BOT RUN SUMMARY
================================================================================

📅 SESSION INFORMATION:
  Start Time:     2026-01-17 01:45:00
  End Time:       2026-01-17 01:55:00
  Duration:       0h 10m
  Exchange:       Bybit
  Symbol:         ETH/USDT:USDT
  Leverage:       4x
  ML Model:       XGBOOST

📊 VOLUME STATISTICS:
  Total Volume:        $          850.25
  Volume/Hour:         $        5,101.50
  Projected/Day:       $      122,436.00
  Total Trades:                     42
  Orders Placed:                   200
  Orders Filled:                    42
  Fill Rate:                     21.00%

💰 PROFIT & LOSS:
  Net PnL:             $           -0.45
  Total Fees Paid:     $            0.51
  Profit/Hour:         $           -2.70

... (more details)

🏁 END OF SESSION RECAP
================================================================================
```

---

## 📊 Check Results

### Console Logs

- Lihat output di terminal
- Cek ada errors atau tidak

### Log Files

```powershell
# Main log
type logs\trading_bot.log | more

# Trade log (today)
dir logs\trades_*.log
type logs\trades_20260117.log | more

# Errors (should be empty!)
type logs\errors.log
```

### Bybit Testnet Website

```
1. Login ke https://testnet.bybit.com
2. Go to: Derivatives → Positions
   - Check positions (should be closed)
3. Go to: Order History
   - See all your bot's orders!
4. Go to: Trade History
   - See filled trades
```

---

## ✅ SUCCESS CRITERIA (10 min test)

### MINIMUM Success:

- [x] Bot started without errors
- [x] At least 5 orders placed
- [x] At least 1 trade filled
- [x] No crashes
- [x] Clean shutdown with recap

### GOOD Performance:

- [x] 20+ trades in 10 minutes
- [x] Volume > $500
- [x] Position stays < $50
- [x] ML signals changing
- [x] No errors in logs

### EXCELLENT:

- [x] 50+ trades
- [x] Volume > $1,000
- [x] Fill rate > 15%
- [x] PnL close to breakeven
- [x] Everything smooth

---

## 🔧 Quick Troubleshooting

### "NO ML MODEL FOUND"

```powershell
python train_xgboost.py
```

### "API Error: Invalid key"

```
1. Check .env file
2. Verify API key copied correctly
3. Make sure using TESTNET keys
```

### "Insufficient Balance"

```
1. Login to testnet.bybit.com
2. Go to Assets
3. Request more test funds
```

### No Fills

```python
# Widen spread in config.py
MIN_SPREAD_PCT = 0.05  # Increase
```

---

## 🎯 EXPECTED RESULTS (10 min)

```
✅ Volume: $500-1,500
✅ Trades: 20-60
✅ PnL: -$0.50 to +$0.20 (normal)
✅ Position: < $20 (should be neutral)
✅ Fill Rate: 10-25%
```

---

## 📝 NEXT STEPS

### If Test Successful:

1. ✅ Run longer (30-60 min)
2. ✅ Monitor stability
3. ✅ Check if settings optimal
4. ✅ Consider switching to Bitunix
5. ✅ Or prepare for mainnet (CAREFULLY!)

### If Issues:

1. 📋 Note errors
2. 🔍 Check logs
3. ⚙️ Adjust config
4. 🔄 Test again

---

## 🚀 QUICK COMMAND SUMMARY

```powershell
# Full test sequence:
cd e:\TRADE\simple-bybit-spread-capture
pip install -r requirements.txt
python train_xgboost.py
python main.py

# Let run 10 minutes
# Press Ctrl+C to stop
# Review session recap!
```

---

## 💡 TIPS

1. **Stay at computer** first 5 minutes
2. **Watch for errors** immediately
3. **Don't panic** if position fluctuates
4. **Check Bybit website** to verify
5. **Save session recap** for reference

**GOOD LUCK!** 🚀

Test funds are FREE - jangan takut experiment! 💪
