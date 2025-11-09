"""
Logging Module
Custom logger with file rotation and formatting
"""

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
import colorlog


def setup_logger(name: str = 'bot', level: str = 'INFO', 
                log_dir: str = 'logs', console: bool = True) -> logging.Logger:
    """
    Setup custom logger with file and console handlers
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        console: Enable console output
        
    Returns:
        Configured logger
    """
    # Create logs directory if not exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Log format
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console format with colors
    console_format = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # File handler - Daily rotation
    log_file = os.path.join(log_dir, f'{name}.log')
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Error file handler - Separate file for errors
    error_file = os.path.join(log_dir, f'{name}_error.log')
    error_handler = RotatingFileHandler(
        error_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    logger.addHandler(error_handler)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
    
    return logger


def log_trade(logger: logging.Logger, trade_info: dict):
    """
    Log trade information in structured format
    
    Args:
        logger: Logger instance
        trade_info: Trade information dict
    """
    logger.info("=" * 60)
    logger.info("TRADE EXECUTED")
    logger.info(f"Symbol: {trade_info.get('symbol')}")
    logger.info(f"Side: {trade_info.get('side')}")
    logger.info(f"Size: {trade_info.get('amount')}")
    logger.info(f"Entry Price: {trade_info.get('entry_price')}")
    logger.info(f"Stop Loss: {trade_info.get('stop_loss')}")
    logger.info(f"Take Profit: {trade_info.get('take_profit')}")
    logger.info(f"Signal Confidence: {trade_info.get('confidence', 'N/A')}")
    logger.info(f"Timestamp: {trade_info.get('timestamp', datetime.now())}")
    logger.info("=" * 60)


def log_signal(logger: logging.Logger, signal: dict, features: dict = None):
    """
    Log trading signal
    
    Args:
        logger: Logger instance
        signal: Signal dict
        features: Optional feature values
    """
    logger.info("-" * 60)
    logger.info(f"SIGNAL: {signal.get('signal')} | Confidence: {signal.get('confidence', 0):.2%}")
    if signal.get('probabilities'):
        logger.info(f"Probabilities: {signal.get('probabilities')}")
    if features:
        logger.debug(f"Features: {features}")
    logger.info("-" * 60)


def log_pnl(logger: logging.Logger, pnl_info: dict):
    """
    Log profit/loss information
    
    Args:
        logger: Logger instance
        pnl_info: PnL information dict
    """
    pnl = pnl_info.get('pnl', 0)
    log_level = logging.INFO if pnl >= 0 else logging.WARNING
    
    logger.log(log_level, "=" * 60)
    logger.log(log_level, f"POSITION CLOSED - {'PROFIT' if pnl >= 0 else 'LOSS'}")
    logger.log(log_level, f"Symbol: {pnl_info.get('symbol')}")
    logger.log(log_level, f"Side: {pnl_info.get('side')}")
    logger.log(log_level, f"Entry: {pnl_info.get('entry_price')}")
    logger.log(log_level, f"Exit: {pnl_info.get('exit_price')}")
    logger.log(log_level, f"PnL: ${pnl:.2f} ({pnl_info.get('pnl_percent', 0):.2f}%)")
    logger.log(log_level, f"Duration: {pnl_info.get('duration', 'N/A')}")
    logger.log(log_level, "=" * 60)


def log_daily_summary(logger: logging.Logger, summary: dict):
    """
    Log daily trading summary
    
    Args:
        logger: Logger instance
        summary: Summary dict
    """
    logger.info("=" * 60)
    logger.info("DAILY SUMMARY")
    logger.info(f"Date: {summary.get('date', datetime.now().date())}")
    logger.info(f"Total Trades: {summary.get('total_trades', 0)}")
    logger.info(f"Wins: {summary.get('wins', 0)}")
    logger.info(f"Losses: {summary.get('losses', 0)}")
    logger.info(f"Win Rate: {summary.get('win_rate', 0):.2%}")
    logger.info(f"Total PnL: ${summary.get('total_pnl', 0):.2f}")
    logger.info(f"Best Trade: ${summary.get('best_trade', 0):.2f}")
    logger.info(f"Worst Trade: ${summary.get('worst_trade', 0):.2f}")
    logger.info(f"Capital: ${summary.get('current_capital', 0):.2f}")
    logger.info("=" * 60)


def log_error_with_context(logger: logging.Logger, error: Exception, context: dict = None):
    """
    Log error with context information
    
    Args:
        logger: Logger instance
        error: Exception object
        context: Additional context dict
    """
    logger.error("!" * 60)
    logger.error(f"ERROR: {type(error).__name__}")
    logger.error(f"Message: {str(error)}")
    if context:
        logger.error(f"Context: {context}")
    logger.error("!" * 60, exc_info=True)


if __name__ == "__main__":
    # Test logger
    logger = setup_logger('test_bot', level='DEBUG')
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test trade logging
    trade_info = {
        'symbol': 'SOL/USDT:USDT',
        'side': 'LONG',
        'amount': 0.5,
        'entry_price': 100.50,
        'stop_loss': 98.00,
        'take_profit': 104.00,
        'confidence': 0.75,
        'timestamp': datetime.now()
    }
    log_trade(logger, trade_info)
    
    # Test signal logging
    signal = {
        'signal': 'BUY',
        'confidence': 0.68,
        'probabilities': [0.32, 0.68]
    }
    log_signal(logger, signal)
    
    # Test PnL logging
    pnl_info = {
        'symbol': 'SOL/USDT:USDT',
        'side': 'LONG',
        'entry_price': 100.50,
        'exit_price': 102.30,
        'pnl': 9.00,
        'pnl_percent': 1.79,
        'duration': '15 minutes'
    }
    log_pnl(logger, pnl_info)
