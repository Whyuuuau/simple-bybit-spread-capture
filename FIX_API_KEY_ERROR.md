# 🔑 API KEY ERROR - Quick Fix Guide

## ❌ ERROR: "API key is invalid"

**Problem**: .env file di VPS tidak memiliki API keys atau salah format!

---

## ✅ SOLUTION: Setup .env File di VPS

### Step 1: Check if .env exists

```bash
cd ~/workspace/simple-bybit-spread-capture
ls -la | grep .env
```

**If NOT found**: File .env tidak ada!

### Step 2: Create .env file

```bash
# Create .env file
nano .env
```

### Step 3: Paste your API keys

**IMPORTANT**: Paste EXACTLY dari Bybit Testnet!

```env
BYBIT_API_KEY=B4b9W27Jz1qAOoG4...your_actual_testnet_key
BYBIT_API_SECRET=••••••...your_actual_testnet_secret
```

**Save**: `Ctrl+X`, then `Y`, then `Enter`

### Step 4: Verify .env file

```bash
# Check file exists
ls -la .env

# Check content (ke-mask secret!)
cat .env
```

**Should show:**

```
BYBIT_API_KEY=B4b9...
BYBIT_API_SECRET=••••...
```

---

## 🔍 TROUBLESHOOTING

### Issue 1: .env exists but still fails

**Fix**: Check for spaces or typos

```bash
# View exact content
cat .env

# Make sure NO spaces around =
# CORRECT:
BYBIT_API_KEY=your_key

# WRONG:
BYBIT_API_KEY = your_key  # SPACES!
BYBIT_API_KEY= your_key   # SPACE AFTER!
```

### Issue 2: Wrong API keys

**Verify**:

1. Login to https://testnet.bybit.com
2. Go to Account → API Management
3. Copy TESTNET keys (not mainnet!)
4. Keys should start with specific characters

### Issue 3: File permissions

```bash
# Make sure .env is readable
chmod 644 .env

# Verify
ls -la .env
```

---

## 🚀 AFTER FIXING .env

```bash
# Deactivate and reactivate venv (reload environment)
deactivate
source venv/bin/activate

# Try training again
python train_xgboost.py
```

---

## 📋 COMPLETE .env TEMPLATE

```env
# Bybit Testnet API Keys
BYBIT_API_KEY=paste_your_testnet_api_key_here
BYBIT_API_SECRET=paste_your_testnet_secret_here

# NOTE:
# - NO quotes needed
# - NO spaces around =
# - Get keys from: https://testnet.bybit.com → Account → API Management
```

---

## ✅ VERIFICATION CHECKLIST

Before running again:

- [ ] .env file exists in project folder
- [ ] API key pasted correctly (no spaces)
- [ ] API secret pasted correctly (no spaces)
- [ ] Using TESTNET keys (not mainnet!)
- [ ] File saved properly
- [ ] Virtual environment reactivated

---

## 🎯 QUICK FIX COMMANDS

```bash
# 1. Navigate to project
cd ~/workspace/simple-bybit-spread-capture

# 2. Create .env
nano .env

# 3. Paste content:
# BYBIT_API_KEY=your_testnet_key
# BYBIT_API_SECRET=your_testnet_secret
# Save: Ctrl+X, Y, Enter

# 4. Verify
cat .env

# 5. Reload venv
deactivate
source venv/bin/activate

# 6. Try again
python train_xgboost.py
```

---

**IF STILL FAILS**: Double-check keys di Bybit Testnet website!
