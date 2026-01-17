"""LSTM model for profit prediction with proper binary classification"""
from tensorflow.keras.models import Sequential, load_model as keras_load_model
from tensorflow.keras.layers import Dense, LSTM, Dropout, BatchNormalization, Input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import numpy as np
import pickle
import os
from logger_config import setup_logger

logger = setup_logger('MLModel')


def build_lstm_model(input_shape, dropout_rate=0.3):
    """
    Build LSTM model for BINARY CLASSIFICATION
    
    Predicts: Will price move up profitably in next X minutes?
    Output: Probability between 0 and 1
    
    Args:
        input_shape: Tuple (timesteps, features)
        dropout_rate: Dropout rate for regularization
    
    Returns:
        Compiled Keras model
    """
    model = Sequential()
    model.add(Input(shape=input_shape))
    
    # First LSTM layer
    model.add(LSTM(units=64, return_sequences=True))
    model.add(BatchNormalization())
    model.add(Dropout(dropout_rate))
    
    # Second LSTM layer
    model.add(LSTM(units=64, return_sequences=True))
    model.add(BatchNormalization())
    model.add(Dropout(dropout_rate))
    
    # Third LSTM layer
    model.add(LSTM(units=32))
    model.add(Dropout(dropout_rate * 0.67))  # Slightly less dropout
    
    # Output layer - Binary classification
    model.add(Dense(1, activation='sigmoid'))
    
    # Compile with binary crossentropy
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', 'AUC']
    )
    
    logger.info(f"✅ Model built: {model.count_params():,} parameters")
    
    return model


def predict_probability(model, data, scaler, feature_cols, lookback_period):
    """
    Predict probability that price will move up profitably
    
    Args:
        model: Trained LSTM model
        data: DataFrame with features
        scaler: Fitted scaler
        feature_cols: List of feature column names
        lookback_period: Lookback window size
    
    Returns:
        float: Probability (0 to 1)
    """
    try:
        # Get recent data
        recent_data = data[feature_cols].tail(lookback_period)
        
        if len(recent_data) < lookback_period:
            logger.warning(f"Insufficient data for prediction: {len(recent_data)} < {lookback_period}")
            return 0.5  # Neutral
        
        # Scale and reshape
        scaled_data = scaler.transform(recent_data)
        X = scaled_data.reshape(1, lookback_period, len(feature_cols))
        
        # Predict
        probability = model.predict(X, verbose=0)[0][0]
        
        return float(probability)
        
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        return 0.5  # Return neutral on error


def get_trading_signal(probability, threshold_high=0.65, threshold_low=0.35):
    """
    Convert probability to trading signal
    
    Args:
        probability: Model output probability (0-1)
        threshold_high: Threshold for BULLISH signal
        threshold_low: Threshold for BEARISH signal
    
    Returns:
        tuple: (signal, confidence)
            signal: 'BULLISH', 'BEARISH', or 'NEUTRAL'
            confidence: Confidence level (0-1)
    """
    if probability > threshold_high:
        signal = 'BULLISH'
        confidence = (probability - threshold_high) / (1 - threshold_high)
    elif probability < threshold_low:
        signal = 'BEARISH'
        confidence = (threshold_low - probability) / threshold_low
    else:
        signal = 'NEUTRAL'
        confidence = 0
    
    return signal, confidence


def train_model(X_train, y_train, X_test, y_test, epochs=50, batch_size=32, model_path='models/'):
    """
    Train LSTM model with early stopping and checkpointing
    
    Args:
        X_train, y_train: Training data
        X_test, y_test: Validation data
        epochs: Maximum epochs
        batch_size: Batch size
        model_path: Path to save model
    
    Returns:
        Trained model
    """
    logger.info(f"🚀 Starting model training: {epochs} epochs, batch size {batch_size}")
    
    # Create models directory
    os.makedirs(model_path, exist_ok=True)
    
    # Build model
    input_shape = (X_train.shape[1], X_train.shape[2])
    model = build_lstm_model(input_shape)
    
    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=os.path.join(model_path, 'best_model.h5'),
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Train
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate
    test_loss, test_acc, test_auc = model.evaluate(X_test, y_test, verbose=0)
    logger.info(f"✅ Training complete!")
    logger.info(f"   Test Accuracy: {test_acc:.4f}")
    logger.info(f"   Test AUC: {test_auc:.4f}")
    logger.info(f"   Test Loss: {test_loss:.4f}")
    
    return model, history


def save_model(model, scaler, feature_cols, path='models/'):
    """
    Save model, scaler, and feature columns
    
    Args:
        model: Trained Keras model
        scaler: Fitted scaler
        feature_cols: List of feature column names
        path: Directory to save to
    """
    try:
        os.makedirs(path, exist_ok=True)
        
        # Save model
        model_file = os.path.join(path, 'lstm_model.h5')
        model.save(model_file)
        logger.info(f"✅ Model saved to {model_file}")
        
        # Save scaler
        scaler_file = os.path.join(path, 'scaler.pkl')
        with open(scaler_file, 'wb') as f:
            pickle.dump(scaler, f)
        logger.info(f"✅ Scaler saved to {scaler_file}")
        
        # Save feature columns
        features_file = os.path.join(path, 'feature_cols.pkl')
        with open(features_file, 'wb') as f:
            pickle.dump(feature_cols, f)
        logger.info(f"✅ Features saved to {features_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save model: {e}")
        return False


def load_model(path='models/'):
    """
    Load saved model, scaler, and feature columns
    
    Args:
        path: Directory to load from
    
    Returns:
        tuple: (model, scaler, feature_cols) or (None, None, None)
    """
    try:
        # Load model
        model_file = os.path.join(path, 'lstm_model.h5')
        model = keras_load_model(model_file)
        logger.info(f"✅ Model loaded from {model_file}")
        
        # Load scaler
        scaler_file = os.path.join(path, 'scaler.pkl')
        with open(scaler_file, 'rb') as f:
            scaler = pickle.load(f)
        logger.info(f"✅ Scaler loaded from {scaler_file}")
        
        # Load feature columns
        features_file = os.path.join(path, 'feature_cols.pkl')
        with open(features_file, 'rb') as f:
            feature_cols = pickle.load(f)
        logger.info(f"✅ Features loaded: {len(feature_cols)} columns")
        
        return model, scaler, feature_cols
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to load model: {e}")
        return None, None, None


def model_exists(path='models/'):
    """Check if a trained model exists"""
    model_file = os.path.join(path, 'lstm_model.h5')
    scaler_file = os.path.join(path, 'scaler.pkl')
    features_file = os.path.join(path, 'feature_cols.pkl')
    
    return (os.path.exists(model_file) and 
            os.path.exists(scaler_file) and 
            os.path.exists(features_file))

