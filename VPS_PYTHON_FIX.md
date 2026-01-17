# 🔧 VPS SETUP - Python Installation Fix

## ❌ ERROR: Can't find python3.11

**Problem**: Ubuntu repo doesn't have Python 3.11 by default

**Solution**: Install from deadsnakes PPA or use available Python version

---

## ✅ SOLUTION 1: Install Python 3.10 (Easier, Recommended)

```bash
# Python 3.10 should be available
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# Verify version
python3 --version

# Should show: Python 3.10.x (good enough!)
```

**Then proceed:**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

---

## ✅ SOLUTION 2: Install Python 3.11 (If you want latest)

```bash
# Add deadsnakes PPA
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install pip for 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Verify
python3.11 --version
```

**Then use:**

```bash
# Create venv with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

---

## 🚀 RECOMMENDED: Use Python 3.10 (Simpler)

**Bot works perfectly with Python 3.10!** No need for 3.11.

```bash
# Quick setup
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y

# Clone/upload bot
cd /home/your-username
# Upload your bot files here

# Setup
cd simple-bybit-spread-capture
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Train model
python train_xgboost.py

# Run bot
python main.py
```

---

## ⚠️ IMPORTANT: .gitignore Security Issue

**You removed `.env` from .gitignore!**

**Risk**: API keys could be committed to git and exposed!

**Fix immediately:**

```bash
# Restore .gitignore protection
cat >> .gitignore << EOF
# Sensitive files
.env
*.env
!.env.example
EOF

# If already committed .env, remove from git:
git rm --cached .env
git commit -m "Remove .env from version control"
```

**Never commit .env file!** Contains your API keys!

---

## 📋 Complete VPS Setup Commands

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.10 (available by default)
sudo apt install python3 python3-pip python3-venv git screen -y

# 3. Upload bot files (use SCP or git)
# Example: scp -r local-folder user@vps-ip:~/

# 4. Setup bot
cd ~/simple-bybit-spread-capture
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Create .env file
nano .env
# Paste API keys, save (Ctrl+X, Y, Enter)

# 7. Train ML model
python train_xgboost.py

# 8. Test run
python main.py
# Press Ctrl+C after 2-3 minutes

# 9. Deploy 24/7
screen -S trading-bot
python main.py
# Press Ctrl+A then D to detach
```

---

## ✅ NEXT STEPS

After fixing Python installation:

1. ✅ Restore .gitignore security
2. ✅ Create virtual environment
3. ✅ Install requirements
4. ✅ Upload .env with API keys
5. ✅ Train XGBoost model
6. ✅ Test run bot
7. ✅ Deploy with screen

**Use Python 3.10 - bot works perfectly!** 🚀
