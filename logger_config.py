"""Centralized logging configuration for the trading bot"""
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logger(name='TradingBot', log_dir='logs'):
    """
    Setup comprehensive logging with file rotation and multiple handlers
    
    Args:
        name: Logger name
        log_dir: Directory for log files
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Console handler - INFO level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # Main file handler - DEBUG level with rotation
    main_file = os.path.join(log_dir, 'trading_bot.log')
    file_handler = RotatingFileHandler(
        main_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Trades file handler - for trade execution logs
    trades_file = os.path.join(log_dir, f'trades_{datetime.now().strftime("%Y%m%d")}.log')
    trades_handler = RotatingFileHandler(
        trades_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=30,
        encoding='utf-8'
    )
    trades_handler.setLevel(logging.INFO)
    trades_handler.addFilter(TradeFilter())
    trades_format = logging.Formatter(
        '%(asctime)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    trades_handler.setFormatter(trades_format)
    
    # Error file handler - errors only
    error_file = os.path.join(log_dir, 'errors.log')
    error_handler = RotatingFileHandler(
        error_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    
    # Add all handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(trades_handler)
    logger.addHandler(error_handler)
    
    return logger


class TradeFilter(logging.Filter):
    """Filter to only log trade-related messages"""
    def filter(self, record):
        trade_keywords = ['ORDER', 'FILL', 'TRADE', 'PROFIT', 'LOSS', 'POSITION']
        return any(keyword in record.getMessage().upper() for keyword in trade_keywords)


def log_trade(logger, action, symbol, side, price, size, order_id=None):
    """
    Log trade execution with consistent format
    
    Args:
        logger: Logger instance
        action: Action type (PLACED, FILLED, CANCELLED, etc)
        symbol: Trading symbol
        side: buy or sell
        price: Order price
        size: Order size
        order_id: Order ID if available
    """
    msg = f"TRADE {action} | {symbol} | {side.upper()} | Price: {price:.6f} | Size: {size:.4f}"
    if order_id:
        msg += f" | ID: {order_id}"
    logger.info(msg)


def log_pnl(logger, pnl, total_volume, trade_count):
    """
    Log PnL statistics
    
    Args:
        logger: Logger instance
        pnl: Net profit/loss
        total_volume: Total trading volume
        trade_count: Number of trades
    """
    logger.info(f"PNL UPDATE | Net PnL: ${pnl:.2f} | Volume: ${total_volume:,.2f} | Trades: {trade_count}")


def log_error_with_context(logger, error, context):
    """
    Log error with additional context
    
    Args:
        logger: Logger instance
        error: Exception object
        context: Dictionary with additional context
    """
    logger.error(f"ERROR: {str(error)}", exc_info=True, extra={'context': context})
