"""Enhanced data handler with technical indicators for ML model"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from logger_config import setup_logger

logger = setup_logger('DataHandler')

# Import advanced feature engineering
try:
    from feature_engineering import add_all_features
    logger.info("✅ Advanced feature engineering module active")
except ImportError:
    logger.warning("⚠️ Advanced features not found, check feature_engineering.py")
    def add_all_features(df): return df  # Fallback

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
    Uses advanced feature engineering module with 30+ indicators
    
    Args:
        data: DataFrame with OHLCV data
    
    Returns:
        DataFrame: Data with added features
    """
    if data.empty:
        return data
        
    try:
        # Use the new advanced feature engineering module
        logger.info("Adding advanced features...")
        df = add_all_features(data)
        
        # Log feature count
        if not df.empty:
            logger.info(f"Feature engineering complete: {len(df.columns)} features generated")
            
        return df
        
    except Exception as e:
        logger.error(f"Error adding features: {e}", exc_info=True)
        return data


def prepare_lstm_data(data, lookback_period=50, future_window=10, profit_threshold_pct=0.1):
    """
    Prepare data for LSTM/XGBoost model training
    
    Args:
        data: DataFrame with features
        lookback_period: Lookback window for sequences
        future_window: How many minutes ahead to predict
        profit_threshold_pct: Minimum profit % to classify as profitable
    
    Returns:
        tuple: (X_train, X_test, y_train, y_test, scaler, feature_cols)
    """
    try:
        # Select relevant features (exclude raw OHLCV and derived columns)
        # Dynamic selection: use all numeric columns except OHLCV
        exclude_cols = ['open', 'high', 'low', 'close', 'volume', 'timestamp']
        feature_cols = [col for col in data.columns if col not in exclude_cols]
        
        # Filter to only columns that exist (double check)
        feature_cols = [col for col in feature_cols if col in data.columns]
        
        logger.info(f"Using {len(feature_cols)} features for model")
        
        if not feature_cols:
            logger.error("No features found for training!")
            return None, None, None, None, None, None
        
        # Scale features
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data[feature_cols])
        
        # Create target: Will price go up profitably in next `future_window` minutes?
        future_returns = data['close'].pct_change(future_window).shift(-future_window)
        target = (future_returns > (profit_threshold_pct / 100)).astype(int)
        
        # Create sequences
        X, y = [], []
        
        # Check if we have enough data
        if len(scaled_data) < lookback_period + future_window + 10:
            logger.error(f"Not enough data! Need at least {lookback_period + future_window + 10} rows.")
            return None, None, None, None, None, None
            
        for i in range(lookback_period, len(scaled_data) - future_window):
            X.append(scaled_data[i-lookback_period:i])
            y.append(target.iloc[i])
        
        X = np.array(X)
        y = np.array(y)
        
        # Time-based split (important for time series!)
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        logger.info(f"Prepared data: Train={len(X_train)}, Test={len(X_test)}")
        logger.info(f"Positive samples: {y_train.sum()}/{len(y_train)} ({y_train.mean()*100:.1f}%)")
        
        return X_train, X_test, y_train, y_test, scaler, feature_cols
        
    except Exception as e:
        logger.error(f"Error preparing data: {e}", exc_info=True)
        return None, None, None, None, None, None
