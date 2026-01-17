# 🧪 BITUNIX DEMO TEST RUN GUIDE

## ✅ PRE-TEST VERIFICATION

All critical fixes applied:

- ✅ Syntax error fixed (main.py line 548)
- ✅ orders_filled tracking added
- ✅ .gitignore created
- ✅ All Python files compile successfully

---

## 📋 STEP-BY-STEP TEST GUIDE

### Phase 1: Setup Bitunix Demo Account

#### 1.1 Create Bitunix Account

```
1. Go to Bitunix website
2. Register for demo/testnet account
3. Navigate to API Management
4. Create API Key with permissions:
   - ✅ Read
   - ✅ Trade (Futures)
   - ❌ Withdraw (NEVER enable!)
5. Save API Key & Secret securely
```

#### 1.2 Verify Bitunix API

```python
# Quick test script
import ccxt

exchange = ccxt.bitunix({
    'apiKey': 'YOUR_KEY',
    'secret': 'YOUR_SECRET',
})

# Test connectivity
ticker = exchange.fetch_ticker('ETH/USDT')
print(f"ETH Price: ${ticker['last']}")
print("✅ Bitunix connection successful!")
```

---

### Phase 2: Configure Bot for Demo

#### 2.1 Update .env File

```bash
# Edit .env
BYBIT_API_KEY=your_bitunix_demo_key_here
BYBIT_API_SECRET=your_bitunix_demo_secret_here
```

#### 2.2 Verify config.py Settings

```python
# Should already be set:
EXCHANGE_NAME = 'bitunix'  # ✅
TESTNET = True  # ✅
LEVERAGE = 4  # ✅
symbol = 'ETH/USDT:USDT'  # ✅

# Order sizes (safe for demo):
MIN_ORDER_SIZE_USD = 8
MAX_ORDER_SIZE_USD = 18
BASE_ORDER_SIZE_USD = 12

# Risk limits (safe):
MAX_DAILY_LOSS_USD = -15
MAX_TOTAL_LOSS_USD = -25
```

---

### Phase 3: Install Dependencies

```powershell
# Navigate to project
cd e:\TRADE\simple-bybit-spread-capture

# Install requirements
pip install -r requirements.txt

# Verify installations
python -c "import ccxt; print('CCXT OK')"
python -c "import xgboost; print('XGBoost OK')"
python -c "import pandas; print('Pandas OK')"
```

**Expected Output:**

```
CCXT OK
XGBoost OK
Pandas OK
```

---

### Phase 4: Train ML Model (MANDATORY!)

```powershell
# Train XGBoost model (recommended)
python train_xgboost.py

# This will:
# 1. Fetch historical ETH data
# 2. Add 19+ technical indicators
# 3. Train XGBoost model
# 4. Save to models/ directory
#
# Expected time: 2-5 minutes
# Expected output: "✅ XGBOOST MODEL TRAINING COMPLETE!"
```

**What to Watch For:**

- Data fetching progress
- Training accuracy (should be >55%)
- Model saved successfully
- No errors

---

### Phase 5: DRY RUN TEST (Recommended)

Before live demo test, verify bot starts:

```powershell
# Test bot initialization only
python -c "from main import HybridVolumeBot; import asyncio; bot = HybridVolumeBot(); print('Bot initialized OK!')"
```

**Expected:** No errors, "Bot initialized OK!"

---

### Phase 6: LIVE DEMO TEST RUN

#### 6.1 Start Bot

```powershell
python main.py
```

#### 6.2 What to Expect on Startup

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
   Using SUPERIOR XGBoost model (faster & better accuracy)

Fetching initial market data...
✅ Bot initialization complete!

🚀 Bot starting main loop...
```

#### 6.3 Monitor Initial Activity (First 5 Minutes)

**Watch for:**

- ✅ Orders being placed (should see ~10 orders)
- ✅ ML signal updates ("ML Signal changed: NEUTRAL → BULLISH")
- ✅ Position staying neutral (should be ~$0)
- ✅ No errors in console

**Every 60 seconds you'll see:**

```
================================================================================
📊 BOT STATISTICS
================================================================================
Runtime:        0.05 hours
Total Volume:   $245.50
Volume/Hour:    $4,910.00
Total Trades:   12
Orders Placed:  60
Net PnL:        $-0.15
Total Fees:     $0.18
Rebalances:     0
Position:       $2.50 LONG
ML Signal:      BULLISH (65%)
================================================================================
```

---

### Phase 7: TEST CHECKLIST (Run for 10-15 Minutes)

#### ✅ Functionality Tests

**Orders:**

- [ ] Bot places buy orders
- [ ] Bot places sell orders
- [ ] Orders appear on exchange
- [ ] Some orders get filled
- [ ] New orders replace filled ones

**Position:**

- [ ] Position stays < $70
- [ ] Auto-rebalances if needed
- [ ] No liquidation warnings

**ML Model:**

- [ ] Signals change (BULLISH/BEARISH/NEUTRAL)
- [ ] Confidence scores shown
- [ ] ML stats incrementing

**Logging:**

- [ ] No error messages
- [ ] Stats update every 60s
- [ ] Trade logs generated

---

### Phase 8: GRACEFUL SHUTDOWN TEST

```
Press Ctrl+C to stop bot

Expected sequence:
1. "⚠️ Bot stopped by user (Ctrl+C)"
2. "🚨 EMERGENCY SHUTDOWN INITIATED!"
3. Orders cancelled
4. Positions closed
5. Final statistics shown
6. 🎯 SESSION RECAP displayed

SESSION RECAP should show:
- Duration
- Total volume
- Net PnL
- Final position
- ML statistics
- Recommendations
```

---

### Phase 9: VERIFY RESULTS

#### Check Log Files

```powershell
# View main log
type logs\trading_bot.log

# View trades only
type logs\trades_YYYYMMDD.log

# Check for errors
type logs\errors.log
```

#### Verify on Exchange

```
1. Login to Bitunix web interface
2. Check Order History
   - Should see cancelled orders
3. Check Position
   - Should be closed (0)
4. Check Trade History
   - Should match bot logs
```

---

## 🎯 SUCCESS CRITERIA

### MINIMUM (Bot Working)

- ✅ Bot starts without errors
- ✅ Orders placed successfully
- ✅ At least 1 trade executed
- ✅ No crashes for 10 minutes
- ✅ Clean shutdown with recap

### GOOD (Bot Performing)

- ✅ 10+ trades in 15 minutes
- ✅ Volume > $100 in 15 minutes
- ✅ ML signals changing
- ✅ PnL tracking working
- ✅ Position stays neutral

### EXCELLENT (Ready for Production)

- ✅ 50+ trades in 1 hour
- ✅ Volume > $1,000/hour
- ✅ PnL near breakeven (±$0.50)
- ✅ Fill rate > 5%
- ✅ Zero errors

---

## ⚠️ TROUBLESHOOTING

### Error: "NO ML MODEL FOUND"

```powershell
# Train model first
python train_xgboost.py
```

### Error: "Failed to set leverage"

```
1. Check API keys in .env
2. Verify API has futures permission
3. Check if Bitunix supports 4x leverage
```

### Error: "Insufficient margin"

```python
# Reduce order sizes in config.py
MIN_ORDER_SIZE_USD = 5
MAX_ORDER_SIZE_USD = 10
BASE_ORDER_SIZE_USD = 7
```

### No Orders Filling

```python
# Widen spread in config.py
MIN_SPREAD_PCT = 0.05  # Increase from 0.03
```

### High Position Size

```python
# Reduce in config.py
MAX_POSITION_SIZE_USD = 50  # Down from 70
```

---

## 📊 EXPECTED TEST RESULTS (15 MIN RUN)

### Conservative Estimate

```
Runtime:        15 minutes (0.25 hours)
Total Volume:   $200-500
Volume/Hour:    $800-2,000
Total Trades:   10-30
Net PnL:        -$0.20 to +$0.10 (fees)
Position:       < $20
Rebalances:     0-1
```

### Optimal Performance

```
Runtime:        15 minutes
Total Volume:   $500-1,000
Volume/Hour:    $2,000-4,000
Total Trades:   30-60
Net PnL:        -$0.10 to +$0.20
Position:       < $10
Rebalances:     0
```

---

## 🚀 AFTER SUCCESSFUL TEST

### If Test Passed (All Green):

1. ✅ Run longer test (1-2 hours)
2. ✅ Monitor for stability
3. ✅ Verify PnL tracking accurate
4. ✅ Check log files complete
5. ✅ Review session recap
6. ✅ Consider increasing capital/sizes

### If Test Had Issues:

1. 📋 Note all errors
2. 🔍 Check logs/errors.log
3. ⚙️ Adjust config as needed
4. 🔄 Retest with fixes
5. 📧 Document findings

---

## 💡 TEST RUN COMMANDS SUMMARY

```powershell
# 1. Install
pip install -r requirements.txt

# 2. Train ML (if not done)
python train_xgboost.py

# 3. Verify config
python -c "from config import *; print(f'Exchange: {EXCHANGE_NAME}, Testnet: {TESTNET}')"

# 4. Run bot
python main.py

# 5. Monitor (let run 10-15 min)
# Watch console output

# 6. Stop
# Press Ctrl+C

# 7. Check logs
type logs\trading_bot.log
```

---

## ✅ FINAL CHECKLIST BEFORE STARTING

- [ ] Bitunix demo account created
- [ ] API keys saved in .env
- [ ] Dependencies installed
- [ ] XGBoost model trained
- [ ] config.py verified (exchange='bitunix', testnet=True)
- [ ] No errors when compiling Python files
- [ ] Ready to monitor for 15+ minutes

---

**WHEN READY:**

```powershell
cd e:\TRADE\simple-bybit-spread-capture
python main.py
```

**STAY AT COMPUTER** for first 5 minutes to monitor!

Good luck! 🚀💰
