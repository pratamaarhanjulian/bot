"""
Data preprocessor with feature engineering
"""

import logging
import numpy as np
import pandas as pd
from typing import Tuple
import ta  # Technical Analysis library

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    Preprocess data and engineer features for ML models.
    """
    
    def __init__(self):
        """Initialize data preprocessor."""
        self.sequence_length = 100
        self.prediction_horizon = 30
        logger.info("Data Preprocessor initialized")
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to dataframe.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added indicators
        """
        try:
            df = df.copy()
            
            # RSI
            df['rsi'] = ta.momentum.RSIIndicator(
                close=df['close'], window=14
            ).rsi()
            
            # MACD
            macd = ta.trend.MACD(close=df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_diff'] = macd.macd_diff()
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(close=df['close'])
            df['bb_high'] = bb.bollinger_hband()
            df['bb_mid'] = bb.bollinger_mavg()
            df['bb_low'] = bb.bollinger_lband()
            df['bb_width'] = bb.bollinger_wband()
            
            # ATR
            df['atr'] = ta.volatility.AverageTrueRange(
                high=df['high'], low=df['low'], close=df['close']
            ).average_true_range()
            
            # EMAs
            df['ema_20'] = ta.trend.EMAIndicator(
                close=df['close'], window=20
            ).ema_indicator()
            df['ema_50'] = ta.trend.EMAIndicator(
                close=df['close'], window=50
            ).ema_indicator()
            df['ema_200'] = ta.trend.EMAIndicator(
                close=df['close'], window=200
            ).ema_indicator()
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price changes
            df['price_change'] = df['close'].pct_change()
            df['high_low_range'] = (df['high'] - df['low']) / df['close']
            
            # Fill NaN values
            df = df.fillna(method='bfill').fillna(method='ffill')
            
            logger.info(f"Added {len(df.columns) - 6} technical indicators")
            
            return df
        
        except Exception as e:
            logger.error(f"Error adding technical indicators: {e}")
            return df
    
    def create_sequences(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for training.
        
        Args:
            df: DataFrame with features
        
        Returns:
            X (features), y (targets)
        """
        try:
            # Select feature columns
            feature_cols = [col for col in df.columns if col != 'timestamp']
            data = df[feature_cols].values
            
            X, y = [], []
            
            for i in range(len(data) - self.sequence_length - self.prediction_horizon):
                # Input sequence
                X.append(data[i:i + self.sequence_length])
                
                # Target: next 30 closing prices
                future_closes = data[i + self.sequence_length:
                                    i + self.sequence_length + self.prediction_horizon, 3]
                y.append(future_closes)
            
            X = np.array(X, dtype=np.float32)
            y = np.array(y, dtype=np.float32)
            
            logger.info(f"Created {len(X)} sequences with shape {X.shape}")
            
            return X, y
        
        except Exception as e:
            logger.error(f"Error creating sequences: {e}")
            return np.array([]), np.array([])
    
    def normalize_data(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Normalize features.
        
        Args:
            X: Feature array
            y: Target array
        
        Returns:
            Normalized X, y
        """
        try:
            # Normalize X (per feature)
            X_norm = np.zeros_like(X)
            
            for i in range(X.shape[2]):  # For each feature
                feature = X[:, :, i]
                mean = np.mean(feature)
                std = np.std(feature)
                
                if std > 0:
                    X_norm[:, :, i] = (feature - mean) / std
                else:
                    X_norm[:, :, i] = feature - mean
            
            # Normalize y (closing prices)
            y_mean = np.mean(y)
            y_std = np.std(y)
            
            if y_std > 0:
                y_norm = (y - y_mean) / y_std
            else:
                y_norm = y - y_mean
            
            logger.info("Data normalized")
            
            return X_norm, y_norm
        
        except Exception as e:
            logger.error(f"Error normalizing data: {e}")
            return X, y
    
    def split_data(self, X: np.ndarray, y: np.ndarray,
                   train_ratio: float = 0.8) -> Tuple:
        """
        Split data into train and validation sets.
        
        Args:
            X: Features
            y: Targets
            train_ratio: Ratio of training data
        
        Returns:
            X_train, X_val, y_train, y_val
        """
        try:
            split_idx = int(len(X) * train_ratio)
            
            X_train = X[:split_idx]
            X_val = X[split_idx:]
            y_train = y[:split_idx]
            y_val = y[split_idx:]
            
            logger.info(f"Split: {len(X_train)} train, {len(X_val)} validation")
            
            return X_train, X_val, y_train, y_val
        
        except Exception as e:
            logger.error(f"Error splitting data: {e}")
            return X, np.array([]), y, np.array([])
    
    def preprocess_pipeline(self, df: pd.DataFrame) -> Tuple:
        """
        Complete preprocessing pipeline.
        
        Args:
            df: Raw OHLCV DataFrame
        
        Returns:
            X_train, X_val, y_train, y_val
        """
        try:
            # Add indicators
            df = self.add_technical_indicators(df)
            
            # Create sequences
            X, y = self.create_sequences(df)
            
            # Normalize
            X, y = self.normalize_data(X, y)
            
            # Split
            X_train, X_val, y_train, y_val = self.split_data(X, y)
            
            logger.info("✅ Preprocessing pipeline complete")
            
            return X_train, X_val, y_train, y_val
        
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {e}")
            return None, None, None, None
