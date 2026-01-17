# 🔧 CODE-SERVER PYTHON FIX - Docker Container Issue

## ❌ PROBLEM: Python not found in code-server container

**Root Cause**: Code-server runs in Docker container - separate from VPS host!

**What you see:**

- ✅ Host VPS: Python works
- ❌ Code-server terminal: "Unable to locate package python3"

**Solution**: Install Python INSIDE the code-server container

---

## ✅ SOLUTION 1: Install Python in Container (Quick)

### In code-server terminal:

```bash
# Update apt sources
sudo apt update

# Install Python3 (whatever version available)
sudo apt install python3 python3-pip python3-venv -y

# Verify
python3 --version
which python3
```

### If python3 already exists but pip doesn't:

```bash
# Just install pip
sudo apt install python3-pip -y

# Verify
pip3 --version
```

---

## ✅ SOLUTION 2: Fix apt-get errors

**If you see "Unable to locate package":**

```bash
# Fix 1: Update package lists
sudo apt-get update
sudo apt-get upgrade -y

# Fix 2: If still fails, check Python is available
apt-cache search python3 | grep python3

# Install whatever is available
sudo apt-get install python3 -y
```

---

## ✅ SOLUTION 3: Use existing Python (if present)

```bash
# Check if python3 already installed
which python3
python3 --version

# If exists, just install pip separately
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py

# Install venv
sudo apt-get install python3-venv -y
```

---

## 🚀 AFTER Python is Installed

```bash
# Navigate to project
cd ~/workspace/simple-bybit-spread-capture

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Train model
python train_xgboost.py

# Run bot
python main.py
```

---

## 🔍 TROUBLESHOOTING

### Error: "E: Unable to locate package"

**Cause**: Container apt sources not configured

**Fix**:

```bash
# Update sources
sudo apt-get update

# If still fails, manually add universe repo
sudo add-apt-repository universe
sudo apt-get update
```

### Error: "python3 is already the newest version"

**Good!** Python already installed. Just need pip:

```bash
sudo apt-get install python3-pip python3-venv -y
```

### Check what's actually installed:

```bash
# List all python packages
dpkg -l | grep python

# Find python executables
which python3
ls -la /usr/bin/python*
```

---

## 💡 RECOMMENDED: Use Host Python (Alternative)

**If code-server Python is problematic, use host VPS directly:**

### Option A: SSH to VPS (outside code-server)

```bash
# From your local machine
ssh user@vps-ip

# Now you're on VPS host (not container)
cd ~/simple-bybit-spread-capture
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train_xgboost.py
python main.py
```

### Option B: Use screen on VPS host

```bash
# SSH to VPS host
ssh user@vps-ip

# Create screen session
screen -S trading-bot

# Setup and run bot
cd ~/simple-bybit-spread-capture
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train_xgboost.py
python main.py

# Detach: Ctrl+A then D
# To return: screen -r trading-bot
```

---

## 🎯 QUICK FIX COMMAND

**Try this in code-server terminal:**

```bash
# All-in-one fix
sudo apt-get update && \
sudo apt-get install -y python3 python3-pip python3-venv && \
python3 --version && \
echo "✅ Python installed successfully!"
```

**If that works, continue:**

```bash
cd ~/workspace/simple-bybit-spread-capture
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📋 SUMMARY

**Problem**: Code-server = Docker container ≠ Host VPS

**Solutions**:

1. ✅ Install Python inside container (`sudo apt update && sudo apt install python3 python3-pip -y`)
2. ✅ Use VPS host directly (SSH outside code-server)
3. ✅ Deploy with screen on host (recommended for 24/7)

**Recommended**: Use **SSH + screen** on host VPS for production bot!

Code-server is good for coding, but for 24/7 trading bot, use host directly! 🚀
