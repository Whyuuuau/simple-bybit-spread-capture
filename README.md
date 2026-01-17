# 🚀 Bybit Demo Mainnet Trading Bot

Ultimate trading bot untuk **testing trading strategies** di **Bybit Demo Mainnet** dengan **real market prices** dan **virtual balance**!

## ✨ Features

### 🎯 Core Features

- ✅ **DEMO MAINNET trading** dengan virtual balance
- ✅ **Real market prices** dari Bybit mainnet
- ✅ **FUTURES trading** dengan leverage
- ✅ **ML-powered profit signals** (XGBoost/LSTM)
- ✅ **Auto risk management** & position rebalancing
- ✅ **Liquidation protection** monitoring
- ✅ **Smart order management**
- ✅ **Comprehensive logging**

### 🛡️ Safety Features

- ✅ Daily/total loss limits dengan auto-stop
- ✅ Position size limits dengan leverage consideration
- ✅ Liquidation distance monitoring
- ✅ PnL tracking
- ✅ Emergency shutdown system
- ✅ **ZERO REAL MONEY RISK** - Virtual balance only!

### 🤖 ML Features

- ✅ XGBoost/LSTM model dengan 19+ technical indicators
- ✅ Binary classification (profitable vs tidak)
- ✅ Adaptive order sizing based on confidence
- ✅ Model persistence (train once, use forever)

---

## 📦 Installation

### 1. Install Python

Download Python 3.11 (64-bit) dari [python.org](https://www.python.org/downloads/)

- ❌ Jangan gunakan Python 3.12 (TensorFlow issues)
- ✅ Gunakan Python 3.9, 3.10, atau 3.11

### 2. Clone/Download Project

```powershell
cd e:\\TRADE\\simple-bybit-spread-capture
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

**Note:** TA-Lib mungkin fail install di Windows. Jika gagal, bot akan fallback ke pandas implementation.

### 4. Setup Demo API Keys

**Get Demo API Keys:**

1. Create account di https://demo.bybit.com
2. Login dan pergi ke: https://demo.bybit.com/app/user/api-management
3. Create API key dengan permissions:
   - ✅ **Read** - Required
   - ✅ **Trade (Spot & Derivatives)** - Required
   - ❌ **Withdraw** - NEVER enable this!

4. Copy `.env.example` ke `.env`:

   ```powershell
   copy .env.example .env
   ```

5. Edit `.env` dan paste API keys:
   ```
   BYBIT_API_KEY=your_demo_api_key_here
   BYBIT_API_SECRET=your_demo_api_secret_here
   ```

**Security Tips:**

- ✅ Demo keys are safe to use (virtual money only)
- ✅ Set IP whitelist for extra security
- ❌ NEVER enable withdrawal permission
- ✅ Use separate keys untuk different bots

---

## 🎓 Training ML Model (Optional tapi Recommended)

Untuk enable profit mode, train model dulu:

```powershell
python train_xgboost.py
```

**Training time:**

- CPU only: 30-60 minutes
- With GPU: 5-10 minutes

**Training output:**

- Model saved di: `models/xgboost_model.pkl`
- Scaler saved di: `models/scaler.pkl`
- Features saved di: `models/feature_cols.pkl`

**Jika skip training:**

- Bot akan run tanpa ML optimization
- Tetap bisa generate volume, tapi kurang optimal

---

## 🚀 Running the Bot

### Demo Mainnet (DEFAULT)

1. Pastikan sudah setup demo API keys di `.env`

2. Run bot:

   ```powershell
   python main.py
   ```

3. Monitor logs:
   - Console: Real-time updates
   - `logs/trading_bot.log`: Full log
   - `logs/trades_YYYYMMDD.log`: Trade-only log
   - `logs/errors.log`: Errors only

### Get More Demo Money

Jika demo balance habis, apply for more:

```powershell
# Run this to add $100,000 USDT to demo account
python -c "from config import apply_demo_money; import asyncio; asyncio.run(apply_demo_money('USDT', '100000'))"
```

**Available coins dan max amounts:**

- USDT: 100,000
- USDC: 100,000
- ETH: 200
- BTC: 15

---

## ⚙️ Configuration

Edit `config.py` untuk customize settings:

### Leverage & Position

```python
LEVERAGE = 5                          # Leverage (1-50)
MAX_POSITION_SIZE_USD = 500          # Max position value
POSITION_REBALANCE_THRESHOLD_USD = 200  # Auto-rebalance trigger
```

### Volume Targets

```python
TARGET_VOLUME_PER_HOUR = 50000       # $50k/hour target
TARGET_VOLUME_PER_DAY = 1000000      # $1M/day target
```

### Order Settings

```python
num_orders = 5                        # Orders per side
MIN_ORDER_SIZE_USD = 5               # Min per order
MAX_ORDER_SIZE_USD = 50              # Max per order
BASE_ORDER_SIZE_USD = 20             # Base size
```

### Safety Limits

```python
MAX_DAILY_LOSS_USD = -100            # Stop if lose $100/day
MAX_TOTAL_LOSS_USD = -300            # Emergency stop
STOP_LOSS_PCT = 2.0                  # 2% stop loss
```

### Spread Settings

```python
MIN_SPREAD_PCT = 0.05                # 0.05% minimum
MAX_SPREAD_PCT = 0.3                 # 0.3% maximum
```

---

## 📊 Monitoring

### Real-time Stats (logged setiap 60 detik)

```
📊 BOT STATISTICS
Runtime:        2.50 hours
Total Volume:   $125,450.25
Volume/Hour:    $50,180.10
Total Trades:   234
Net PnL:        $125.50
Position:       $45.20 LONG
ML Signal:      BULLISH (75%)
```

### Key Metrics to Watch

- ✅ **Total Volume**: Should steadily increase
- ✅ **Net PnL**: Should be positive (or small negative from fees)
- ✅ **Position**: Should stay near $0 (±$100)
- ✅ **Liquidation Distance**: Should stay >20%
- ⚠️ **Rebalances**: Too many = problem

### Log Files

- `logs/trading_bot.log` - Full detailed log
- `logs/trades_YYYYMMDD.log` - All trades
- `logs/errors.log` - Errors only

---

## 🛑 Stopping the Bot

### Graceful Stop

Press `Ctrl+C` in terminal:

- Bot will cancel all orders
- Close all positions
- Log final statistics
- Safe shutdown

### Emergency Stop

If bot frozen, force close:

- Close terminal window
- Manually cancel orders di Bybit web interface
- Check positions di exchange

---

## 🔧 Troubleshooting

### "Failed to set leverage"

- Check API keys permissions
- Enable "Trade" permission di API settings
- Verify symbol exists di exchange

### "No ML model found"

- Run `python train_model.py` first
- Or set `USE_ML_MODEL = False` di config.py

### "Insufficient margin"

- Reduce MAX_ORDER_SIZE_USD
- Reduce num_orders
- Add more capital to account

### "Rate limit exceeded"

- Increase ORDER_REFRESH_INTERVAL
- Reduce num_orders

### "Position rebalancing too often"

- Increase POSITION_REBALANCE_THRESHOLD_USD
- Reduce order sizes
- Check for bugs in order logic

---

## 📈 Performance Expectations

### Volume (dengan optimal settings)

| Timeframe | Conservative | Moderate  | Aggressive  |
| --------- | ------------ | --------- | ----------- |
| Hourly    | $20k-50k     | $50k-100k | $100k-200k+ |
| Daily     | $250k-500k   | $500k-1M  | $1M-3M+     |

### PnL

- **Without ML**: -0.01% to -0.05% of volume (fees)
- **With ML (good model)**: +0.1% to +0.5% of volume
- **With maker rebates**: Could be net positive

### Risk Profile

- **Leverage**: 5x (conservative, adjustable)
- **Liquidation Risk**: LOW (auto-monitor & rebalance)
- **Max Drawdown**: Capped by safety limits

---

## ⚠️ Risks & Disclaimers

> [!CAUTION]
> **Trading with leverage is RISKY!**
>
> - You can lose more than your initial capital
> - 5x leverage = 5x faster liquidation
> - Market volatility can cause rapid losses
> - Always use testnet first
> - Only trade with money you can afford to lose

> [!WARNING]
> **This bot is NOT financial advice!**
>
> - Use at your own risk
> - Past performance ≠ future results
> - Monitor the bot constantly
> - Have emergency stop plan
> - Start with small capital

> [!IMPORTANT]
> **Security is YOUR responsibility!**
>
> - Protect your API keys
> - Use IP whitelisting
> - Disable withdrawal permission
> - Use 2FA on exchange account
> - Never share your .env file

---

## 🆘 Support & Help

### Issues?

1. Check logs in `logs/` directory
2. Review config settings
3. Test in testnet first
4. Start with small capital

### Common Solutions

- **No fills**: Widen spread, reduce order size
- **Too many rebalances**: Adjust thresholds
- **Losses**: Check spread vs fees, adjust parameters
- **Crashes**: Check logs/errors.log, fix issues

---

## 📁 Project Structure

```
simple-bybit-spread-capture/
├── main.py                      # Main bot (START HERE)
├── train_model.py              # ML model training
├── config.py                   # Configuration
├── trading.py                  # Trading functions
├── futures_position_manager.py # Position management
├── order_book_analyzer.py      # Order book analysis
├── data_handler.py             # Data & features
├── model.py                    # ML model
├── utils.py                    # Utility functions
├── logger_config.py            # Logging setup
├── requirements.txt            # Dependencies
├── .env                        # API keys (YOU CREATE THIS)
├── .env.example                # Template
├── logs/                       # Log files (auto-created)
└── models/                     # ML models (auto-created)
```

---

## 🚀 Quick Start Guide

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup API keys
copy .env.example .env
# Edit .env with your testnet keys

# 3. (Optional) Train ML model
python train_model.py

# 4. Run bot in testnet
# Edit config.py: TESTNET = True
python main.py

# 5. Monitor & adjust
# Check logs/, adjust config as needed

# 6. When ready for production
# Edit config.py: TESTNET = False
# Use small capital, monitor closely
python main.py
```

---

## 📄 License

This project is provided as-is for educational purposes.
Use at your own risk.

---

## 💪 Ready to Trade!

Bot siap digunakan! Remember:

1. ✅ Start dengan testnet
2. ✅ Test thoroughly (24+ hours)
3. ✅ Start production dengan capital kecil
4. ✅ Monitor closely
5. ✅ Scale gradually

**Happy Trading! 🚀💰**
