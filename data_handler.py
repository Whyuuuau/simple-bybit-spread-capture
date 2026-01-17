"""Enhanced data handler with technical indicators for ML model"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from logger_config import setup_logger

logger = setup_logger('DataHandler')

# Try to import TA-Lib, fallback to pandas if not available
try:
    import talib
    HAS_TALIB = True
    logger.info("✅ TA-Lib available for technical indicators")
except ImportError:
    HAS_TALIB = False
    logger.warning("⚠️ TA-Lib not available, using pandas for indicators")


async def fetch_historical_data(exchange, symbol, lookback_period=100):
    """
    Fetch historical OHLCV data
    
    Args:
        exchange: CCXT exchange instance
        symbol: Trading symbol
        lookback_period: Number of candles to fetch
    
    Returns:
        DataFrame: Historical data with OHLCV
    """
    try:
        # Fetch extra data for indicator calculation
        limit = lookback_period + 200
        
        # Use 1-minute candles (more stable than 1-second)
        ohlcv = await exchange.fetch_ohlcv(
            symbol, 
            timeframe='1m', 
            limit=limit
        )
        
        data = pd.DataFrame(
            ohlcv, 
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data.set_index('timestamp', inplace=True)
        
        logger.debug(f"Fetched {len(data)} candles for {symbol}")
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}", exc_info=True)
        return pd.DataFrame()


def add_features(data):
    """
    Add technical indicators and features for ML model
    
    Args:
        data: DataFrame with OHLCV data
    
    Returns:
        DataFrame: Data with added features
    """
    if data.empty:
        return data
    
    df = data.copy()
    
    try:
        # ================================================================
        # PRICE-BASED FEATURES
        # ================================================================
        
        # Returns (multiple timeframes)
        df['return_1'] = df['close'].pct_change(1)
        df['return_5'] = df['close'].pct_change(5)
        df['return_10'] = df['close'].pct_change(10)
        df['return_20'] = df['close'].pct_change(20)
        
        # Price position relative to recent high/low
        df['high_20'] = df['high'].rolling(window=20).max()
        df['low_20'] = df['low'].rolling(window=20).min()
        df['price_position'] = (df['close'] - df['low_20']) / (df['high_20'] - df['low_20'] + 1e-10)
        
        # ================================================================
        # VOLATILITY FEATURES
        # ================================================================
        
        df['volatility_10'] = df['close'].rolling(window=10).std()
        df['volatility_20'] = df['close'].rolling(window=20).std()
        df['volatility_ratio'] = df['volatility_10'] / (df['volatility_20'] + 1e-10)
        
        # ATR (Average True Range)
        if HAS_TALIB:
            df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        else:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            df['atr'] = true_range.rolling(14).mean()
        
        # ================================================================
        # MOMENTUM INDICATORS
        # ================================================================
        
        # RSI
        if HAS_TALIB:
            df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        else:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10)
            df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        if HAS_TALIB:
            df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(
                df['close'], 
                fastperiod=12, 
                slowperiod=26, 
                signalperiod=9
            )
        else:
            ema_fast = df['close'].ewm(span=12, adjust=False).mean()
            ema_slow = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = ema_fast - ema_slow
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Momentum
        df['momentum'] = df['close'] / df['close'].shift(10) - 1
        
        # ================================================================
        # MOVING AVERAGES
        # ================================================================
        
        # Simple moving averages
        df['sma_7'] = df['close'].rolling(window=7).mean()
        df['sma_25'] = df['close'].rolling(window=25).mean()
        df['sma_99'] = df['close'].rolling(window=99).mean()
        
        # Exponential moving average
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # MA crossovers
        df['ma_cross_fast'] = (df['sma_7'] - df['sma_25']) / df['close']
        df['ma_cross_slow'] = (df['sma_25'] - df['sma_99']) / df['close']
        
        # ================================================================
        # BOLLINGER BANDS
        # ================================================================
        
        if HAS_TALIB:
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
                df['close'], 
                timeperiod=20, 
                nbdevup=2, 
                nbdevdn=2
            )
        else:
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (std * 2)
            df['bb_lower'] = df['bb_middle'] - (std * 2)
        
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'] + 1e-10)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # ================================================================
        # VOLUME FEATURES
        # ================================================================
        
        # Volume moving averages
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / (df['volume_sma'] + 1e-10)
        
        # Volume-price trend
        df['vpt'] = (df['volume'] * df['return_1']).cumsum()
        
        # ================================================================
        # CANDLE PATTERNS
        # ================================================================
        
        # Body and shadow ratios
        df['body'] = abs(df['close'] - df['open'])
        df['upper_shadow'] = df['high'] - df[['close', 'open']].max(axis=1)
        df['lower_shadow'] = df[['close', 'open']].min(axis=1) - df['low']
        df['body_ratio'] = df['body'] / ((df['high'] - df['low']) + 1e-10)
        
        # ================================================================
        # IMPROVED FEATURES (for better accuracy!) ✅
        # ================================================================
        
        # Price momentum (multiple timeframes)
        df['momentum_5'] = df['close'].pct_change(5)
        df['momentum_10'] = df['close'].pct_change(10)
        df['momentum_20'] = df['close'].pct_change(20)
        
        # Volume surge detection
        volume_ma_20 = df['volume'].rolling(20).mean()
        df['volume_surge'] = (df['volume'] > volume_ma_20 * 1.5).astype(int)
        
        # Support/Resistance distance
        high_20 = df['high'].rolling(20).max()
        low_20 = df['low'].rolling(20).min()
        df['distance_to_high'] = (high_20 - df['close']) / (df['close'] + 1e-10)
        df['distance_to_low'] = (df['close'] - low_20) / (df['close'] + 1e-10)
        
        # Time-based features (for session patterns)
        df['hour'] = df.index.hour
        df['is_asian_session'] = ((df['hour'] >= 0) & (df['hour'] < 8)).astype(int)
        df['is_london_session'] = ((df['hour'] >= 8) & (df['hour'] < 16)).astype(int)
        df['is_ny_session'] = ((df['hour'] >= 13) & (df['hour'] < 22)).astype(int)
        
        # Price position in range
        df['price_position'] = (df['close'] - low_20) / (high_20 - low_20 + 1e-10)
        
        # ================================================================
        # CLEANUP
        # ================================================================
        
        # Drop NaN values
        df.dropna(inplace=True)
        
        logger.debug(f"Added {len(df.columns) - 5} features to data")
        
        return df
        
    except Exception as e:
        logger.error(f"Error adding features: {e}", exc_info=True)
        return data


def prepare_lstm_data(data, lookback_period=50, future_window=10, profit_threshold_pct=0.1):
    """
    Prepare data for LSTM model training
    
    FIXED: Target is now binary classification (profitable or not)
    
    Args:
        data: DataFrame with features
        lookback_period: Lookback window for LSTM
        future_window: How many minutes ahead to predict
        profit_threshold_pct: Minimum profit % to classify as profitable
    
    Returns:
        tuple: (X_train, X_test, y_train, y_test, scaler, feature_cols)
    """
    try:
        # Select relevant features (exclude raw OHLCV and derived columns)
        feature_cols = [
            'return_1', 'return_5', 'return_10', 'return_20',
            'price_position', 'volatility_10', 'volatility_20', 'volatility_ratio',
            'atr', 'rsi', 'macd', 'macd_hist', 'momentum',
            'ma_cross_fast', 'ma_cross_slow', 'bb_position', 'bb_width',
            'volume_ratio', 'body_ratio'
        ]
        
        # Filter to only columns that exist
        feature_cols = [col for col in feature_cols if col in data.columns]
        
        logger.info(f"Using {len(feature_cols)} features for model")
        
        # Scale features
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data[feature_cols])
        
        # Create target: Will price go up profitably in next `future_window` minutes?
        future_returns = data['close'].pct_change(future_window).shift(-future_window)
        target = (future_returns > (profit_threshold_pct / 100)).astype(int)
        
        # Create sequences
        X, y = [], []
        
        for i in range(lookback_period, len(scaled_data) - future_window):
            X.append(scaled_data[i-lookback_period:i])
            y.append(target.iloc[i])
        
        X = np.array(X)
        y = np.array(y)
        
        # Time-based split (important for time series!)
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        logger.info(f"Prepared LSTM data: Train={len(X_train)}, Test={len(X_test)}")
        logger.info(f"Positive samples: {y_train.sum()}/{len(y_train)} ({y_train.mean()*100:.1f}%)")
        
        return X_train, X_test, y_train, y_test, scaler, feature_cols
        
    except Exception as e:
        logger.error(f"Error preparing LSTM data: {e}", exc_info=True)
        return None, None, None, None, None, None

