#!/bin/bash

# Test script untuk memverifikasi semua modul berfungsi
# Run: bash test_modules.sh

echo "=========================================="
echo "Testing Bot Modules"
echo "=========================================="

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check Python version
echo ""
echo "1. Checking Python version..."
python --version

# Check dependencies
echo ""
echo "2. Checking dependencies..."
pip list | grep -E "ccxt|pandas|numpy|scikit-learn|xgboost"

# Test data collector
echo ""
echo "3. Testing Data Collector..."
python -c "
from utils.data_collector import DataCollector
import os
from dotenv import load_dotenv
load_dotenv()

try:
    collector = DataCollector(
        api_key=os.getenv('BITGET_API_KEY', 'test'),
        api_secret=os.getenv('BITGET_API_SECRET', 'test'),
        password=os.getenv('BITGET_PASSWORD', 'test'),
        testnet=True
    )
    print('✓ Data Collector initialized')
except Exception as e:
    print(f'✗ Data Collector error: {e}')
"

# Test feature engineering
echo ""
echo "4. Testing Feature Engineering..."
python -c "
from utils.feature_engineering import FeatureEngineer
import pandas as pd
import numpy as np

try:
    engineer = FeatureEngineer()
    
    # Create dummy data
    df = pd.DataFrame({
        'open': np.random.randn(100) + 100,
        'high': np.random.randn(100) + 101,
        'low': np.random.randn(100) + 99,
        'close': np.random.randn(100) + 100,
        'volume': np.random.randn(100) * 1000
    })
    
    result = engineer.extract_all_features(df)
    print(f'✓ Feature Engineering OK - {len(result.columns)} features extracted')
except Exception as e:
    print(f'✗ Feature Engineering error: {e}')
"

# Test risk manager
echo ""
echo "5. Testing Risk Manager..."
python -c "
from utils.risk_manager import RiskManager

try:
    config = {
        'initial_capital': 100,
        'leverage': 5,
        'risk_per_trade': 2,
        'max_loss_per_day': 10,
        'max_open_positions': 3,
        'stop_loss_percent': 2.0,
        'take_profit_percent': 4.0,
        'trailing_stop': False,
        'cooldown_period': 600,
        'confidence_threshold': 0.6
    }
    
    rm = RiskManager(config)
    print('✓ Risk Manager initialized')
    
    # Test position sizing
    size, value = rm.calculate_position_size(100, 98, 'long')
    print(f'✓ Position sizing: {size:.4f} units, ${value:.2f}')
except Exception as e:
    print(f'✗ Risk Manager error: {e}')
"

# Test trade executor (dry run)
echo ""
echo "6. Testing Trade Executor (Dry Run)..."
python -c "
from utils.trade_executor import TradeExecutor

try:
    executor = TradeExecutor(
        api_key='test',
        api_secret='test',
        password='test',
        testnet=True,
        dry_run=True
    )
    print('✓ Trade Executor initialized (dry run mode)')
except Exception as e:
    print(f'✗ Trade Executor error: {e}')
"

# Test logger
echo ""
echo "7. Testing Logger..."
python -c "
from utils.logger import setup_logger

try:
    logger = setup_logger('test_bot', level='INFO')
    logger.info('Test log message')
    print('✓ Logger initialized')
except Exception as e:
    print(f'✗ Logger error: {e}')
"

# Test config loading
echo ""
echo "8. Testing Config Loading..."
python -c "
import yaml

try:
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print('✓ Config loaded successfully')
    print(f'  - Trading pair: {config[\"trading\"][\"pair\"]}')
    print(f'  - Leverage: {config[\"trading\"][\"leverage\"]}x')
except Exception as e:
    print(f'✗ Config loading error: {e}')
"

# Check .env file
echo ""
echo "9. Checking .env file..."
if [ -f ".env" ]; then
    echo "✓ .env file exists"
    
    # Check if keys are set (not showing actual values)
    if grep -q "BITGET_API_KEY=" .env; then
        echo "✓ BITGET_API_KEY is set"
    else
        echo "✗ BITGET_API_KEY not set"
    fi
    
    if grep -q "BITGET_API_SECRET=" .env; then
        echo "✓ BITGET_API_SECRET is set"
    else
        echo "✗ BITGET_API_SECRET not set"
    fi
else
    echo "✗ .env file not found. Copy .env.example to .env"
fi

# Check for trained model
echo ""
echo "10. Checking for trained model..."
if ls model/*.pkl 1> /dev/null 2>&1; then
    echo "✓ Trained model found:"
    ls -lh model/*.pkl | tail -1
else
    echo "✗ No trained model found. Run: python model/train.py"
fi

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. If no errors above, you're ready to go!"
echo "2. Train model if not exists: python model/train.py"
echo "3. Test with dry run: python main.py --dry-run"
echo "4. Go live on testnet: python main.py"
echo ""
