"""
Advanced Feature Engineering for ML Trading Model

Adds 30+ technical indicators for improved prediction accuracy:
- Momentum & Trend indicators
- Volume analysis
- Volatility measurements
- Market microstructure
- Time-based features
"""

import pandas as pd
import numpy as np
from talib import abstract
import warnings
warnings.filterwarnings('ignore')

def calculate_rsi(series, period=14):
    """Calculate RSI indicator"""
    try:
        return abstract.RSI(series, timeperiod=period)
    except:
        # Fallback if TA-Lib not available
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

def add_stochastic_rsi(df, period=14):
    """Add Stochastic RSI indicator"""
    rsi = calculate_rsi(df['close'], period)
    stoch_rsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    df['stoch_rsi'] = stoch_rsi
    df['stoch_rsi_k'] = stoch_rsi.rolling(3).mean()  # %K line
    df['stoch_rsi_d'] = df['stoch_rsi_k'].rolling(3).mean()  # %D line
    return df

def add_ichimoku(df):
    """Add Ichimoku Cloud indicators"""
    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2
    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    df['tenkan_sen'] = (high_9 + low_9) / 2
    
    # Kijun-sen (Base Line): (26-period high + 26-period low)/2
    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    df['kijun_sen'] = (high_26 + low_26) / 2
    
    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    
    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2
    high_52 = df['high'].rolling(window=52).max()
    low_52 = df['low'].rolling(window=52).min()
    df['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)
    
    # Chikou Span (Lagging Span): Close shifted -26
    df['chikou_span'] = df['close'].shift(-26)
    
    # Cloud thickness
    df['cloud_thickness'] = abs(df['senkou_span_a'] - df['senkou_span_b'])
    
    # Price relative to cloud
    df['price_vs_cloud'] = df['close'] - df['senkou_span_a']
    
    return df

def add_adx(df, period=14):
    """Add Average Directional Index (trend strength)"""
    try:
        df['adx'] = abstract.ADX(df, timeperiod=period)
        df['plus_di'] = abstract.PLUS_DI(df, timeperiod=period)
        df['minus_di'] = abstract.MINUS_DI(df, timeperiod=period)
    except:
        # Simple fallback
        df['adx'] = 50  # Neutral
        df['plus_di'] = 25
        df['minus_di'] = 25
    return df

def add_volume_indicators(df):
    """Add volume-based indicators"""
    # On-Balance Volume (OBV)
    try:
        df['obv'] = abstract.OBV(df)
    except:
        obv = []
        obv_val = 0
        for i, row in df.iterrows():
            if i == 0:
                obv_val = row['volume']
            else:
                if row['close'] > df.loc[i-1, 'close']:
                    obv_val += row['volume']
                elif row['close'] < df.loc[i-1, 'close']:
                    obv_val -= row['volume']
            obv.append(obv_val)
        df['obv'] = obv
    
    # Volume MA ratio
    df['volume_ma_10'] = df['volume'].rolling(10).mean()
    df['volume_ma_20'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma_20']
    
    # Volume Rate of Change
    df['volume_roc'] = df['volume'].pct_change(10)
    
    # VWAP (Volume Weighted Average Price)
    df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    df['price_vs_vwap'] = (df['close'] - df['vwap']) / df['vwap']
    
    return df

def add_volatility_indicators(df):
    """Add volatility measurements"""
    # Average True Range
    try:
        df['atr'] = abstract.ATR(df, timeperiod=14)
        df['atr_pct'] = df['atr'] / df['close']
    except:
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr'] = true_range.rolling(14).mean()
        df['atr_pct'] = df['atr'] / df['close']
    
    # Bollinger Band Width
    bb_middle = df['close'].rolling(20).mean()
    bb_std = df['close'].rolling(20).std()
    bb_upper = bb_middle + (bb_std * 2)
    bb_lower = bb_middle - (bb_std * 2)
    df['bb_width'] = (bb_upper - bb_lower) / bb_middle
    df['bb_position'] = (df['close'] - bb_lower) / (bb_upper - bb_lower)
    
    # Volatility regime
    returns = df['close'].pct_change()
    df['volatility_20'] = returns.rolling(20).std()
    df['volatility_regime'] = df['volatility_20'] / df['volatility_20'].rolling(100).mean()
    
    return df

def add_momentum_indicators(df):
    """Add momentum oscillators"""
    # MACD
    try:
        macd_result = abstract.MACD(df)
        df['macd'] = macd_result['macd']
        df['macd_signal'] = macd_result['macdsignal']
        df['macd_hist'] = macd_result['macdhist']
    except:
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
    
    # ROC (Rate of Change)
    df['roc_5'] = df['close'].pct_change(5) * 100
    df['roc_10'] = df['close'].pct_change(10) * 100
    df['roc_20'] = df['close'].pct_change(20) * 100
    
    # Momentum
    df['momentum_10'] = df['close'] - df['close'].shift(10)
    df['momentum_20'] = df['close'] - df['close'].shift(20)
    
    return df

def add_price_patterns(df):
    """Add price pattern features"""
    # Higher highs / Lower lows
    df['higher_high'] = (df['high'] > df['high'].shift(1)).astype(int)
    df['lower_low'] = (df['low'] < df['low'].shift(1)).astype(int)
    df['higher_close'] = (df['close'] > df['close'].shift(1)).astype(int)
    
    # Price action strength
    df['bullish_candles_5'] = df['higher_close'].rolling(5).sum()
    df['bearish_candles_5'] = (1 - df['higher_close']).rolling(5).sum()
    
    # Candle body size
    df['candle_body'] = abs(df['close'] - df['open']) / df['open']
    df['candle_range'] = (df['high'] - df['low']) / df['open']
    df['upper_shadow'] = (df['high'] - df[['open', 'close']].max(axis=1)) / df['open']
    df['lower_shadow'] = (df[['open', 'close']].min(axis=1) - df['low']) / df['open']
    
    return df

def add_session_features(df):
    """Add time-based trading session features"""
    # Extract hour (assuming index is datetime)
    if isinstance(df.index, pd.DatetimeIndex):
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        
        # Trading sessions (UTC)
        df['is_asian_session'] = ((df['hour'] >= 0) & (df['hour'] < 8)).astype(int)
        df['is_london_session'] = ((df['hour'] >= 8) & (df['hour'] < 16)).astype(int)
        df['is_ny_session'] = ((df['hour'] >= 13) & (df['hour'] < 21)).astype(int)
        df['is_overlap_session'] = ((df['hour'] >= 13) & (df['hour'] < 16)).astype(int)  # London-NY overlap
        
        # Weekend effect
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    else:
        # Default values if no datetime index
        df['hour'] = 12
        df['day_of_week'] = 3
        df['is_asian_session'] = 0
        df['is_london_session'] = 1
        df['is_ny_session'] = 0
        df['is_overlap_session'] = 0
        df['is_weekend'] = 0
    
    return df

def add_trend_strength(df):
    """Add trend strength measurements"""
    # EMA cross
    ema_fast = df['close'].ewm(span=12).mean()
    ema_slow = df['close'].ewm(span=26).mean()
    df['ema_cross'] = (ema_fast - ema_slow) / ema_slow
    
    # Trend strength (distance from MA)
    ma_50 = df['close'].rolling(50).mean()
    df['distance_from_ma50'] = (df['close'] - ma_50) / ma_50
    
    # Consecutive moves
    price_change =df['close'].diff()
    df['consecutive_up'] = (price_change > 0).rolling(5).sum()
    df['consecutive_down'] = (price_change < 0).rolling(5).sum()
    
    return df

def add_all_features(df):
    """
    Add ALL advanced features to dataframe
    
    Returns dataframe with 30+ additional features for ML model
    """
    print("Adding advanced features...")
    
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Add all feature groups
    df = add_stochastic_rsi(df)
    print("✓ Stochastic RSI")
    
    df = add_ichimoku(df)
    print("✓ Ichimoku Cloud")
    
    df = add_adx(df)
    print("✓ ADX")
    
    df = add_volume_indicators(df)
    print("✓ Volume indicators")
    
    df = add_volatility_indicators(df)
    print("✓ Volatility indicators")
    
    df = add_momentum_indicators(df)
    print("✓ Momentum indicators")
    
    df = add_price_patterns(df)
    print("✓ Price patterns")
    
    df = add_session_features(df)
    print("✓ Session features")
    
    df = add_trend_strength(df)
    print("✓ Trend strength")
    
    # Drop any NaN values from indicators
    initial_rows = len(df)
    df = df.dropna()
    dropped_rows = initial_rows - len(df)
    print(f"✓ Dropped {dropped_rows} rows with NaN values")
    
    print(f"✓ Total features added: {len(df.columns) - 5}")  # -5 for OHLCV
    print(f"✓ Final dataset size: {len(df)} rows")
    
    return df

if __name__ == "__main__":
    # Test feature engineering
    print("Testing feature engineering module...")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='5min')
    sample_df = pd.DataFrame({
        'open': np.random.randn(1000).cumsum() + 3000,
        'high': np.random.randn(1000).cumsum() + 3010,
        'low': np.random.randn(1000).cumsum() + 2990,
        'close': np.random.randn(1000).cumsum() + 3000,
        'volume': np.random.rand(1000) * 1000000
    }, index=dates)
    
    # Add features
    enhanced_df = add_all_features(sample_df)
    
    print("\nSample features:")
    print(enhanced_df.columns.tolist())
    print("\nFeature statistics:")
    print(enhanced_df.describe())
