# 🔧 API KEY STILL FAILING - VPS Environment Issue

## ❌ PROBLEM: .env File Not Syncing to VPS!

**Root Cause**: File di Windows lokal ≠ File di VPS container!

---

## ✅ QUICK FIX

### Step 1: Verify .env on VPS

```bash
# In VPS terminal (code-server)
cd ~/workspace/simple-bybit-spread-capture

# Check if .env exists
ls -la .env

# View content
cat .env
```

**Expected:**

```
BYBIT_API_KEY=B6K9tM27Ltj2AX0aCd
BYBIT_API_SECRET=9VH5VgSVi3oNn0nprGY32TzvvrpZAA1hOzOH
```

**If NOT exactly this**: .env di VPS berbeda dari Windows!

### Step 2: Manually Create/Update .env on VPS

```bash
# Create new .env di VPS
nano ~/workspace/simple-bybit-spread-capture/.env
```

**Paste EXACTLY:**

```
BYBIT_API_KEY=B6K9tM27Ltj2AX0aCd
BYBIT_API_SECRET=9VH5VgSVi3oNn0nprGY32TzvvrpZAA1hOzOH
```

**Save**: `Ctrl+X`, `Y`, `Enter`

### Step 3: Verify File Saved

```bash
# Check content
cat ~/workspace/simple-bybit-spread-capture/.env

# Should match exactly what you pasted
```

### Step 4: Restart Python Environment

```bash
# Deactivate venv (important!)
deactivate

# Reactivate to reload environment variables
source venv/bin/activate

# Verify environment picked up
python3 -c "import os; print('API Key loaded:', os.getenv('BYBIT_API_KEY')[:10] + '...' if os.getenv('BYBIT_API_KEY') else 'NOT LOADED')"
```

**Expected Output:**

```
API Key loaded: B6K9tM27Lt...
```

### Step 5: Try Training Again

```bash
cd ~/workspace/simple-bybit-spread-capture
python train_xgboost.py
```

---

## 🔍 IF STILL FAILS

### Check 1: API Key Permissions

```bash
# Login to bybit.com
# Go to: Account → API Management
# Find your "Demo Tes" key
# Check permissions:
# ✅ Contract - Position
# ✅ Contract - Trading
# ✅ Contract - Account
```

### Check 2: IP Whitelist

```bash
# In Bybit API settings
# Check if IP whitelist is enabled
# If YES: Need to add VPS IP or disable it
```

### Check 3: Test API Key Manually

```bash
# Quick Python test
python3 << 'EOF'
import os
from dotenv import load_dotenv
import ccxt

# Load .env
load_dotenv()

api_key = os.getenv('BYBIT_API_KEY')
api_secret = os.getenv('BYBIT_API_SECRET')

print(f"API Key: {api_key[:10]}... (length: {len(api_key)})")
print(f"Secret: {api_secret[:10]}... (length: {len(api_secret)})")

# Test connection
exchange = ccxt.bybit({
    'apiKey': api_key,
    'secret': api_secret,
})

try:
    balance = exchange.fetch_balance()
    print("✅ API Key works! Balance fetched successfully")
except Exception as e:
    print(f"❌ API Key failed: {e}")
EOF
```

---

## 💡 ALTERNATIVE: Use Environment Variables Directly

**If .env keeps failing:**

```bash
# Set environment variables directly
export BYBIT_API_KEY="B6K9tM27Ltj2AX0aCd"
export BYBIT_API_SECRET="9VH5VgSVi3oNn0nprGY32TzvvrpZAA1hOzOH"

# Verify
echo $BYBIT_API_KEY

# Run training
python train_xgboost.py
```

---

## 📋 COMPLETE TROUBLESHOOTING SEQUENCE

```bash
# 1. Navigate to project
cd ~/workspace/simple-bybit-spread-capture

# 2. Create .env
cat > .env << 'EOF'
BYBIT_API_KEY=B6K9tM27Ltj2AX0aCd
BYBIT_API_SECRET=9VH5VgSVi3oNn0nprGY32TzvvrpZAA1hOzOH
EOF

# 3. Verify
cat .env

# 4. Restart venv
deactivate
source venv/bin/activate

# 5. Test environment
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API:', os.getenv('BYBIT_API_KEY')[:15])"

# 6. Try training
python train_xgboost.py
```

---

## ⚠️ IMPORTANT NOTE

**Windows files ≠ VPS files!**

- Editing .env di Windows TIDAK otomatis update di VPS
- VPS is Docker container dengan filesystem terpisah
- **MUST manually create/update .env di VPS terminal!**

---

## 🎯 MOST LIKELY ISSUE

**99% sure**: .env file di VPS container masih kosong atau belum ada!

**Solution**: Manually create di VPS seperti step 2 di atas!
