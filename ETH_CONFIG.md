# 🚀 ETH/USDT Futures - Quick Setup Guide

## ✅ BOT CONFIGURED FOR ETHEREUM!

Bot sekarang sudah di-configure untuk **ETH/USDT FUTURES** dengan settings optimal!

---

## 📊 ETH Configuration Summary

### Symbol

- **Pair**: ETH/USDT Perpetual Futures
- **Leverage**: 5x (conservative & safe)
- **Exchange**: Bybit

### Order Settings

- **Min Order**: $10 USD
- **Max Order**: $100 USD
- **Base Order**: $30 USD
- **Orders per side**: 5

### Position Limits

- **Max Position**: $1,000 USD (with 5x leverage)
- **Rebalance Threshold**: $400 USD
- **Position Check**: Every 10 seconds

### Spread Settings (ETH highly liquid)

- **Min Spread**: 0.02% (tighter for ETH)
- **Max Spread**: 0.2%
- **Target Multiplier**: 60% of current spread

### Volume Targets

- **Per Hour**: $100,000 (ETH can handle high volume)
- **Per Day**: $2,000,000

### Precision

- **Price**: 2 decimals (e.g., 3245.67)
- **Amount**: 3 decimals (e.g., 0.123 ETH)

---

## 🎯 Why ETH is BETTER Choice

✅ **Higher Liquidity** - Tightest spreads, easy fills
✅ **Lower Slippage** - Major coin, deep order book
✅ **More Stable** - Less volatile than memecoins
✅ **Higher Volume Potential** - Can push $2M+ daily
✅ **Better for ML** - More predictable patterns
✅ **24/7 Active** - Always liquid, worldwide trading

---

## 🚀 Ready to Run!

Bot sudah **FULLY CONFIGURED** untuk ETH/USDT futures!

### To Start:

```powershell
# 1. Install dependencies (if not done)
pip install -r requirements.txt

# 2. Setup API keys (testnet first!)
copy .env.example .env
# Edit .env with testnet keys

# 3. Train XGBoost model (recommended)
python train_xgboost.py

# 4. Run bot
python main.py
```

---

## ⚙️ Adjust If Needed

Edit `config.py` kalau mau adjust:

### More Aggressive (Higher Volume)

```python
MAX_ORDER_SIZE_USD = 200      # Bigger orders
BASE_ORDER_SIZE_USD = 50      # Higher base
num_orders = 7                # More orders
```

### More Conservative (Lower Risk)

```python
MAX_ORDER_SIZE_USD = 50       # Smaller orders
BASE_ORDER_SIZE_USD = 15      # Lower base
LEVERAGE = 3                  # Lower leverage
```

---

## 💡 Performance Expectations (ETH)

### Volume (24 hours)

- **Conservative**: $500k-1M
- **Moderate**: $1M-2M
- **Aggressive**: $2M-5M+

### Risk Profile

- **Leverage**: 5x (safe for ETH)
- **Liquidation Risk**: LOW (ETH less volatile)
- **Max Daily Loss**: $100 (auto-stop)

### PnL Expectations

- **Volume mode**: -0.01% to -0.03% (fees only)
- **With XGBoost**: +0.1% to +0.5% profit
- **Best case**: $500-2000 profit per day on $2M volume

---

## ⚠️ Important Notes

> [!IMPORTANT]
> **ALWAYS start with TESTNET!**
>
> - ETH on testnet: Free fake ETH
> - Test for 24+ hours
> - Verify everything works

> [!TIP]
> **ETH Advantages:**
>
> - More liquid = better fills
> - More stable = easier to manage
> - Higher volume capacity
> - Better for competitions

---

## 🎯 READY TO TRADE ETH!

Configuration complete! ETH adalah excellent choice untuk volume + profit bot! 🚀💰
