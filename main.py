"""
Main Trading Bot Engine
Combines all modules into a complete trading system
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Optional
import yaml
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
import signal

# Import bot modules
from utils.data_collector import DataCollector
from utils.feature_engineering import FeatureEngineer
from model.ai_model import TradingModel
from utils.risk_manager import RiskManager
from utils.trade_executor import TradeExecutor
from utils.logger import setup_logger, log_trade, log_signal, log_pnl
from utils.notifier import TelegramNotifier


class TradingBot:
    """
    Main trading bot that orchestrates all components
    """
    
    def __init__(self, config_path: str = 'config/config.yaml', dry_run: bool = False):
        """
        Initialize trading bot
        
        Args:
            config_path: Path to configuration file
            dry_run: Run in simulation mode
        """
        # Load configuration
        self.config = self.load_config(config_path)
        self.dry_run = dry_run
        
        # Setup logger
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        self.logger = setup_logger('trading_bot', level=log_level)
        
        self.logger.info("=" * 60)
        self.logger.info("Initializing Trading Bot")
        self.logger.info("=" * 60)
        
        if dry_run:
            self.logger.warning("DRY RUN MODE - No real trades will be executed")
        
        # Load environment variables
        load_dotenv()
        
        # Initialize components
        self.data_collector = None
        self.feature_engineer = None
        self.model = None
        self.risk_manager = None
        self.trade_executor = None
        self.notifier = None
        self.dashboard_data = None
        
        self.setup_components()
        
        # Bot state
        self.is_running = False
        self.scheduler = None
        
        self.logger.info("Trading Bot initialized successfully")
    
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def setup_components(self):
        """Initialize all bot components"""
        try:
            # Data Collector
            self.logger.info("Setting up Data Collector...")
            self.data_collector = DataCollector(
                api_key=os.getenv('BITGET_API_KEY'),
                api_secret=os.getenv('BITGET_API_SECRET'),
                password=os.getenv('BITGET_PASSWORD'),
                testnet=self.config['exchange']['testnet']
            )
            
            # Feature Engineer
            self.logger.info("Setting up Feature Engineer...")
            self.feature_engineer = FeatureEngineer(
                config=self.config.get('indicators', {})
            )
            
            # AI Model
            self.logger.info("Loading AI Model...")
            model_type = self.config['ai_model']['type']
            self.model = TradingModel(model_type=model_type)
            
            # Try to load pre-trained model
            model_path = self.config['ai_model'].get('model_path')
            if model_path and os.path.exists(model_path):
                self.model.load_model(model_path)
                self.logger.info(f"Loaded model from {model_path}")
            else:
                self.logger.warning("No pre-trained model found. Train a model first!")
            
            # Risk Manager
            self.logger.info("Setting up Risk Manager...")
            self.risk_manager = RiskManager(
                config={
                    'initial_capital': self.config['trading']['initial_capital'],
                    'leverage': self.config['trading']['leverage'],
                    'risk_per_trade': self.config['risk_management']['risk_per_trade'],
                    'max_loss_per_day': self.config['risk_management']['max_loss_per_day'],
                    'max_open_positions': self.config['risk_management']['max_open_positions'],
                    'stop_loss_percent': self.config['risk_management']['stop_loss_percent'],
                    'take_profit_percent': self.config['risk_management']['take_profit_percent'],
                    'trailing_stop': self.config['risk_management']['trailing_stop'],
                    'trailing_stop_percent': self.config['risk_management']['trailing_stop_percent'],
                    'cooldown_period': self.config['risk_management']['cooldown_period'],
                    'confidence_threshold': self.config['ai_model']['confidence_threshold']
                }
            )
            
            # Trade Executor
            self.logger.info("Setting up Trade Executor...")
            self.trade_executor = TradeExecutor(
                api_key=os.getenv('BITGET_API_KEY'),
                api_secret=os.getenv('BITGET_API_SECRET'),
                password=os.getenv('BITGET_PASSWORD'),
                testnet=self.config['exchange']['testnet'],
                dry_run=self.dry_run
            )
            
            # Set leverage
            symbol = self.config['trading']['pair']
            leverage = self.config['trading']['leverage']
            self.trade_executor.set_leverage(symbol, leverage)
            
            # Telegram Notifier
            self.logger.info("Setting up Telegram Notifier...")
            telegram_config = self.config.get('notifications', {}).get('telegram', {})
            self.notifier = TelegramNotifier(
                bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
                chat_id=os.getenv('TELEGRAM_CHAT_ID'),
                enabled=telegram_config.get('enabled', False)
            )
            
            # Dashboard Data Manager (optional)
            try:
                from monitoring.dashboard import DashboardData
                self.dashboard_data = DashboardData()
                self.logger.info("Dashboard integration enabled")
            except ImportError:
                self.logger.debug("Dashboard module not available")
                self.dashboard_data = None
            
            self.logger.info("All components initialized")
            
        except Exception as e:
            self.logger.error(f"Error setting up components: {e}", exc_info=True)
            raise
    
    def trading_loop(self):
        """Main trading loop - runs on schedule"""
        try:
            self.logger.info("-" * 60)
            self.logger.info(f"Trading Loop - {datetime.now()}")
            
            symbol = self.config['trading']['pair']
            timeframe = self.config['data_collection']['ohlcv_timeframe']
            
            # 1. Fetch latest data
            self.logger.info(f"Fetching data for {symbol}...")
            df = self.data_collector.fetch_ohlcv(symbol, timeframe, limit=500)
            
            # 2. Extract features
            self.logger.info("Extracting features...")
            df = self.feature_engineer.extract_all_features(df)
            
            # 3. Get latest features for prediction
            latest_features = df.iloc[-1:]
            feature_cols = self.feature_engineer.get_feature_columns(df)
            X = latest_features[feature_cols]
            
            # 4. Get AI prediction
            self.logger.info("Getting AI prediction...")
            signal = self.model.get_signal(
                X, 
                confidence_threshold=self.config['ai_model']['confidence_threshold']
            )
            
            log_signal(self.logger, signal)
            
            # Update dashboard with signal
            if self.dashboard_data:
                self.dashboard_data.update_signal(signal)
            
            # Send signal notification
            if self.notifier and signal['signal'] != 'HOLD':
                self.notifier.notify_signal(signal)
            
            # 5. Check if should execute trade
            current_price = df['close'].iloc[-1]
            
            # Validate trade
            is_valid, reason = self.risk_manager.validate_trade(signal, current_price)
            
            if not is_valid:
                self.logger.info(f"Trade not executed: {reason}")
                return
            
            # 6. Execute trade
            if signal['signal'] == 'BUY':
                self.execute_long_trade(symbol, current_price, signal)
            elif signal['signal'] == 'SELL':
                self.execute_short_trade(symbol, current_price, signal)
            
            # 7. Check existing positions
            self.check_open_positions()
            
        except Exception as e:
            self.logger.error(f"Error in trading loop: {e}", exc_info=True)
            if self.notifier:
                self.notifier.notify_error(e, context={'action': 'trading_loop'})
    
    def execute_long_trade(self, symbol: str, current_price: float, signal: Dict):
        """Execute long position"""
        try:
            self.logger.info("Executing LONG trade...")
            
            # Calculate SL and TP
            stop_loss = self.risk_manager.calculate_stop_loss(current_price, 'long')
            take_profit = self.risk_manager.calculate_take_profit(current_price, 'long')
            
            # Calculate position size
            position_size, position_value = self.risk_manager.calculate_position_size(
                current_price, stop_loss, 'long'
            )
            
            if position_size <= 0:
                self.logger.warning("Invalid position size, trade cancelled")
                return
            
            # Open position with SL/TP
            result = self.trade_executor.open_position_with_sl_tp(
                symbol=symbol,
                side='long',
                amount=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            if result['success']:
                trade_info = {
                    'symbol': symbol,
                    'side': 'LONG',
                    'amount': position_size,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'confidence': signal['confidence'],
                    'timestamp': datetime.now()
                }
                
                # Log and notify
                log_trade(self.logger, trade_info)
                if self.notifier:
                    self.notifier.notify_trade(trade_info)
                
                # Update dashboard
                if self.dashboard_data:
                    self.dashboard_data.add_trade({
                        'side': 'long',
                        'entry_price': current_price,
                        'entry_timestamp': datetime.now().isoformat(),
                        'size': position_size
                    })
                    current_capital = self.risk_manager.current_capital
                    self.dashboard_data.update_capital(current_capital)
                    self.dashboard_data.update_equity(current_capital)
                
                # Update risk manager
                self.risk_manager.add_position({
                    'id': result['entry_order']['id'],
                    'side': 'long',
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'size': position_size
                })
            else:
                self.logger.error(f"Failed to open position: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Error executing long trade: {e}", exc_info=True)
    
    def execute_short_trade(self, symbol: str, current_price: float, signal: Dict):
        """Execute short position"""
        try:
            self.logger.info("Executing SHORT trade...")
            
            # Calculate SL and TP
            stop_loss = self.risk_manager.calculate_stop_loss(current_price, 'short')
            take_profit = self.risk_manager.calculate_take_profit(current_price, 'short')
            
            # Calculate position size
            position_size, position_value = self.risk_manager.calculate_position_size(
                current_price, stop_loss, 'short'
            )
            
            if position_size <= 0:
                self.logger.warning("Invalid position size, trade cancelled")
                return
            
            # Open position with SL/TP
            result = self.trade_executor.open_position_with_sl_tp(
                symbol=symbol,
                side='short',
                amount=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            if result['success']:
                trade_info = {
                    'symbol': symbol,
                    'side': 'SHORT',
                    'amount': position_size,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'confidence': signal['confidence'],
                    'timestamp': datetime.now()
                }
                
                # Log and notify
                log_trade(self.logger, trade_info)
                if self.notifier:
                    self.notifier.notify_trade(trade_info)
                
                # Update dashboard
                if self.dashboard_data:
                    self.dashboard_data.add_trade({
                        'side': 'short',
                        'entry_price': current_price,
                        'entry_timestamp': datetime.now().isoformat(),
                        'size': position_size
                    })
                    current_capital = self.risk_manager.current_capital
                    self.dashboard_data.update_capital(current_capital)
                    self.dashboard_data.update_equity(current_capital)
                
                # Update risk manager
                self.risk_manager.add_position({
                    'id': result['entry_order']['id'],
                    'side': 'short',
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'size': position_size
                })
            else:
                self.logger.error(f"Failed to open position: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Error executing short trade: {e}", exc_info=True)
    
    def check_open_positions(self):
        """Check and manage open positions"""
        try:
            symbol = self.config['trading']['pair']
            positions = self.trade_executor.get_positions(symbol)
            
            if positions:
                self.logger.info(f"Open positions: {len(positions)}")
                
                # Update dashboard with positions
                if self.dashboard_data:
                    self.dashboard_data.update_positions(positions)
                    
                    # Update risk metrics
                    risk_metrics = self.risk_manager.get_risk_metrics()
                    self.dashboard_data.update_risk_metrics(risk_metrics)
                
        except Exception as e:
            self.logger.error(f"Error checking positions: {e}", exc_info=True)
    
    def start(self):
        """Start the trading bot"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("STARTING TRADING BOT")
            self.logger.info("=" * 60)
            
            # Update dashboard status
            if self.dashboard_data:
                self.dashboard_data.update_bot_status('running')
                initial_capital = self.config['trading']['initial_capital']
                self.dashboard_data.update_capital(initial_capital)
                self.dashboard_data.update_equity(initial_capital)
            
            # Send start notification
            if self.notifier:
                self.notifier.notify_start()
            
            self.is_running = True
            
            # Setup scheduler
            self.scheduler = BlockingScheduler()
            
            # Schedule trading loop
            interval = self.config['trading']['interval']  # seconds
            self.scheduler.add_job(
                self.trading_loop,
                'interval',
                seconds=interval,
                id='trading_loop'
            )
            
            self.logger.info(f"Bot scheduled to run every {interval} seconds")
            
            # Run immediately
            self.trading_loop()
            
            # Start scheduler
            self.scheduler.start()
            
        except (KeyboardInterrupt, SystemExit):
            self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        self.logger.info("=" * 60)
        self.logger.info("STOPPING TRADING BOT")
        self.logger.info("=" * 60)
        
        self.is_running = False
        
        # Update dashboard status
        if self.dashboard_data:
            self.dashboard_data.update_bot_status('stopped')
        
        if self.scheduler:
            self.scheduler.shutdown()
        
        # Send stop notification
        if self.notifier:
            self.notifier.notify_stop("User stopped")
        
        self.logger.info("Bot stopped successfully")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Trading Bot for Bitget Futures')
    parser.add_argument('--config', default='config/config.yaml', help='Config file path')
    parser.add_argument('--dry-run', action='store_true', help='Run in simulation mode')
    
    args = parser.parse_args()
    
    # Create bot instance
    bot = TradingBot(config_path=args.config, dry_run=args.dry_run)
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutdown signal received...")
        bot.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start bot
    bot.start()


if __name__ == "__main__":
    main()
