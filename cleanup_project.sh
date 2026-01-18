#!/bin/bash
echo "========================================================"
echo "🧹 STARTING PROJECT CLEANUP (Removing Bybit Junk)"
echo "========================================================"

# Documentation & Fixes
rm -f BYBIT_DEMO_QUICKSTART.md
rm -f CODE_SERVER_PYTHON_FIX.md
rm -f DEMO_DOMAIN_FIX.md
rm -f FIX_API_KEY_ERROR.md
rm -f VPS_ENV_SYNC_FIX.md
rm -f VPS_PYTHON_FIX.md
rm -f SETUP_API_KEYS.txt
rm -f README.md
rm -f README_VPS.md

# Obsolete Scripts
rm -f check_ccxt.py
rm -f test_api_key.py
rm -f fix_training.patch
rm -f cleanup_unused_files.bat

echo ""
echo "✅ CLEANUP COMPLETE!"
echo "The project is now focused on Bitunix Mainnet."
echo "========================================================"
