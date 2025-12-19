"""
Transformer Model for price prediction
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class TransformerBlock(keras.layers.Layer):
    """
    Transformer block with multi-head attention.
    """
    
    def __init__(self, embed_dim: int, num_heads: int, ff_dim: int, rate: float = 0.1):
        super(TransformerBlock, self).__init__()
        self.att = keras.layers.MultiHeadAttention(
            num_heads=num_heads, 
            key_dim=embed_dim
        )
        self.ffn = keras.Sequential([
            keras.layers.Dense(ff_dim, activation="relu"),
            keras.layers.Dense(embed_dim),
        ])
        self.layernorm1 = keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = keras.layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = keras.layers.Dropout(rate)
        self.dropout2 = keras.layers.Dropout(rate)
    
    def call(self, inputs, training=False):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)

def build_transformer_model(input_shape: Tuple[int, int]) -> keras.Model:
    """
    Build Transformer model for time series prediction.
    
    Args:
        input_shape: (sequence_length, features)
    
    Returns:
        Compiled Keras model
    """
    try:
        inputs = keras.Input(shape=input_shape)
        
        # Positional encoding
        x = keras.layers.Dense(64)(inputs)
        
        # Transformer blocks
        x = TransformerBlock(64, 4, 128)(x)
        x = TransformerBlock(64, 4, 128)(x)
        
        # Global average pooling
        x = keras.layers.GlobalAveragePooling1D()(x)
        
        # Output layers
        x = keras.layers.Dense(128, activation='relu')(x)
        x = keras.layers.Dropout(0.2)(x)
        x = keras.layers.Dense(64, activation='relu')(x)
        outputs = keras.layers.Dense(30)(x)  # 30 candle predictions
        
        model = keras.Model(inputs=inputs, outputs=outputs)
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        logger.info("Transformer model built successfully")
        return model
    
    except Exception as e:
        logger.error(f"Error building Transformer model: {e}")
        raise

class TransformerPredictor:
    """
    Transformer model wrapper for prediction.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize Transformer predictor.
        
        Args:
            model_path: Path to saved model (optional)
        """
        self.model = None
        self.sequence_length = 100
        
        if model_path:
            try:
                self.model = keras.models.load_model(
                    model_path,
                    custom_objects={'TransformerBlock': TransformerBlock}
                )
                logger.info(f"Transformer model loaded from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load Transformer model: {e}")
    
    def build(self, input_shape: Tuple[int, int]):
        """Build new model."""
        self.model = build_transformer_model(input_shape)
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray, y_val: np.ndarray,
              epochs: int = 50, batch_size: int = 32):
        """
        Train the Transformer model.
        
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
            
            logger.info("Transformer model trained successfully")
            return history
        
        except Exception as e:
            logger.error(f"Error training Transformer: {e}")
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
            logger.error(f"Error in Transformer prediction: {e}")
            return np.zeros((X.shape[0], 30))
    
    def save(self, path: str):
        """Save model to file."""
        try:
            if self.model:
                self.model.save(path)
                logger.info(f"Transformer model saved to {path}")
        except Exception as e:
            logger.error(f"Error saving Transformer model: {e}")
