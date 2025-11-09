"""
AI Model Module
Machine learning models for trading signal prediction
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple, Optional
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import xgboost as xgb


class TradingModel:
    """
    Base class for trading AI models
    Supports multiple model types: Logistic Regression, Random Forest, XGBoost
    """
    
    def __init__(self, model_type: str = 'xgboost', config: Optional[Dict] = None):
        """
        Initialize trading model
        
        Args:
            model_type: 'logistic', 'random_forest', or 'xgboost'
            config: Model configuration parameters
        """
        self.logger = logging.getLogger(__name__)
        self.model_type = model_type
        self.config = config or self._default_config()
        self.model = None
        self.feature_importance = None
        
        self._init_model()
    
    def _default_config(self) -> Dict:
        """Default model configurations"""
        return {
            'logistic': {
                'C': 1.0,
                'max_iter': 1000,
                'random_state': 42
            },
            'random_forest': {
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42,
                'n_jobs': -1
            },
            'xgboost': {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1,
                'objective': 'binary:logistic',
                'random_state': 42,
                'n_jobs': -1
            }
        }
    
    def _init_model(self):
        """Initialize the selected model"""
        try:
            config = self.config.get(self.model_type, {})
            
            if self.model_type == 'logistic':
                self.model = LogisticRegression(**config)
                self.logger.info("Initialized Logistic Regression model")
                
            elif self.model_type == 'random_forest':
                self.model = RandomForestClassifier(**config)
                self.logger.info("Initialized Random Forest model")
                
            elif self.model_type == 'xgboost':
                self.model = xgb.XGBClassifier(**config)
                self.logger.info("Initialized XGBoost model")
                
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")
                
        except Exception as e:
            self.logger.error(f"Error initializing model: {e}")
            raise
    
    def prepare_labels(self, df: pd.DataFrame, method: str = 'binary', 
                      future_bars: int = 1, threshold: float = 0.001) -> pd.Series:
        """
        Prepare target labels for training
        
        Args:
            df: DataFrame with price data
            method: 'binary' (up/down) or 'ternary' (buy/sell/hold)
            future_bars: How many bars ahead to predict
            threshold: Minimum price change to consider (for ternary)
            
        Returns:
            Series with labels (0, 1) or (0, 1, 2)
        """
        try:
            future_price = df['close'].shift(-future_bars)
            price_change = (future_price - df['close']) / df['close']
            
            if method == 'binary':
                # 0: down, 1: up
                labels = (price_change > 0).astype(int)
                
            elif method == 'ternary':
                # 0: sell (down), 1: hold (neutral), 2: buy (up)
                labels = pd.Series(1, index=df.index)  # Default: hold
                labels[price_change > threshold] = 2  # Buy
                labels[price_change < -threshold] = 0  # Sell
                
            else:
                raise ValueError(f"Unknown label method: {method}")
            
            # Remove last bars (no future data)
            labels = labels[:-future_bars]
            
            self.logger.debug(f"Prepared {method} labels: {labels.value_counts().to_dict()}")
            return labels
            
        except Exception as e:
            self.logger.error(f"Error preparing labels: {e}")
            raise
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> Dict:
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training labels
            
        Returns:
            Training metrics dict
        """
        try:
            self.logger.info(f"Training {self.model_type} model...")
            self.logger.info(f"Training data shape: X={X_train.shape}, y={y_train.shape}")
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Get predictions
            y_pred = self.model.predict(X_train)
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_train, y_pred),
                'precision': precision_score(y_train, y_pred, average='weighted', zero_division=0),
                'recall': recall_score(y_train, y_pred, average='weighted', zero_division=0),
                'f1': f1_score(y_train, y_pred, average='weighted', zero_division=0)
            }
            
            # Feature importance
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importance = pd.DataFrame({
                    'feature': X_train.columns,
                    'importance': self.model.feature_importances_
                }).sort_values('importance', ascending=False)
            
            self.logger.info(f"Training complete. Metrics: {metrics}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            raise
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """
        Evaluate model on test data
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Evaluation metrics dict
        """
        try:
            self.logger.info("Evaluating model...")
            
            y_pred = self.model.predict(X_test)
            
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
                'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
                'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0)
            }
            
            self.logger.info(f"Evaluation metrics: {metrics}")
            self.logger.info("\nClassification Report:")
            self.logger.info("\n" + classification_report(y_test, y_pred, zero_division=0))
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> int:
        """
        Make prediction for single sample
        
        Args:
            X: Features (single row or DataFrame)
            
        Returns:
            Predicted class (0 or 1 or 2)
        """
        try:
            if isinstance(X, pd.Series):
                X = X.to_frame().T
            
            prediction = self.model.predict(X)[0]
            return int(prediction)
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            raise
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get prediction probabilities (confidence scores)
        
        Args:
            X: Features (single row or DataFrame)
            
        Returns:
            Array of probabilities for each class
        """
        try:
            if isinstance(X, pd.Series):
                X = X.to_frame().T
            
            probas = self.model.predict_proba(X)[0]
            return probas
            
        except Exception as e:
            self.logger.error(f"Error getting prediction probabilities: {e}")
            raise
    
    def get_signal(self, X: pd.DataFrame, confidence_threshold: float = 0.6) -> Dict:
        """
        Get trading signal with confidence score
        
        Args:
            X: Features
            confidence_threshold: Minimum confidence to generate signal
            
        Returns:
            Dict with signal, confidence, and probabilities
        """
        try:
            probas = self.predict_proba(X)
            prediction = self.predict(X)
            confidence = probas[prediction]
            
            # Map prediction to signal
            if prediction == 1:
                signal = 'BUY' if confidence >= confidence_threshold else 'HOLD'
            elif prediction == 0:
                signal = 'SELL' if confidence >= confidence_threshold else 'HOLD'
            elif prediction == 2:  # Ternary classification
                signal = 'BUY'
            else:
                signal = 'HOLD'
            
            return {
                'signal': signal,
                'confidence': float(confidence),
                'probabilities': probas.tolist(),
                'prediction': int(prediction)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting signal: {e}")
            raise
    
    def save_model(self, filepath: str):
        """
        Save trained model to file
        
        Args:
            filepath: Path to save model
        """
        try:
            joblib.dump(self.model, filepath)
            self.logger.info(f"Model saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            raise
    
    def load_model(self, filepath: str):
        """
        Load trained model from file
        
        Args:
            filepath: Path to load model from
        """
        try:
            self.model = joblib.load(filepath)
            self.logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            raise
    
    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get top N most important features
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            DataFrame with feature importance
        """
        if self.feature_importance is not None:
            return self.feature_importance.head(top_n)
        else:
            self.logger.warning("Feature importance not available for this model")
            return pd.DataFrame()


class ModelEnsemble:
    """
    Ensemble of multiple models for more robust predictions
    """
    
    def __init__(self, model_types: list = ['random_forest', 'xgboost']):
        """
        Initialize ensemble
        
        Args:
            model_types: List of model types to use
        """
        self.logger = logging.getLogger(__name__)
        self.models = {}
        
        for model_type in model_types:
            self.models[model_type] = TradingModel(model_type)
        
        self.logger.info(f"Initialized ensemble with {len(self.models)} models")
    
    def train_all(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train all models in ensemble"""
        results = {}
        for name, model in self.models.items():
            self.logger.info(f"Training {name}...")
            results[name] = model.train(X_train, y_train)
        return results
    
    def predict(self, X: pd.DataFrame, method: str = 'majority') -> int:
        """
        Get ensemble prediction
        
        Args:
            X: Features
            method: 'majority' (voting) or 'average' (average probabilities)
            
        Returns:
            Ensemble prediction
        """
        if method == 'majority':
            # Majority voting
            predictions = [model.predict(X) for model in self.models.values()]
            return int(np.bincount(predictions).argmax())
            
        elif method == 'average':
            # Average probabilities
            probas = [model.predict_proba(X) for model in self.models.values()]
            avg_probas = np.mean(probas, axis=0)
            return int(avg_probas.argmax())
    
    def get_signal(self, X: pd.DataFrame, confidence_threshold: float = 0.6) -> Dict:
        """Get ensemble trading signal"""
        signals = [model.get_signal(X, confidence_threshold) for model in self.models.values()]
        
        # Average confidence
        avg_confidence = np.mean([s['confidence'] for s in signals])
        
        # Majority signal
        signal_counts = pd.Series([s['signal'] for s in signals]).value_counts()
        majority_signal = signal_counts.index[0]
        
        return {
            'signal': majority_signal,
            'confidence': float(avg_confidence),
            'individual_signals': signals
        }


if __name__ == "__main__":
    # Test the model
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data
    from utils.data_collector import DataCollector
    from utils.feature_engineering import FeatureEngineer
    import os
    from dotenv import load_dotenv
    from sklearn.model_selection import train_test_split
    
    load_dotenv()
    
    # Collect data
    collector = DataCollector(
        api_key=os.getenv('BITGET_API_KEY', ''),
        api_secret=os.getenv('BITGET_API_SECRET', ''),
        password=os.getenv('BITGET_PASSWORD', ''),
        testnet=True
    )
    
    df = collector.fetch_ohlcv('SOL/USDT:USDT', '5m', 1000)
    
    # Extract features
    engineer = FeatureEngineer()
    df = engineer.extract_all_features(df)
    
    # Prepare data
    model = TradingModel('xgboost')
    labels = model.prepare_labels(df, method='binary')
    
    # Get feature columns
    feature_cols = engineer.get_feature_columns(df)
    X = df[feature_cols].iloc[:-1]  # Remove last row (no label)
    y = labels
    
    # Align X and y
    X = X.loc[y.index]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    
    # Train model
    train_metrics = model.train(X_train, y_train)
    
    # Evaluate
    test_metrics = model.evaluate(X_test, y_test)
    
    # Test prediction
    signal = model.get_signal(X_test.iloc[-1:], confidence_threshold=0.6)
    print(f"\nSignal: {signal}")
    
    # Feature importance
    print("\nTop 10 Features:")
    print(model.get_feature_importance(10))
