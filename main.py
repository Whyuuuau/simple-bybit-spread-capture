"""
🚀 HYBRID VOLUME + PROFIT FUTURES BOT 🚀

Ultimate trading bot for maximum volume + profit with safety first!

Features:
✅ Futures trading with leverage
✅ ML-powered profit signals
✅ High-volume generation
✅ Auto risk management
✅ Position monitoring & rebalancing
✅ Liquidation protection
✅ PnL tracking
✅ Emergency stops

Author: Your Name
"""

import asyncio
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional

# Core modules
from config import *
from logger_config import setup_logger, log_trade, log_pnl
from futures_position_manager import FuturesPositionManager
from order_book_analyzer import *
from trading import *
from data_handler import fetch_historical_data, add_features

# ML models
# Try to import XGBoost model first (preferred)
try:
    from model_xgboost import (
        load_xgboost_model,
        predict_probability as predict_xgb, # Keep original alias for now, will adjust later if needed
        get_trading_signal,
        xgboost_model_exists,
        HAS_XGBOOST as xgboost_available # Use alias for consistency
    )
except ImportError:
    xgboost_available = False

# Fallback to LSTM
try:
    from model_lstm import (
        load_lstm_model,
        predict_probability as predict_lstm, # Keep original alias for now
        model_exists as lstm_model_exists
    )
except ImportError:
    lstm_model_exists = lambda: False # Define a dummy function if not available

from utils import *

# Setup logger
logger = setup_logger('HybridBot')


class HybridVolumeBot:
    """
    Ultimate Hybrid Bot for Volume + Profit
    
    Strategy:
    - Base: Market making for volume generation
    - Enhanced: ML-powered opportunistic profit taking
    - Safety: Comprehensive risk management
    """
    
    def __init__(self):
        self.exchange = exchange
        self.symbol = symbol
        self.leverage = LEVERAGE
        self.running = False
        
        # Demo trading - use real position manager
        self.position_manager = FuturesPositionManager(
            exchange=self.exchange,
            symbol=self.symbol,
            leverage=self.leverage,
            max_position_usd=MAX_POSITION_SIZE_USD,
            rebalance_threshold_usd=POSITION_REBALANCE_THRESHOLD_USD
        )
        
        # PnL tracker
        self.pnl_tracker = PnLTracker()
        
        # ML model (MANDATORY! ✅)
        self.ml_model = None
        self.scaler = None
        self.feature_cols = None
        self.model_type = None
        self.use_ml = True  # ALWAYS True - ML is mandatory!
        
        # Tracking
        self.last_signal = 'NEUTRAL'
        self.signal_confidence = 0
        self.total_volume = 0
        self.total_trades = 0
        self.ml_signal_count = {'BULLISH': 0, 'NEUTRAL': 0, 'BEARISH': 0}
        
        # Session tracking
        self.session_start = datetime.now()
        self.session_start_time = datetime.now()  # Alias for compatibility
        self.start_time = datetime.now()
        self.rebalance_count = 0
        self.daily_pnl_start = 0
        self.emergency_stop_triggered = False
        
        # Loop timing
        self.last_data_update = 0
        self.last_ml_update = 0
        self.last_stats_log = 0
        self.last_position_check = 0
        
        # Market data cache
        self.historical_data = None
        self.current_signal = 'NEUTRAL'
        
        # Statistics
        self.stats = {
            'total_volume': 0,
            'total_trades': 0,
            'net_pnl': 0,
            'total_fees': 0,
            'orders_placed': 0,
            'orders_filled': 0,
            'rebalances': 0,
            'ml_signals': {'BULLISH': 0, 'BEARISH': 0, 'NEUTRAL': 0},
            'session_high_volume': 0,
            'session_low_pnl': 0,
            'session_high_pnl': 0,
        }
        
        logger.info("=" * 80)
        logger.info("🚀 BYBIT DEMO TRADING BOT INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"Symbol: {symbol}")
        logger.info(f"Leverage: {self.leverage}x")
        logger.info(f"Max Position: ${MAX_POSITION_SIZE_USD}")
        logger.info(f"ML Model: {'ENABLED' if USE_ML_MODEL else 'DISABLED'}")
        logger.info(f"Mode: DEMO MAINNET")
        logger.info(f"API Endpoint: https://api-demo.bybit.com")
        logger.info("=" * 80)
        logger.info("")
    
    async def initialize(self):
        """Initialize bot - set leverage, load ML model, etc"""
        try:
            logger.info("🔧 Initializing bot...")
            
            # Set leverage on demo exchange
            logger.info(f"Setting leverage to {self.leverage}x...")
            try:
                success = await self.position_manager.set_leverage(self.leverage)
                if not success:
                    logger.warning("⚠️ Leverage setting may not be supported in demo")
                    logger.info("✅ Demo uses pre-configured leverage (this is normal)")
            except Exception as e:
                if '10032' in str(e):
                    logger.warning(f"⚠️ Demo trading limitation: {e}")
                    logger.info("✅ Continuing with demo's pre-configured leverage setting")
                else:
                    logger.error(f"❌ Failed to set leverage: {e}")
                    return False
            
            # Load ML model (MANDATORY! ✅)
            logger.info("Loading ML model (REQUIRED)...")
            
            model_loaded = False
            
            # Try XGBoost first (preferred)
            if xgboost_available and xgboost_model_exists():
                logger.info("🚀 XGBoost model detected!")
                self.ml_model, self.scaler, self.feature_cols = load_xgboost_model()
                if self.ml_model:
                    logger.info("✅ XGBoost model loaded successfully!")
                    logger.info("   Using SUPERIOR XGBoost model (faster & better accuracy)")
                    self.model_type = 'xgboost'
                    model_loaded = True
            
            # Fallback to LSTM
            if not model_loaded and lstm_model_exists():
                logger.info("📊 LSTM model detected (XGBoost not found)")
                self.ml_model, self.scaler, self.feature_cols = load_lstm_model()
                if self.ml_model:
                    logger.info("✅ LSTM model loaded successfully!")
                    logger.info("   Using LSTM model (consider upgrading to XGBoost)")
                    self.model_type = 'lstm'
                    model_loaded = True
            
            # ML model is MANDATORY!
            if not model_loaded:
                logger.error("=" * 80)
                logger.error("❌ NO ML MODEL FOUND - BOT CANNOT START!")
                logger.error("=" * 80)
                logger.error("ML model is MANDATORY for profit optimization!")
                logger.error("")
                logger.error("Please train a model first:")
                logger.error("  Recommended: python train_xgboost.py")
                logger.error("  Alternative: python train_model.py")
                logger.error("")
                logger.error("Bot will not start without ML model.")
                logger.error("=" * 80)
                return False
            
            # Fetch initial market data
            logger.info("Fetching initial market data...")
            await self.update_market_data()
            
            # Check current position
            position = await self.position_manager.get_current_position()
            logger.info(f"Current position: ${position['position_value_usd']:.2f} {position['side'].upper()}")
            
            # Get margin info
            margin = await self.position_manager.get_margin_info()
            logger.info(f"Available margin: ${margin['available_margin']:.2f}")
            
            logger.info("✅ Bot initialization complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}", exc_info=True)
            return False
    
    async def update_market_data(self):
        """Update historical data and ML signal"""
        try:
            # Fetch historical data
            self.historical_data = await fetch_historical_data(
                self.exchange, 
                self.symbol, 
                ML_LOOKBACK_PERIOD + 100
            )
            
            if self.historical_data.empty:
                logger.warning("No historical data fetched")
                return
            
            # Add features
            self.historical_data = add_features(self.historical_data)
            
            # Update ML signal if model available
            if self.use_ml and self.ml_model:
                await self.update_ml_signal()
            
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
    
    async def update_ml_signal(self):
        """Update ML trading signal"""
        try:
            if not self.use_ml or not self.ml_model:
                return
            
            # Predict probability (use appropriate function based on model type)
            if hasattr(self, 'model_type') and self.model_type == 'xgboost':
                probability = predict_xgb(
                    self.ml_model,
                    self.historical_data,
                    self.scaler,
                    self.feature_cols
                )
            else:
                # LSTM prediction
                probability = predict_lstm(
                    self.ml_model,
                    self.historical_data,
                    self.scaler,
                    self.feature_cols,
                    ML_LOOKBACK_PERIOD
                )
            
            # Get trading signal (same for both)
            signal, confidence = get_trading_signal(
                probability,
                threshold_high=ML_CONFIDENCE_THRESHOLD,
                threshold_low=1 - ML_CONFIDENCE_THRESHOLD
            )
            
            # Update state
            old_signal = self.current_signal
            self.current_signal = signal
            self.signal_confidence = confidence
            
            # Log signal changes
            if signal != old_signal:
                model_name = getattr(self, 'model_type', 'unknown').upper()
                logger.info(f"🤖 ML Signal [{model_name}] changed: {old_signal} → {signal} (conf: {confidence:.2%}, prob: {probability:.2%})")
                self.stats['ml_signals'][signal] += 1
            
        except Exception as e:
            logger.error(f"Error updating ML signal: {e}")
    
    async def calculate_dynamic_spread(self):
        """Calculate spread based on market conditions and ML signal"""
        try:
            # Get order book
            order_book = await fetch_order_book(self.exchange, self.symbol, ORDER_BOOK_DEPTH)
            
            # Get volatility if we have data
            volatility = 0
            if self.historical_data is not None and 'volatility_20' in self.historical_data.columns:
                volatility = self.historical_data['volatility_20'].iloc[-1]
                # Normalize volatility (0-1 range)
                volatility = min(volatility / self.historical_data['close'].iloc[-1], 1.0)
            
            # Base spread from order book
            base_spread_pct = calculate_optimal_spread(
                order_book,
                MIN_SPREAD_PCT,
                MAX_SPREAD_PCT,
                volatility
            )
            
            # Adjust based on ML signal
            if self.current_signal == 'NEUTRAL' or not self.use_ml:
                # Volume mode: tighter spread for more fills
                final_spread = base_spread_pct * TARGET_SPREAD_MULTIPLIER
            else:
                # Profit mode: wider spread for better margins
                final_spread = base_spread_pct * (1.0 + self.signal_confidence * 0.5)
            
            # Ensure within limits
            final_spread = clamp(final_spread, MIN_SPREAD_PCT, MAX_SPREAD_PCT)
            
            return final_spread
            
        except Exception as e:
            logger.error(f"Error calculating spread: {e}")
            return MIN_SPREAD_PCT
    
    async def calculate_order_sizes(self, position_value):
        """Calculate order sizes based on ML signal and position"""
        try:
            base_size_usd = BASE_ORDER_SIZE_USD / num_orders
            
            # Adjust based on ML signal
            if self.use_ml and self.current_signal != 'NEUTRAL':
                # Size up on strong signals
                size_multiplier = 1.0 + (self.signal_confidence * 0.5)
                base_size_usd *= size_multiplier
            
            # Cap at max order size
            base_size_usd = min(base_size_usd, MAX_ORDER_SIZE_USD / num_orders)
            
            # Adjust based on current position (for rebalancing)
            # Adjust based on current position (for rebalancing)
            buy_sizes = []
            sell_sizes = []
            
            # Get current price once for conversion
            ticker = await self.exchange.fetch_ticker(self.symbol)
            current_price = (ticker['bid'] + ticker['ask']) / 2
            
            # DEBUG LOG
            logger.info(f"🔎 CALC_SIZES: BaseUSD={BASE_ORDER_SIZE_USD} | Price={current_price} | Num={num_orders}")

            
            for i in range(num_orders):
                buy_size_usd = base_size_usd
                sell_size_usd = base_size_usd
                
                # If we have a position, adjust to help rebalance
                if abs(position_value) > 50:
                    if position_value > 0:
                        # Long position - increase sell orders
                        sell_size_usd *= 1.2
                        buy_size_usd *= 0.8
                    else:
                        # Short position - increase buy orders
                        buy_size_usd *= 1.2
                        sell_size_usd *= 0.8
                
                # ML signal adjustments
                if self.current_signal == 'BULLISH':
                    buy_size_usd *= 1.3
                    sell_size_usd *= 0.7
                elif self.current_signal == 'BEARISH':
                    sell_size_usd *= 1.3
                    buy_size_usd *= 0.7
                
                # Convert USD to ETH amount and round properly
                buy_amount_eth = calc_sol_size(buy_size_usd / current_price, current_price)
                sell_amount_eth = calc_sol_size(sell_size_usd / current_price, current_price)
                
                # LOG FIRST ORDER ONLY
                if i == 0:
                    logger.info(f"🔎 CALC_RESULT: BuyUSD={buy_size_usd:.2f} -> Amt={buy_amount_eth} | SellUSD={sell_size_usd:.2f} -> Amt={sell_amount_eth}")

                buy_sizes.append(buy_amount_eth)
                sell_sizes.append(sell_amount_eth)
            
            return buy_sizes, sell_sizes
            
        except Exception as e:
            logger.error(f"Error calculating order sizes: {e}")
            return [BASE_ORDER_SIZE_USD] * num_orders, [BASE_ORDER_SIZE_USD] * num_orders
    
    async def place_orders(self):
        """Place optimized orders based on market conditions"""
        try:
            # Get current position
            position = await self.position_manager.get_current_position()
            position_value = position['position_value_usd']
            
            # Get market price for size calculations
            bid, ask = await get_market_price(self.exchange, self.symbol)
            mid_price = (bid + ask) / 2
            
            # Calculate dynamic spread
            spread_pct = await self.calculate_dynamic_spread()
            
            # Get order book for optimal price levels
            order_book = await fetch_order_book(self.exchange, self.symbol, ORDER_BOOK_DEPTH)
            
            # Find optimal price levels
            buy_prices, sell_prices = find_optimal_price_levels(
                order_book,
                num_orders,
                spread_pct,
                PRICE_PRECISION
            )
            
            # Calculate order sizes
            buy_sizes_usd, sell_sizes_usd = await self.calculate_order_sizes(position_value)
            
            # Convert USD to contracts
            buy_sizes = [calculate_amount_from_usd(size, price, AMOUNT_PRECISION) 
                        for size, price in zip(buy_sizes_usd, buy_prices)]
            sell_sizes = [calculate_amount_from_usd(size, price, AMOUNT_PRECISION)
                         for size, price in zip(sell_sizes_usd, sell_prices)]
            
            # Create target orders
            target_orders = []
            for i in range(num_orders):
                target_orders.append({
                    'side': 'buy',
                    'price': buy_prices[i],
                    'size': buy_sizes[i]
                })
                target_orders.append({
                    'side': 'sell',
                    'price': sell_prices[i],
                    'size': sell_sizes[i]
                })
            
            # Smart order management (only update what changed)
            stats = await smart_order_management(
                self.exchange,
                self.symbol,
                target_orders,
                price_tolerance_pct=0.1
            )
            
            self.stats['orders_placed'] += stats['placed']
            
            logger.debug(f"Orders | Kept: {stats['kept']} | Cancelled: {stats['cancelled']} | Placed: {stats['placed']}")
            
        except Exception as e:
            logger.error(f"Error placing orders: {e}", exc_info=True)
    
    async def check_and_manage_position(self):
        """Check position and rebalance if needed"""
        try:
            # Check if position needs rebalancing
            if await self.position_manager.needs_rebalancing():
                logger.warning("⚠️ Position rebalancing triggered")
                success = await self.position_manager.rebalance()
                if success:
                    self.stats['rebalances'] += 1
            
            # Check liquidation risk
            risk = await self.position_manager.check_liquidation_risk()
            
            if risk['risk_level'] == 'CRITICAL':
                logger.error(f"🚨 CRITICAL LIQUIDATION RISK: {risk['distance_to_liq_pct']:.2f}% from liquidation!")
                # Force rebalance
                await self.position_manager.rebalance(force=True)
            elif risk['risk_level'] == 'HIGH':
                logger.warning(f"⚠️ HIGH liquidation risk: {risk['distance_to_liq_pct']:.2f}% from liquidation")
            
        except Exception as e:
            logger.error(f"Error managing position: {e}")
    
    async def update_statistics(self):
        """Update trading statistics"""
        try:
            # Update PnL
            pnl_data = await self.pnl_tracker.calculate_pnl(
                self.exchange, 
                self.symbol
            )
            
            self.stats['total_volume'] = pnl_data['total_volume']
            self.stats['total_trades'] = pnl_data['trade_count']
            self.stats['total_fees'] = pnl_data['total_fees']
            self.stats['net_pnl'] = pnl_data.get('realized_pnl', pnl_data.get('estimated_pnl', 0))
            self.stats['orders_filled'] = pnl_data['trade_count']  # ✅ Track filled orders
            
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
    
    def check_safety_limits(self):
        """Check if safety limits are breached"""
        try:
            # Check daily loss limit
            daily_pnl = self.stats['net_pnl'] - self.daily_pnl_start
            
            if daily_pnl < MAX_DAILY_LOSS_USD:
                logger.error(f"🚨 DAILY LOSS LIMIT BREACHED: ${daily_pnl:.2f}")
                return False
            
            # Check total loss limit
            if self.stats['net_pnl'] < MAX_TOTAL_LOSS_USD:
                logger.error(f"🚨 TOTAL LOSS LIMIT BREACHED: ${self.stats['net_pnl']:.2f}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking safety limits: {e}")
            return True
    
    def log_statistics(self):
        """Log current statistics"""
        try:
            runtime = (datetime.now() - self.start_time).total_seconds() / 3600
            volume_per_hour = self.stats['total_volume'] / runtime if runtime > 0 else 0
            
            # Update high/low tracking
            if self.stats['total_volume'] > self.stats['session_high_volume']:
                self.stats['session_high_volume'] = self.stats['total_volume']
            if self.stats['net_pnl'] < self.stats['session_low_pnl']:
                self.stats['session_low_pnl'] = self.stats['net_pnl']
            if self.stats['net_pnl'] > self.stats['session_high_pnl']:
                self.stats['session_high_pnl'] = self.stats['net_pnl']
            
            position = self.position_manager.position_history[-1] if self.position_manager.position_history else None
            
            logger.info("=" * 80)
            logger.info("📊 BOT STATISTICS")
            logger.info("=" * 80)
            logger.info(f"Runtime:        {runtime:.2f} hours")
            logger.info(f"Total Volume:   ${self.stats['total_volume']:,.2f}")
            logger.info(f"Volume/Hour:    ${volume_per_hour:,.2f}")
            logger.info(f"Total Trades:   {self.stats['total_trades']}")
            logger.info(f"Orders Placed:  {self.stats['orders_placed']}")
            logger.info(f"Net PnL:        ${self.stats['net_pnl']:.2f}")
            logger.info(f"Total Fees:     ${self.stats['total_fees']:.2f}")
            logger.info(f"Rebalances:     {self.stats['rebalances']}")
            
            if position:
                logger.info(f"Position:       ${position['position_value_usd']:.2f} {position['side'].upper()}")
                logger.info(f"Unrealized PnL: ${position['unrealized_pnl']:.2f}")
                if position['liquidation_price'] > 0:
                    logger.info(f"Liq Price:      ${position['liquidation_price']:.4f}")
            
            if self.use_ml:
                logger.info(f"ML Signal:      {self.current_signal} ({self.signal_confidence:.1%})")
                logger.info(f"ML Stats:       B:{self.stats['ml_signals']['BULLISH']} "
                          f"N:{self.stats['ml_signals']['NEUTRAL']} "
                          f"Be:{self.stats['ml_signals']['BEARISH']}")
            
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Error logging statistics: {e}")
    
    def print_session_recap(self):
        """Print comprehensive session recap - MANDATORY OUTPUT! ✅"""
        try:
            session_duration = (datetime.now() - self.session_start_time).total_seconds()
            hours = session_duration / 3600
            minutes = (session_duration % 3600) / 60
            
            # Calculate rates
            volume_per_hour = self.stats['total_volume'] / hours if hours > 0 else 0
            volume_per_day_projected = volume_per_hour * 24
            
            # Calculate profit metrics
            profit_per_hour = self.stats['net_pnl'] / hours if hours > 0 else 0
            profit_per_day_projected = profit_per_hour * 24
            
            # Calculate days to $1M
            days_to_million = 1000000 / volume_per_day_projected if volume_per_day_projected > 0 else 999
            
            # Get final position
            final_position = self.position_manager.position_history[-1] if self.position_manager.position_history else None
            
            print("\n" + "=" * 100)
            print("🎯 SESSION RECAP - BOT RUN SUMMARY")
            print("=" * 100)
            
            # Session Info
            print("\n📅 SESSION INFORMATION:")
            print(f"  Start Time:     {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  End Time:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Duration:       {int(hours)}h {int(minutes)}m")
            print(f"  Exchange:       {'Bitunix' if EXCHANGE_NAME == 'bitunix' else 'Bybit'}")
            print(f"  Symbol:         {self.symbol}")
            print(f"  Leverage:       {self.leverage}x")
            print(f"  ML Model:       {getattr(self, 'model_type', 'None').upper()}")
            
            # Volume Statistics
            print("\n📊 VOLUME STATISTICS:")
            print(f"  Total Volume:        ${self.stats['total_volume']:>15,.2f}")
            print(f"  Volume/Hour:         ${volume_per_hour:>15,.2f}")
            print(f"  Projected/Day:       ${volume_per_day_projected:>15,.2f}")
            print(f"  Total Trades:        {self.stats['total_trades']:>15,}")
            print(f"  Orders Placed:       {self.stats['orders_placed']:>15,}")
            print(f"  Orders Filled:       {self.stats['orders_filled']:>15,}")
            if self.stats['orders_placed'] > 0:
                fill_rate = (self.stats['orders_filled'] / self.stats['orders_placed']) * 100
                print(f"  Fill Rate:           {fill_rate:>15.2f}%")
            
            # Profit & Loss
            print("\n💰 PROFIT & LOSS:")
            print(f"  Net PnL:             ${self.stats['net_pnl']:>15.2f}")
            print(f"  Total Fees Paid:     ${self.stats['total_fees']:>15.2f}")
            print(f"  Profit/Hour:         ${profit_per_hour:>15.2f}")
            print(f"  Projected/Day:       ${profit_per_day_projected:>15.2f}")
            print(f"  Session High PnL:    ${self.stats['session_high_pnl']:>15.2f}")
            print(f"  Session Low PnL:     ${self.stats['session_low_pnl']:>15.2f}")
            
            # Position & Risk
            print("\n📈 POSITION & RISK:")
            if final_position:
                print(f"  Final Position:      ${final_position['position_value_usd']:>15.2f} {final_position['side'].upper()}")
                print(f"  Unrealized PnL:      ${final_position['unrealized_pnl']:>15.2f}")
                print(f"  Entry Price:         ${final_position['entry_price']:>15.4f}")
                if final_position['liquidation_price'] > 0:
                    print(f"  Liquidation Price:   ${final_position['liquidation_price']:>15.4f}")
            else:
                print(f"  Final Position:      ${'0.00':>15} NEUTRAL")
            print(f"  Rebalances:          {self.stats['rebalances']:>15}")
            
            # ML Statistics
            if self.use_ml:
                print("\n🤖 ML MODEL PERFORMANCE:")
                total_signals = sum(self.stats['ml_signals'].values())
                print(f"  Total Signals:       {total_signals:>15}")
                print(f"  Bullish Signals:     {self.stats['ml_signals']['BULLISH']:>15} ({self.stats['ml_signals']['BULLISH']/total_signals*100 if total_signals > 0 else 0:.1f}%)")
                print(f"  Neutral Signals:     {self.stats['ml_signals']['NEUTRAL']:>15} ({self.stats['ml_signals']['NEUTRAL']/total_signals*100 if total_signals > 0 else 0:.1f}%)")
                print(f"  Bearish Signals:     {self.stats['ml_signals']['BEARISH']:>15} ({self.stats['ml_signals']['BEARISH']/total_signals*100 if total_signals > 0 else 0:.1f}%)")
                print(f"  Current Signal:      {self.current_signal:>15} ({self.signal_confidence*100:.1f}%)")
            
            # Performance Metrics
            print("\n🎯 PERFORMANCE METRICS:")
            print(f"  Volume Target/Day:   ${TARGET_VOLUME_PER_DAY:>15,.2f}")
            volume_progress = (volume_per_day_projected / TARGET_VOLUME_PER_DAY) * 100
            print(f"  Target Achievement:  {volume_progress:>15.1f}%")
            print(f"  Days to $1M Volume:  {days_to_million:>15.1f}")
            
            if self.stats['net_pnl'] > 0:
                roi = (self.stats['net_pnl'] / INITIAL_BALANCE_USD) * 100
                print(f"  Session ROI:         {roi:>15.2f}%")
            
            # Recommendations
            print("\n💡 RECOMMENDATIONS:")
            if volume_per_day_projected < TARGET_VOLUME_PER_DAY * 0.8:
                print("  ⚠️  Volume below target - consider tightening spreads")
            elif volume_per_day_projected > TARGET_VOLUME_PER_DAY * 1.2:
                print("  ✅ Excellent volume generation!")
            
            if self.stats['net_pnl'] > 0:
                print("  ✅ Profit positive - strategy working well!")
            elif self.stats['net_pnl'] < -10:
                print("  ⚠️  Losses exceeding expectations - review spread settings")
            
            if self.stats['rebalances'] > 10:
                print("  ⚠️  High rebalance frequency - consider adjusting position limits")
            
            if hours < 1:
                print("  ℹ️  Short session - run longer for better statistics")
            
            print("\n" + "=" * 100)
            print("🏁 END OF SESSION RECAP")
            print("=" * 100 + "\n")
            
            # Also log to file
            logger.info("=" * 100)
            logger.info("SESSION RECAP GENERATED")
            logger.info(f"Volume: ${self.stats['total_volume']:,.2f} | PnL: ${self.stats['net_pnl']:.2f} | Runtime: {int(hours)}h {int(minutes)}m")
            logger.info("=" * 100)
            
        except Exception as e:
            logger.error(f"Error printing session recap: {e}", exc_info=True)
            print(f"\n⚠️  Error generating session recap: {e}\n")
    
    async def emergency_shutdown(self):
        """Emergency shutdown - close all positions and cancel orders"""
        logger.warning("🚨 EMERGENCY SHUTDOWN INITIATED!")
        
        try:
            # Cancel all orders
            await cancel_all_orders(self.exchange, self.symbol)
            
            # Close all positions
            await self.position_manager.emergency_close_all()
            
            # Update final stats
            await self.update_statistics()
            
            # Print SESSION RECAP - MANDATORY! ✅
            logger.info("Generating session recap...")
            self.print_session_recap()
            
            # Final stats to log
            self.log_statistics()
            
            logger.warning("✅ Emergency shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during emergency shutdown: {e}", exc_info=True)
    
    async def run(self):
        """Main bot loop"""
        self.running = True
        
        try:
            logger.info("🚀 Bot starting main loop...")
            
            while self.running:
                loop_start = asyncio.get_event_loop().time()
                
                # Update market data periodically
                if loop_start - self.last_data_update > DATA_UPDATE_INTERVAL:
                    await self.update_market_data()
                    self.last_data_update = loop_start
                
                # Update ML signal periodically
                if self.use_ml and loop_start - self.last_ml_update > ML_UPDATE_INTERVAL:
                    await self.update_ml_signal()
                    self.last_ml_update = loop_start
                
                # Place/update orders
                await self.place_orders()
                
                # Check and manage position
                if loop_start - self.last_position_check > POSITION_CHECK_INTERVAL:
                    await self.check_and_manage_position()
                    self.last_position_check = loop_start
                
                # Update statistics
                await self.update_statistics()
                
                # Check safety limits
                if not self.check_safety_limits():
                    logger.error("🚨 Safety limits breached - stopping bot!")
                    break
                
                # Log statistics periodically
                if loop_start - self.last_stats_log > STATS_LOG_INTERVAL:
                    self.log_statistics()
                    self.last_stats_log = loop_start
                
                # Sleep before next iteration
                await asyncio.sleep(ORDER_REFRESH_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("⚠️ Bot stopped by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"❌ Fatal error in main loop: {e}", exc_info=True)
        finally:
            await self.emergency_shutdown()
            await self.exchange.close()
            logger.info("👋 Bot stopped")


async def main():
    """Entry point"""
    # Create bot instance
    bot = HybridVolumeBot()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        bot.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize bot
    if not await bot.initialize():
        logger.error("Failed to initialize bot - exiting")
        return 1
    
    # Run bot
    await bot.run()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
