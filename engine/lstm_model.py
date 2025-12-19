"""
LSTM Model for price prediction
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

def build_lstm_model(input_shape: Tuple[int, int]) -> keras.Model:
    """
    Build LSTM model for time series prediction.
    
    Args:
        input_shape: (sequence_length, features)
    
    Returns:
        Compiled Keras model
    """
    try:
        model = keras.Sequential([
            keras.layers.LSTM(128, return_sequences=True, input_shape=input_shape),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(64, return_sequences=True),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(32),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(30)  # 30 candle predictions
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        logger.info("LSTM model built successfully")
        return model
    
    except Exception as e:
        logger.error(f"Error building LSTM model: {e}")
        raise

class LSTMPredictor:
    """
    LSTM model wrapper for prediction.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize LSTM predictor.
        
        Args:
            model_path: Path to saved model (optional)
        """
        self.model = None
        self.sequence_length = 100
        
        if model_path:
            try:
                self.model = keras.models.load_model(model_path)
                logger.info(f"LSTM model loaded from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load LSTM model: {e}")
    
    def build(self, input_shape: Tuple[int, int]):
        """Build new model."""
        self.model = build_lstm_model(input_shape)
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray, y_val: np.ndarray,
              epochs: int = 50, batch_size: int = 32):
        """
        Train the LSTM model.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            epochs: Number of epochs
            batch_size: Batch size
        """
        try:
            if self.model is None:
                self.build((X_train.shape[1], X_train.shape[2]))
            
            early_stopping = keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            )
            
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=[early_stopping],
                verbose=0
            )
            
            logger.info("LSTM model trained successfully")
            return history
        
        except Exception as e:
            logger.error(f"Error training LSTM: {e}")
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input features
        
        Returns:
            Predictions array
        """
        try:
            if self.model is None:
                raise ValueError("Model not initialized")
            
            predictions = self.model.predict(X, verbose=0)
            return predictions
        
        except Exception as e:
            logger.error(f"Error in LSTM prediction: {e}")
            return np.zeros((X.shape[0], 30))
    
    def save(self, path: str):
        """Save model to file."""
        try:
            if self.model:
                self.model.save(path)
                logger.info(f"LSTM model saved to {path}")
        except Exception as e:
            logger.error(f"Error saving LSTM model: {e}")
