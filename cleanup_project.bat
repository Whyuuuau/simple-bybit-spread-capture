@echo off
echo ========================================================
echo 🧹 STARTING PROJECT CLEANUP (Removing Bybit Junk)
echo ========================================================

:: Documentation & Fixes
del /Q BYBIT_DEMO_QUICKSTART.md
del /Q CODE_SERVER_PYTHON_FIX.md
del /Q DEMO_DOMAIN_FIX.md
del /Q FIX_API_KEY_ERROR.md
del /Q VPS_ENV_SYNC_FIX.md
del /Q VPS_PYTHON_FIX.md
del /Q SETUP_API_KEYS.txt
del /Q README.md
del /Q README_VPS.md

:: Obsolete Scripts
del /Q check_ccxt.py
del /Q test_api_key.py
del /Q fix_training.patch
del /Q cleanup_unused_files.bat

echo.
echo ✅ CLEANUP COMPLETE!
echo The project is now focused on Bitunix Mainnet.
echo ========================================================
pause
