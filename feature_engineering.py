"""
Advanced Feature Engineering for ML Trading Model
Includes both modern and legacy features for compatibility
"""

import pandas as pd
import numpy as np
from talib import abstract
import warnings
warnings.filterwarnings('ignore')

def calculate_rsi(series, period=14):
    """Calculate RSI indicator with Series return"""
    try:
        rsi_np = abstract.RSI(series, timeperiod=period)
        return pd.Series(rsi_np, index=series.index)
    except:
        # Fallback
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

def add_legacy_features(df):
    """Add legacy features expected by the model"""
    # Returns
    df['return_1'] = df['close'].pct_change(1)
    df['return_5'] = df['close'].pct_change(5)
    df['return_10'] = df['close'].pct_change(10)
    df['return_20'] = df['close'].pct_change(20)
    
    # Price Position
    df['high_20'] = df['high'].rolling(window=20).max()
    df['low_20'] = df['low'].rolling(window=20).min()
    df['price_position'] = (df['close'] - df['low_20']) / (df['high_20'] - df['low_20'] + 1e-10)
    
    # Volatility
    df['volatility_10'] = df['close'].rolling(window=10).std()
    df['volatility_20'] = df['close'].rolling(window=20).std()
    df['volatility_ratio'] = df['volatility_10'] / (df['volatility_20'] + 1e-10)
    
    # Momentum (Legacy Formula)
    df['momentum'] = df['close'] / df['close'].shift(10) - 1
    
    # Moving Average Cross
    df['sma_7'] = df['close'].rolling(window=7).mean()
    df['sma_25'] = df['close'].rolling(window=25).mean()
    df['sma_99'] = df['close'].rolling(window=99).mean()
    df['ma_cross_fast'] = (df['sma_7'] - df['sma_25']) / df['close']
    df['ma_cross_slow'] = (df['sma_25'] - df['sma_99']) / df['close']
    
    # Body Ratio
    df['body'] = abs(df['close'] - df['open'])
    df['body_ratio'] = df['body'] / ((df['high'] - df['low']) + 1e-10)
    
    return df

def add_stochastic_rsi(df, period=14):
    """Add Stochastic RSI"""
    rsi = calculate_rsi(df['close'], period)
    df['rsi'] = rsi  # IMPORTANT: Save RSI column
    
    stoch_rsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    df['stoch_rsi'] = stoch_rsi
    df['stoch_rsi_k'] = stoch_rsi.rolling(3).mean()
    df['stoch_rsi_d'] = df['stoch_rsi_k'].rolling(3).mean()
    return df

def add_ichimoku(df):
    """Add Ichimoku Cloud"""
    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    df['tenkan_sen'] = (high_9 + low_9) / 2
    
    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    df['kijun_sen'] = (high_26 + low_26) / 2
    
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    
    high_52 = df['high'].rolling(window=52).max()
    low_52 = df['low'].rolling(window=52).min()
    df['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)
    
    df['chikou_span'] = df['close'].shift(-26)
    df['cloud_thickness'] = abs(df['senkou_span_a'] - df['senkou_span_b'])
    df['price_vs_cloud'] = df['close'] - df['senkou_span_a']
    return df

def add_adx(df, period=14):
    """Add ADX"""
    try:
        df['adx'] = abstract.ADX(df, timeperiod=period)
        df['plus_di'] = abstract.PLUS_DI(df, timeperiod=period)
        df['minus_di'] = abstract.MINUS_DI(df, timeperiod=period)
    except:
        df['adx'] = 50
        df['plus_di'] = 25
        df['minus_di'] = 25
    return df

def add_volume_indicators(df):
    """Add Volume Indicators"""
    try:
        df['obv'] = abstract.OBV(df)
    except:
        df['obv'] = (np.sign(df['close'].diff()) * df['volume']).cumsum()
    
    df['volume_ma_10'] = df['volume'].rolling(10).mean()
    df['volume_ma_20'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / (df['volume_ma_20'] + 1e-10) # Matches name
    df['volume_roc'] = df['volume'].pct_change(10)
    df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    return df

def add_volatility_indicators(df):
    """Add Volatility Indicators"""
    try:
        df['atr'] = abstract.ATR(df, timeperiod=14)
    except:
        # Simple ATR fallback
        tr = pd.DataFrame({
            'a': df['high'] - df['low'],
            'b': abs(df['high'] - df['close'].shift(1)),
            'c': abs(df['low'] - df['close'].shift(1))
        }).max(axis=1)
        df['atr'] = tr.rolling(14).mean()
        
    df['atr_pct'] = df['atr'] / df['close']
    
    bb_middle = df['close'].rolling(20).mean()
    bb_std = df['close'].rolling(20).std()
    bb_upper = bb_middle + (bb_std * 2)
    bb_lower = bb_middle - (bb_std * 2)
    df['bb_width'] = (bb_upper - bb_lower) / bb_middle
    df['bb_position'] = (df['close'] - bb_lower) / (bb_upper - bb_lower)
    return df

def add_price_patterns(df):
    """Add Price Patterns"""
    df['higher_high'] = (df['high'] > df['high'].shift(1)).astype(int)
    df['lower_low'] = (df['low'] < df['low'].shift(1)).astype(int)
    df['higher_close'] = (df['close'] > df['close'].shift(1)).astype(int)
    
    df['candle_body'] = abs(df['close'] - df['open']) / df['open']
    df['lower_shadow'] = (df[['open', 'close']].min(axis=1) - df['low']) / df['open']
    return df

def add_gacor_features(df):
    """
    Add High-Impact 'Gacor' Features for HFT/Scalping
    Focuses on Velocity, Volume Shocks, and Micro-Volatility
    """
    # 1. Micro-Velocity (Rate of Change)
    df['roc_1'] = df['close'].pct_change(1) * 100
    df['roc_3'] = df['close'].pct_change(3) * 100
    df['roc_5'] = df['close'].pct_change(5) * 100
    
    # 2. Volume Shock (Relative Volume)
    vol_ma5 = df['volume'].rolling(5).mean()
    vol_ma20 = df['volume'].rolling(20).mean()
    df['vol_shock'] = vol_ma5 / (vol_ma20 + 1e-10)
    
    # 3. Candle Range Shock (Volatility Spike)
    df['candle_range'] = (df['high'] - df['low']) / df['close']
    range_ma20 = df['candle_range'].rolling(20).mean()
    df['range_shock'] = df['candle_range'] / (range_ma20 + 1e-10)
    
    # 4. Intra-Candle Strength (Where did we close?)
    # 1.0 = High, 0.0 = Low
    df['close_loc'] = (df['close'] - df['low']) / ((df['high'] - df['low']) + 1e-10)
    
    # 5. Pseudo-VWAP deviation (approximate)
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    df['price_vs_typical'] = (df['close'] - typical_price) / typical_price
    
    return df

def add_all_features(df):
    """Add ALL features (Legacy + Advanced)"""
    print("Adding advanced features...")
    df = df.copy()
    
    # 1. Add Legacy Features (Fixes 'not in index' errors)
    df = add_legacy_features(df)
    print("✓ Legacy features (Returns, Momentum, etc)")
    
    # 2. Add Advanced Features
    df = add_stochastic_rsi(df)
    df = add_ichimoku(df)
    df = add_adx(df)
    df = add_volume_indicators(df)
    df = add_volatility_indicators(df)
    df = add_price_patterns(df)
    df = add_gacor_features(df)
    
    # Session features simplified
    if hasattr(df.index, 'hour'):
        df['hour'] = df.index.hour
        df['is_ny_session'] = ((df['hour'] >= 13) & (df['hour'] < 21)).astype(int)
    else:
        df['is_ny_session'] = 0
        
    df = df.dropna()
    print(f"✓ Feature engineering complete: {len(df.columns)} columns")
    return df
