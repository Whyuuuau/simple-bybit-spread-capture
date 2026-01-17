"""
Train ML Model for Profit Prediction

This script trains the LSTM model for the hybrid bot.
Run this ONCE before running the bot for the first time.

Usage:
    python train_model.py
"""

import asyncio
from datetime import datetime
from config import exchange, symbol, ML_LOOKBACK_PERIOD, ML_FUTURE_WINDOW, ML_PROFIT_THRESHOLD_PCT
from data_handler import fetch_historical_data, add_features, prepare_lstm_data
from model import train_model, save_model
from logger_config import setup_logger

logger = setup_logger('ModelTraining')


async def main():
    """Train and save ML model"""
    try:
        logger.info("=" * 80)
        logger.info("🤖 STARTING ML MODEL TRAINING")
        logger.info("=" * 80)
        
        # Fetch historical data
        logger.info(f"Fetching historical data for {symbol}...")
        logger.info("This may take a few minutes...")
        
        # Fetch more data for training (last 30 days of 1m candles = 43,200 candles)
        historical_data = await fetch_historical_data(
            exchange, 
            symbol, 
            limit=10000  # Fetch 10k candles for training
        )
        
        if historical_data.empty:
            logger.error("❌ Failed to fetch historical data!")
            return False
        
        logger.info(f"✅ Fetched {len(historical_data)} candles")
        
        # Add features
        logger.info("Adding technical indicators...")
        data_with_features = add_features(historical_data)
        logger.info(f"✅ Added features, {len(data_with_features)} rows after cleaning")
        
        # Prepare LSTM data
        logger.info("Preparing data for LSTM...")
        X_train, X_test, y_train, y_test, scaler, feature_cols = prepare_lstm_data(
            data_with_features,
            lookback_period=ML_LOOKBACK_PERIOD,
            future_window=ML_FUTURE_WINDOW,
            profit_threshold_pct=ML_PROFIT_THRESHOLD_PCT
        )
        
        if X_train is None:
            logger.error("❌ Failed to prepare LSTM data!")
            return False
        
        logger.info(f"✅ Data prepared:")
        logger.info(f"   Training samples: {len(X_train)}")
        logger.info(f"   Test samples: {len(X_test)}")
        logger.info(f"   Features: {len(feature_cols)}")
        logger.info(f"   Lookback period: {ML_LOOKBACK_PERIOD}")
        
        # Train model
        logger.info("=" * 80)
        logger.info("Starting model training...")
        logger.info("This will take 10-60 minutes depending on your hardware")
        logger.info("=" * 80)
        
        model, history = train_model(
            X_train, y_train,
            X_test, y_test,
            epochs=50,
            batch_size=32
        )
        
        if model is None:
            logger.error("❌ Model training failed!")
            return False
        
        # Save model
        logger.info("Saving model...")
        success = save_model(model, scaler, feature_cols)
        
        if success:
            logger.info("=" * 80)
            logger.info("✅ MODEL TRAINING COMPLETE!")
            logger.info("=" * 80)
            logger.info("Model saved to: models/lstm_model.h5")
            logger.info("You can now run the bot with: python main.py")
            logger.info("=" * 80)
            return True
        else:
            logger.error("❌ Failed to save model!")
            return False
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}", exc_info=True)
        return False
    finally:
        await exchange.close()


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
