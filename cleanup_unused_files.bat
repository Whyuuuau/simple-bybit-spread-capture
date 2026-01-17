@echo off
REM ============================================================================
REM Cleanup Script - Remove Unused Files (Bybit Demo Mainnet Only)
REM ============================================================================

echo.
echo ========================================
echo CLEANUP: Removing Unused Files
echo ========================================
echo.

REM Paper Trading files (should be already deleted)
if exist "paper_trading.py" (
    del /F "paper_trading.py"
    echo [DELETED] paper_trading.py
) else (
    echo [SKIP] paper_trading.py - already deleted
)

if exist "paper_position_manager.py" (
    del /F "paper_position_manager.py"
    echo [DELETED] paper_position_manager.py
) else (
    echo [SKIP] paper_position_manager.py - already deleted
)

REM Old documentation files (testnet/paper trading related)
if exist "TESTNET_SETUP_GUIDE.md" (
    del /F "TESTNET_SETUP_GUIDE.md"
    echo [DELETED] TESTNET_SETUP_GUIDE.md
)

if exist "HOW_TO_MONITOR_PAPER_TRADING.md" (
    del /F "HOW_TO_MONITOR_PAPER_TRADING.md"
    echo [DELETED] HOW_TO_MONITOR_PAPER_TRADING.md
)

if exist "TURBO_MODE_1M.md" (
    del /F "TURBO_MODE_1M.md"
    echo [DELETED] TURBO_MODE_1M.md
)

if exist "CURRENT_SETUP_STATUS.md" (
    del /F "CURRENT_SETUP_STATUS.md"
    echo [DELETED] CURRENT_SETUP_STATUS.md
)

REM Bitunix related files (not using Bitunix)
if exist "BITUNIX_100_CONFIG.md" (
    del /F "BITUNIX_100_CONFIG.md"
    echo [DELETED] BITUNIX_100_CONFIG.md
)

if exist "BITUNIX_DEMO_TEST.md" (
    del /F "BITUNIX_DEMO_TEST.md"
    echo [DELETED] BITUNIX_DEMO_TEST.md
)

if exist "BITUNIX_FEES_ANALYSIS.md" (
    del /F "BITUNIX_FEES_ANALYSIS.md"
    echo [DELETED] BITUNIX_FEES_ANALYSIS.md
)

REM Old configuration files
if exist "ETH_CONFIG.md" (
    del /F "ETH_CONFIG.md"
    echo [DELETED] ETH_CONFIG.md
)

if exist "config_presets.py" (
    del /F "config_presets.py"
    echo [DELETED] config_presets.py
)

REM Old position manager (using futures_position_manager.py only)
if exist "position_manager.py" (
    del /F "position_manager.py"
    echo [DELETED] position_manager.py
)

REM Old LSTM model training (using XGBoost now)
if exist "train_model.py" (
    del /F "train_model.py"
    echo [DELETED] train_model.py
)

if exist "model.py" (
    del /F "model.py"
    echo [DELETED] model.py - using model_xgboost.py
)

REM Optional: Remove old LSTM models if exist
if exist "models\lstm_model.h5" (
    del /F "models\lstm_model.h5"
    echo [DELETED] models\lstm_model.h5
)

echo.
echo ========================================
echo CLEANUP COMPLETE!
echo ========================================
echo.
echo Remaining important files:
echo - config.py (Demo Mainnet config)
echo - main.py (Bot logic)
echo - trading.py (Trading functions)
echo - futures_position_manager.py (Position management)
echo - data_handler.py (Data fetching)
echo - model_xgboost.py (ML model)
echo - train_xgboost.py (ML training)
echo - README.md (Documentation)
echo - DEMO_QUICKSTART.md (Quick start guide)
echo.
echo Project is now DEMO MAINNET ONLY!
echo.
pause
