"""
PRESET CONFIGURATIONS FOR DIFFERENT VOLUME TARGETS

Quick presets untuk ganti mode dengan mudah!
"""

# ============================================================================
# PRESET 1: SAFE MODE ($100 capital, low risk)
# ============================================================================
SAFE_MODE = {
    'LEVERAGE': 3,
    'num_orders': 3,
    'ORDER_REFRESH_INTERVAL': 5,
    'MIN_SPREAD_PCT': 0.02,
    'MAX_SPREAD_PCT': 0.15,
    'TARGET_SPREAD_MULTIPLIER': 0.7,
    'MAX_POSITION_SIZE_USD': 50,
    'POSITION_REBALANCE_THRESHOLD_USD': 25,
    'MIN_ORDER_SIZE_USD': 5,
    'MAX_ORDER_SIZE_USD': 15,
    'BASE_ORDER_SIZE_USD': 8,
    'MAX_DAILY_LOSS_USD': -10,
    'MAX_TOTAL_LOSS_USD': -20,
    'TARGET_VOLUME_PER_DAY': 20000,
    # Expected: $20k/day, 50 days to $1M
}

# ============================================================================
# PRESET 2: BALANCED MODE ($100 capital, moderate risk)
# ============================================================================
BALANCED_MODE = {
    'LEVERAGE': 4,
    'num_orders': 4,
    'ORDER_REFRESH_INTERVAL': 3,
    'MIN_SPREAD_PCT': 0.015,
    'MAX_SPREAD_PCT': 0.12,
    'TARGET_SPREAD_MULTIPLIER': 0.75,
    'MAX_POSITION_SIZE_USD': 65,
    'POSITION_REBALANCE_THRESHOLD_USD': 35,
    'MIN_ORDER_SIZE_USD': 6,
    'MAX_ORDER_SIZE_USD': 18,
    'BASE_ORDER_SIZE_USD': 10,
    'MAX_DAILY_LOSS_USD': -12,
    'MAX_TOTAL_LOSS_USD': -25,
    'TARGET_VOLUME_PER_DAY': 50000,
    # Expected: $50k/day, 20 days to $1M
}

# ============================================================================
# PRESET 3: AGGRESSIVE MODE ($100 capital, high risk) ⚡
# ============================================================================
AGGRESSIVE_MODE = {
    'LEVERAGE': 4,
    'num_orders': 5,
    'ORDER_REFRESH_INTERVAL': 3,
    'MIN_SPREAD_PCT': 0.015,
    'MAX_SPREAD_PCT': 0.10,
    'TARGET_SPREAD_MULTIPLIER': 0.8,
    'MAX_POSITION_SIZE_USD': 70,
    'POSITION_REBALANCE_THRESHOLD_USD': 35,
    'MIN_ORDER_SIZE_USD': 8,
    'MAX_ORDER_SIZE_USD': 18,
    'BASE_ORDER_SIZE_USD': 12,
    'MAX_DAILY_LOSS_USD': -15,
    'MAX_TOTAL_LOSS_USD': -25,
    'TARGET_VOLUME_PER_DAY': 70000,
    # Expected: $70k/day, 14 days to $1M ⭐ RECOMMENDED!
}

# ============================================================================
# PRESET 4: TURBO MODE ($100 capital, very high risk) 🚀
# ============================================================================
TURBO_MODE = {
    'LEVERAGE': 5,
    'num_orders': 5,
    'ORDER_REFRESH_INTERVAL': 2,
    'MIN_SPREAD_PCT': 0.01,
    'MAX_SPREAD_PCT': 0.08,
    'TARGET_SPREAD_MULTIPLIER': 0.8,
    'MAX_POSITION_SIZE_USD': 80,
    'POSITION_REBALANCE_THRESHOLD_USD': 40,
    'MIN_ORDER_SIZE_USD': 8,
    'MAX_ORDER_SIZE_USD': 20,
    'BASE_ORDER_SIZE_USD': 12,
    'MAX_DAILY_LOSS_USD': -15,
    'MAX_TOTAL_LOSS_USD': -30,
    'TARGET_VOLUME_PER_DAY': 100000,
    # Expected: $100k/day, 10 days to $1M 🔥 EXTREME!
}

# ============================================================================
# PRESET 5: ULTRA MODE ($100 capital, EXTREME risk) ⚠️ 
# ============================================================================
ULTRA_MODE = {
    'LEVERAGE': 5,
    'num_orders': 6,
    'ORDER_REFRESH_INTERVAL': 2,
    'MIN_SPREAD_PCT': 0.008,
    'MAX_SPREAD_PCT': 0.06,
    'TARGET_SPREAD_MULTIPLIER': 0.85,
    'MAX_POSITION_SIZE_USD': 90,
    'POSITION_REBALANCE_THRESHOLD_USD': 45,
    'MIN_ORDER_SIZE_USD': 10,
    'MAX_ORDER_SIZE_USD': 22,
    'BASE_ORDER_SIZE_USD': 15,
    'MAX_DAILY_LOSS_USD': -20,
    'MAX_TOTAL_LOSS_USD': -35,
    'TARGET_VOLUME_PER_DAY': 150000,
    # Expected: $150k/day, 7 days to $1M ⚠️ NOT RECOMMENDED!
}

# ============================================================================
# HOW TO USE
# ============================================================================
"""
1. Choose your mode based on risk tolerance:
   - SAFE_MODE: Low risk, slow (50 days)
   - BALANCED_MODE: Medium risk, moderate (20 days)
   - AGGRESSIVE_MODE: High risk, fast (14 days) ⭐ BEST!
   - TURBO_MODE: Very high risk, very fast (10 days)
   - ULTRA_MODE: EXTREME risk, fastest (7 days) ⚠️

2. In config.py, set:
   ACTIVE_PRESET = AGGRESSIVE_MODE  # or whichever you choose

3. The bot will use these settings automatically

Example:
```python
# At top of config.py
from config_presets import AGGRESSIVE_MODE

# Use preset
LEVERAGE = AGGRESSIVE_MODE['LEVERAGE']
num_orders = AGGRESSIVE_MODE['num_orders']
# ... etc for all settings
```

OR manually copy values to config.py for full control.
"""

# ============================================================================
# COMPARISON TABLE
# ============================================================================
"""
| Mode       | Leverage | Orders | Volume/Day | Days to $1M | Risk   | Recommended |
|------------|----------|--------|------------|-------------|--------|-------------|
| SAFE       | 3x       | 3      | $20k       | 50          | LOW    | Beginners   |
| BALANCED   | 4x       | 4      | $50k       | 20          | MEDIUM | Most users  |
| AGGRESSIVE | 4x       | 5      | $70k       | 14          | HIGH   | ⭐ BEST     |
| TURBO      | 5x       | 5      | $100k      | 10          | V.HIGH | Experienced |
| ULTRA      | 5x       | 6      | $150k      | 7           | EXTREME| ⚠️ Risky   |
"""
