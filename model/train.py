"""
Model Training Pipeline
Handles data preparation, training, and model evaluation
"""

import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime
from typing import Dict, Optional
from sklearn.model_selection import train_test_split, TimeSeriesSplit
import joblib

from utils.data_collector import DataCollector
from utils.feature_engineering import FeatureEngineer
from model.ai_model import TradingModel, ModelEnsemble


class ModelTrainer:
    """
    Handles the complete training pipeline
    - Data collection
    - Feature extraction
    - Model training
    - Model evaluation
    - Model saving
    """
    
    def __init__(self, config: Dict):
        """
        Initialize model trainer
        
        Args:
            config: Configuration dict with training parameters
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize components
        self.data_collector = None
        self.feature_engineer = FeatureEngineer(config.get('indicators'))
        self.model = None
        
    def setup_data_collector(self, api_key: str, api_secret: str, password: str, testnet: bool = True):
        """Setup data collector with API credentials"""
        self.data_collector = DataCollector(api_key, api_secret, password, testnet)
        self.logger.info("Data collector initialized")
    
    def collect_training_data(self, symbol: str, timeframe: str, days: int) -> pd.DataFrame:
        """
        Collect historical data for training
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            days: Number of days to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            self.logger.info(f"Collecting {days} days of data for {symbol}...")
            df = self.data_collector.fetch_historical_data(symbol, timeframe, days)
            
            # Save raw data
            raw_data_path = f"data/raw_data_{symbol.replace('/', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(raw_data_path)
            self.logger.info(f"Raw data saved to {raw_data_path}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error collecting training data: {e}")
            raise
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all features from raw data
        
        Args:
            df: Raw OHLCV DataFrame
            
        Returns:
            DataFrame with features
        """
        try:
            self.logger.info("Extracting features...")
            df = self.feature_engineer.extract_all_features(df)
            
            # Save processed data
            processed_data_path = f"data/processed_data_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(processed_data_path)
            self.logger.info(f"Processed data saved to {processed_data_path}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error preparing features: {e}")
            raise
    
    def prepare_labels(self, df: pd.DataFrame, method: str = 'binary', 
                      future_bars: int = 1) -> pd.Series:
        """
        Prepare target labels
        
        Args:
            df: DataFrame with features
            method: Label generation method
            future_bars: Bars ahead to predict
            
        Returns:
            Series with labels
        """
        try:
            # Initialize temporary model just for label preparation
            temp_model = TradingModel(self.config.get('model_type', 'xgboost'))
            labels = temp_model.prepare_labels(df, method, future_bars)
            
            self.logger.info(f"Labels prepared. Distribution: {labels.value_counts().to_dict()}")
            return labels
            
        except Exception as e:
            self.logger.error(f"Error preparing labels: {e}")
            raise
    
    def split_data(self, X: pd.DataFrame, y: pd.Series, 
                   test_size: float = 0.2, validation_size: float = 0.1) -> tuple:
        """
        Split data into train, validation, and test sets
        Uses time-based split (no shuffle) to prevent look-ahead bias
        
        Args:
            X: Features
            y: Labels
            test_size: Test set proportion
            validation_size: Validation set proportion
            
        Returns:
            (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        try:
            # Calculate split indices
            n = len(X)
            test_idx = int(n * (1 - test_size))
            val_idx = int(test_idx * (1 - validation_size))
            
            # Split without shuffling (time series)
            X_train = X.iloc[:val_idx]
            y_train = y.iloc[:val_idx]
            
            X_val = X.iloc[val_idx:test_idx]
            y_val = y.iloc[val_idx:test_idx]
            
            X_test = X.iloc[test_idx:]
            y_test = y.iloc[test_idx:]
            
            self.logger.info(f"Data split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
            
            return X_train, X_val, X_test, y_train, y_val, y_test
            
        except Exception as e:
            self.logger.error(f"Error splitting data: {e}")
            raise
    
    def train_model(self, X_train: pd.DataFrame, y_train: pd.Series, 
                   X_val: Optional[pd.DataFrame] = None, 
                   y_val: Optional[pd.Series] = None) -> Dict:
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
            
        Returns:
            Training results dict
        """
        try:
            model_type = self.config.get('model_type', 'xgboost')
            self.logger.info(f"Training {model_type} model...")
            
            # Initialize model
            self.model = TradingModel(model_type, self.config.get('model_config'))
            
            # Train
            train_metrics = self.model.train(X_train, y_train)
            
            results = {
                'model_type': model_type,
                'train_metrics': train_metrics,
                'feature_importance': self.model.get_feature_importance().to_dict()
            }
            
            # Validate if validation set provided
            if X_val is not None and y_val is not None:
                val_metrics = self.model.evaluate(X_val, y_val)
                results['val_metrics'] = val_metrics
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            raise
    
    def evaluate_model(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """
        Evaluate trained model on test set
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Evaluation metrics dict
        """
        try:
            if self.model is None:
                raise ValueError("No model trained yet")
            
            metrics = self.model.evaluate(X_test, y_test)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            raise
    
    def save_model(self, filepath: Optional[str] = None):
        """
        Save trained model
        
        Args:
            filepath: Path to save model (auto-generated if None)
        """
        try:
            if self.model is None:
                raise ValueError("No model trained yet")
            
            if filepath is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = f"model/{self.config.get('model_type', 'model')}_{timestamp}.pkl"
            
            self.model.save_model(filepath)
            
            # Also save feature columns
            feature_cols_path = filepath.replace('.pkl', '_features.txt')
            with open(feature_cols_path, 'w') as f:
                for col in self.model.feature_importance['feature']:
                    f.write(f"{col}\n")
            
            self.logger.info(f"Model and features saved")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            raise
    
    def run_full_pipeline(self, symbol: str, timeframe: str, days: int) -> Dict:
        """
        Run complete training pipeline
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            days: Days of historical data
            
        Returns:
            Complete results dict
        """
        try:
            self.logger.info("=" * 50)
            self.logger.info("Starting Full Training Pipeline")
            self.logger.info("=" * 50)
            
            # 1. Collect data
            df = self.collect_training_data(symbol, timeframe, days)
            
            # 2. Extract features
            df = self.prepare_features(df)
            
            # 3. Prepare labels
            labels = self.prepare_labels(
                df, 
                method=self.config.get('label_method', 'binary'),
                future_bars=self.config.get('future_bars', 1)
            )
            
            # 4. Get feature columns
            feature_cols = self.feature_engineer.get_feature_columns(df)
            X = df[feature_cols].iloc[:-self.config.get('future_bars', 1)]
            y = labels
            
            # Align X and y
            X = X.loc[y.index]
            
            # 5. Split data
            X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(X, y)
            
            # 6. Train model
            train_results = self.train_model(X_train, y_train, X_val, y_val)
            
            # 7. Evaluate on test set
            test_metrics = self.evaluate_model(X_test, y_test)
            train_results['test_metrics'] = test_metrics
            
            # 8. Save model
            model_path = self.save_model()
            train_results['model_path'] = model_path
            
            self.logger.info("=" * 50)
            self.logger.info("Training Pipeline Complete!")
            self.logger.info(f"Test Accuracy: {test_metrics['accuracy']:.4f}")
            self.logger.info(f"Model saved to: {model_path}")
            self.logger.info("=" * 50)
            
            return train_results
            
        except Exception as e:
            self.logger.error(f"Error in training pipeline: {e}")
            raise


def main():
    """Main training script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Training configuration
    config = {
        'model_type': 'xgboost',
        'label_method': 'binary',
        'future_bars': 1,
        'indicators': {
            'ma_periods': [7, 25, 99],
            'ema_periods': [7, 25],
            'rsi_period': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb_period': 20,
            'bb_std': 2,
            'volume_ma_period': 20,
            'atr_period': 14
        }
    }
    
    # Initialize trainer
    trainer = ModelTrainer(config)
    
    # Setup data collector
    trainer.setup_data_collector(
        api_key=os.getenv('BITGET_API_KEY', ''),
        api_secret=os.getenv('BITGET_API_SECRET', ''),
        password=os.getenv('BITGET_PASSWORD', ''),
        testnet=True
    )
    
    # Run training pipeline
    results = trainer.run_full_pipeline(
        symbol='SOL/USDT:USDT',
        timeframe='5m',
        days=30
    )
    
    print("\n" + "=" * 50)
    print("TRAINING RESULTS")
    print("=" * 50)
    print(f"Model Type: {results['model_type']}")
    print(f"\nTrain Metrics: {results['train_metrics']}")
    print(f"\nValidation Metrics: {results.get('val_metrics', 'N/A')}")
    print(f"\nTest Metrics: {results['test_metrics']}")
    print(f"\nModel saved to: {results['model_path']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
