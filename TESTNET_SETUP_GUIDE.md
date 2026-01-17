# 🎁 BYBIT TESTNET - Get FREE Test Funds Guide

## ✅ STEP-BY-STEP GUIDE

### 1️⃣ Register Bybit Testnet Account

**Go to:** https://testnet.bybit.com

**Register:**

- Email & password (bisa sama dengan mainnet atau beda)
- Verify email
- Login

**✅ NO KYC REQUIRED!**

---

### 2️⃣ Get FREE Test Funds

**After login:**

1. **Navigate to Assets**

   ```
   Top right → Click profile icon → Assets
   Or: https://testnet.bybit.com/user/assets/home
   ```

2. **Request Test Funds**
   - Click on "Get Test Funds" button
   - Or click "Deposit" → Select coin (USDT)
   - Look for "Get Test Funds" option

3. **Receive Instant Funds!**
   - Usually get: **10,000 USDT** instantly!
   - FREE, unlimited requests
   - Can request more if needed

---

### 3️⃣ Create Testnet API Keys

**Go to API Management:**

```
Profile → Account & Security → API Management
Or: https://testnet.bybit.com/app/user/api-management
```

**Create New Key:**

1. Click "Create New Key"
2. Name: "Trading Bot Test"
3. **Permissions** (IMPORTANT!):
   - ✅ **Contract - Account** (Read)
   - ✅ **Contract - Position** (Read/Write)
   - ✅ **Contract - Trading** (Read/Write)
   - ❌ **Wallet** (NO!)
   - ❌ **Withdraw** (NO!)
   - ✅ **Spot** (Optional, Read if needed)

4. **IP Whitelist:** Leave empty or select "No IP restriction"
5. Click Submit
6. **SAVE API Key & Secret!** (won't show again)

---

### 4️⃣ Update Bot Configuration

**A. Update .env on VPS:**

```bash
# In VPS code-server terminal:
cd ~/workspace/simple-bybit-spread-capture

# Create/update .env
nano .env
```

**Paste testnet keys:**

```
BYBIT_API_KEY=your_testnet_api_key_here
BYBIT_API_SECRET=your_testnet_secret_here
```

**Save:** Ctrl+X, Y, Enter

**B. Config already updated to testnet!** ✅

---

### 5️⃣ Verify Setup

**Test API:**

```bash
cd ~/workspace/simple-bybit-spread-capture
source venv/bin/activate
python test_api_key.py
```

**Expected:**

```
✅ Public API works!
✅ Authentication SUCCESS!
✅ Futures API works!
```

---

### 6️⃣ Train ML Model & Run Bot

```bash
# Train model
python train_xgboost.py

# Run bot
python main.py
```

---

## 🎯 TESTNET vs MAINNET COMPARISON

| Feature              | Testnet           | Mainnet Demo      |
| -------------------- | ----------------- | ----------------- |
| **Cost**             | FREE              | Restricted        |
| **Funds**            | 10,000 USDT free! | 3,415 USD limited |
| **API Restrictions** | NONE              | Account at risk   |
| **KYC**              | NOT required      | May require       |
| **Perfect for**      | Testing bot! ✅   | Real trading prep |
| **URL**              | testnet.bybit.com | bybit.com         |

---

## 💡 TESTNET TIPS

**1. Unlimited Test Funds:**

- Request more anytime
- Can reset account if needed
- No real money risk!

**2. Same Features as Mainnet:**

- Real-time prices
- Same order types
- Same leverage options
- Futures contracts

**3. Perfect for Bot Testing:**

- Test aggressive settings
- High leverage experiments
- No fear of losses
- Learn without risk

**4. If Balance Low:**

```
Assets → Get Test Funds → Instant 10,000 USDT!
```

---

## 🚀 QUICK START COMMANDS

```bash
# After getting testnet API keys:

# 1. Update .env on VPS
cd ~/workspace/simple-bybit-spread-capture
cat > .env << 'EOF'
BYBIT_API_KEY=paste_your_testnet_key
BYBIT_API_SECRET=paste_your_testnet_secret
EOF

# 2. Reload environment
deactivate
source venv/bin/activate

# 3. Train model
python train_xgboost.py

# 4. Run bot
python main.py

# 5. Monitor for 5-10 minutes
# Press Ctrl+C to stop
```

---

## ✅ FINAL CHECKLIST

Before running bot:

- [ ] Registered at testnet.bybit.com
- [ ] Got FREE 10,000 USDT test funds
- [ ] Created testnet API keys with correct permissions
- [ ] Updated .env on VPS with testnet keys
- [ ] Config set to TESTNET = True ✅
- [ ] Virtual environment reloaded
- [ ] Ready to test!

---

## 🎁 BONUS: Reset Testnet Account

**If you mess up:**

- Just request new test funds
- Or create new testnet account
- 100% FREE, zero consequences!

**This is why testnet is PERFECT for learning!** 🚀

---

**GO TO:** https://testnet.bybit.com
**GET:** Free 10,000 USDT test funds!
**START:** Testing your bot risk-free!
