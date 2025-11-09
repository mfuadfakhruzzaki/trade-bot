"""
Feature Engineering Module
Extracts technical indicators and prepares features for AI model
"""

import pandas as pd
import numpy as np
import talib as ta
from typing import Dict, List, Optional
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class FeatureEngineer:
    """
    Handles feature extraction from OHLCV data
    - Technical indicators (MA, EMA, RSI, MACD, Bollinger Bands, etc.)
    - Volume indicators
    - Candlestick patterns
    - Data normalization and windowing
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize feature engineer
        
        Args:
            config: Configuration dict with indicator parameters
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or self._default_config()
        self.scaler = StandardScaler()
        
    def _default_config(self) -> Dict:
        """Default indicator configuration"""
        return {
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
    
    def add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Simple Moving Averages (SMA) and Exponential Moving Averages (EMA)
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with MA/EMA columns added
        """
        try:
            # Simple Moving Averages
            for period in self.config['ma_periods']:
                df[f'SMA_{period}'] = ta.SMA(df['close'], timeperiod=period)
            
            # Exponential Moving Averages
            for period in self.config['ema_periods']:
                df[f'EMA_{period}'] = ta.EMA(df['close'], timeperiod=period)
            
            # Price relative to MAs
            df['price_above_sma_7'] = (df['close'] > df['SMA_7']).astype(int)
            df['price_above_ema_25'] = (df['close'] > df['EMA_25']).astype(int)
            
            self.logger.debug("Added moving averages")
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding moving averages: {e}")
            raise
    
    def add_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Relative Strength Index (RSI)
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with RSI column added
        """
        try:
            period = self.config['rsi_period']
            df['RSI'] = ta.RSI(df['close'], timeperiod=period)
            
            # RSI zones
            df['RSI_oversold'] = (df['RSI'] < 30).astype(int)
            df['RSI_overbought'] = (df['RSI'] > 70).astype(int)
            
            self.logger.debug("Added RSI")
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding RSI: {e}")
            raise
    
    def add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with MACD columns added
        """
        try:
            macd, signal, hist = ta.MACD(
                df['close'],
                fastperiod=self.config['macd_fast'],
                slowperiod=self.config['macd_slow'],
                signalperiod=self.config['macd_signal']
            )
            
            df['MACD'] = macd
            df['MACD_signal'] = signal
            df['MACD_hist'] = hist
            
            # MACD crossovers
            df['MACD_bullish'] = ((df['MACD'] > df['MACD_signal']) & 
                                   (df['MACD'].shift(1) <= df['MACD_signal'].shift(1))).astype(int)
            df['MACD_bearish'] = ((df['MACD'] < df['MACD_signal']) & 
                                   (df['MACD'].shift(1) >= df['MACD_signal'].shift(1))).astype(int)
            
            self.logger.debug("Added MACD")
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding MACD: {e}")
            raise
    
    def add_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Bollinger Bands
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with Bollinger Bands columns added
        """
        try:
            upper, middle, lower = ta.BBANDS(
                df['close'],
                timeperiod=self.config['bb_period'],
                nbdevup=self.config['bb_std'],
                nbdevdn=self.config['bb_std']
            )
            
            df['BB_upper'] = upper
            df['BB_middle'] = middle
            df['BB_lower'] = lower
            df['BB_width'] = (upper - lower) / middle
            
            # Price position in BB
            df['BB_position'] = (df['close'] - lower) / (upper - lower)
            df['price_below_bb_lower'] = (df['close'] < lower).astype(int)
            df['price_above_bb_upper'] = (df['close'] > upper).astype(int)
            
            self.logger.debug("Added Bollinger Bands")
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding Bollinger Bands: {e}")
            raise
    
    def add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume-based indicators
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with volume indicators added
        """
        try:
            # Volume MA
            df['volume_MA'] = ta.SMA(df['volume'], timeperiod=self.config['volume_ma_period'])
            df['volume_ratio'] = df['volume'] / df['volume_MA']
            
            # OBV (On-Balance Volume)
            df['OBV'] = ta.OBV(df['close'], df['volume'])
            
            # Volume spike
            df['volume_spike'] = (df['volume'] > df['volume_MA'] * 2).astype(int)
            
            self.logger.debug("Added volume indicators")
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding volume indicators: {e}")
            raise
    
    def add_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add Average True Range (ATR) for volatility
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with ATR column added
        """
        try:
            df['ATR'] = ta.ATR(
                df['high'], 
                df['low'], 
                df['close'], 
                timeperiod=self.config['atr_period']
            )
            
            # ATR percentage
            df['ATR_pct'] = (df['ATR'] / df['close']) * 100
            
            self.logger.debug("Added ATR")
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding ATR: {e}")
            raise
    
    def add_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add candlestick pattern recognition
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with candlestick pattern columns added
        """
        try:
            # Bullish patterns
            df['pattern_hammer'] = ta.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])
            df['pattern_engulfing_bull'] = ta.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
            df['pattern_morning_star'] = ta.CDLMORNINGSTAR(df['open'], df['high'], df['low'], df['close'])
            
            # Bearish patterns
            df['pattern_shooting_star'] = ta.CDLSHOOTINGSTAR(df['open'], df['high'], df['low'], df['close'])
            df['pattern_engulfing_bear'] = ta.CDLEVENINGSTAR(df['open'], df['high'], df['low'], df['close'])
            
            # Doji (indecision)
            df['pattern_doji'] = ta.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
            
            # Normalize pattern values to 0/1/-1
            pattern_cols = [col for col in df.columns if col.startswith('pattern_')]
            for col in pattern_cols:
                df[col] = df[col] / 100  # TA-Lib returns -100, 0, or 100
            
            self.logger.debug("Added candlestick patterns")
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding candlestick patterns: {e}")
            raise
    
    def add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add momentum indicators
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with momentum indicators added
        """
        try:
            # Stochastic
            slowk, slowd = ta.STOCH(
                df['high'], 
                df['low'], 
                df['close'],
                fastk_period=14,
                slowk_period=3,
                slowd_period=3
            )
            df['STOCH_K'] = slowk
            df['STOCH_D'] = slowd
            
            # ADX (Average Directional Index)
            df['ADX'] = ta.ADX(df['high'], df['low'], df['close'], timeperiod=14)
            
            # CCI (Commodity Channel Index)
            df['CCI'] = ta.CCI(df['high'], df['low'], df['close'], timeperiod=20)
            
            # Williams %R
            df['WILLR'] = ta.WILLR(df['high'], df['low'], df['close'], timeperiod=14)
            
            self.logger.debug("Added momentum indicators")
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding momentum indicators: {e}")
            raise
    
    def add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add price-based features
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with price features added
        """
        try:
            # Price changes
            df['price_change'] = df['close'].pct_change()
            df['price_change_2'] = df['close'].pct_change(periods=2)
            df['price_change_5'] = df['close'].pct_change(periods=5)
            
            # High-Low range
            df['hl_range'] = (df['high'] - df['low']) / df['close']
            
            # Body size (open-close)
            df['body_size'] = abs(df['open'] - df['close']) / df['close']
            
            # Upper/lower shadows
            df['upper_shadow'] = (df['high'] - df[['open', 'close']].max(axis=1)) / df['close']
            df['lower_shadow'] = (df[['open', 'close']].min(axis=1) - df['low']) / df['close']
            
            # Gap
            df['gap'] = df['open'] - df['close'].shift(1)
            df['gap_pct'] = df['gap'] / df['close'].shift(1)
            
            self.logger.debug("Added price features")
            return df
            
        except Exception as e:
            self.logger.error(f"Error adding price features: {e}")
            raise
    
    def extract_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all technical indicators and features
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with all features added
        """
        try:
            self.logger.info("Extracting all features...")
            
            df = self.add_moving_averages(df)
            df = self.add_rsi(df)
            df = self.add_macd(df)
            df = self.add_bollinger_bands(df)
            df = self.add_volume_indicators(df)
            df = self.add_atr(df)
            df = self.add_candlestick_patterns(df)
            df = self.add_momentum_indicators(df)
            df = self.add_price_features(df)
            
            # Drop NaN rows (from indicator calculations)
            initial_rows = len(df)
            df = df.dropna()
            dropped_rows = initial_rows - len(df)
            
            self.logger.info(f"Feature extraction complete. Dropped {dropped_rows} NaN rows.")
            self.logger.info(f"Total features: {len(df.columns)}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error extracting features: {e}")
            raise
    
    def normalize_features(self, df: pd.DataFrame, feature_cols: List[str], 
                          method: str = 'standard') -> pd.DataFrame:
        """
        Normalize features for ML model
        
        Args:
            df: DataFrame with features
            feature_cols: List of column names to normalize
            method: 'standard' (StandardScaler) or 'minmax' (MinMaxScaler)
            
        Returns:
            DataFrame with normalized features
        """
        try:
            if method == 'standard':
                scaler = StandardScaler()
            elif method == 'minmax':
                scaler = MinMaxScaler()
            else:
                raise ValueError(f"Unknown normalization method: {method}")
            
            df[feature_cols] = scaler.fit_transform(df[feature_cols])
            
            self.logger.debug(f"Normalized features using {method} scaling")
            return df
            
        except Exception as e:
            self.logger.error(f"Error normalizing features: {e}")
            raise
    
    def create_windowed_dataset(self, df: pd.DataFrame, feature_cols: List[str], 
                               window_size: int = 20) -> tuple:
        """
        Create windowed dataset for time series models (e.g., LSTM)
        
        Args:
            df: DataFrame with features
            feature_cols: List of feature column names
            window_size: Number of timesteps to look back
            
        Returns:
            (X, y) tuple where X is (samples, timesteps, features) and y is target
        """
        try:
            X, y = [], []
            
            data = df[feature_cols].values
            
            for i in range(window_size, len(data)):
                X.append(data[i-window_size:i])
                # Target: 1 if price goes up, 0 if down
                y.append(1 if df['close'].iloc[i] > df['close'].iloc[i-1] else 0)
            
            X = np.array(X)
            y = np.array(y)
            
            self.logger.info(f"Created windowed dataset: X shape {X.shape}, y shape {y.shape}")
            return X, y
            
        except Exception as e:
            self.logger.error(f"Error creating windowed dataset: {e}")
            raise
    
    def get_feature_columns(self, df: pd.DataFrame, exclude_base: bool = True) -> List[str]:
        """
        Get list of feature column names (excluding OHLCV base columns)
        
        Args:
            df: DataFrame
            exclude_base: Exclude OHLCV base columns
            
        Returns:
            List of feature column names
        """
        base_cols = ['open', 'high', 'low', 'close', 'volume']
        
        if exclude_base:
            return [col for col in df.columns if col not in base_cols]
        else:
            return list(df.columns)


if __name__ == "__main__":
    # Test the feature engineer
    logging.basicConfig(level=logging.DEBUG)
    
    # Create sample data
    from utils.data_collector import DataCollector
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    collector = DataCollector(
        api_key=os.getenv('BITGET_API_KEY', ''),
        api_secret=os.getenv('BITGET_API_SECRET', ''),
        password=os.getenv('BITGET_PASSWORD', ''),
        testnet=True
    )
    
    df = collector.fetch_ohlcv('SOL/USDT:USDT', '5m', 500)
    
    # Extract features
    engineer = FeatureEngineer()
    df = engineer.extract_all_features(df)
    
    print("\nExtracted Features:")
    print(df.tail())
    print(f"\nTotal columns: {len(df.columns)}")
    print(f"Feature columns: {len(engineer.get_feature_columns(df))}")
