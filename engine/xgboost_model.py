"""
XGBoost Model for price prediction
"""

import numpy as np
import xgboost as xgb
from typing import Optional
import logging
import pickle

logger = logging.getLogger(__name__)

class XGBoostPredictor:
    """
    XGBoost model wrapper for prediction.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize XGBoost predictor.
        
        Args:
            model_path: Path to saved model (optional)
        """
        self.model = None
        self.sequence_length = 100
        
        if model_path:
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"XGBoost model loaded from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load XGBoost model: {e}")
    
    def build(self):
        """Build new model."""
        self.model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        logger.info("XGBoost model initialized")
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray, y_val: np.ndarray):
        """
        Train the XGBoost model.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
        """
        try:
            if self.model is None:
                self.build()
            
            # Flatten the sequence data for XGBoost
            X_train_flat = X_train.reshape(X_train.shape[0], -1)
            X_val_flat = X_val.reshape(X_val.shape[0], -1)
            
            # Train for each output dimension
            self.models = []
            for i in range(y_train.shape[1]):
                model = xgb.XGBRegressor(
                    n_estimators=200,
                    max_depth=7,
                    learning_rate=0.1,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    n_jobs=-1
                )
                
                model.fit(
                    X_train_flat, y_train[:, i],
                    eval_set=[(X_val_flat, y_val[:, i])],
                    early_stopping_rounds=10,
                    verbose=False
                )
                
                self.models.append(model)
            
            logger.info("XGBoost models trained successfully")
        
        except Exception as e:
            logger.error(f"Error training XGBoost: {e}")
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input features (batch, sequence, features)
        
        Returns:
            Predictions array (batch, 30)
        """
        try:
            if not hasattr(self, 'models') or not self.models:
                logger.warning("XGBoost models not trained yet")
                return np.zeros((X.shape[0], 30))
            
            # Flatten input
            X_flat = X.reshape(X.shape[0], -1)
            
            # Predict for each output dimension
            predictions = []
            for model in self.models:
                pred = model.predict(X_flat)
                predictions.append(pred)
            
            # Stack predictions
            result = np.column_stack(predictions)
            return result
        
        except Exception as e:
            logger.error(f"Error in XGBoost prediction: {e}")
            return np.zeros((X.shape[0], 30))
    
    def save(self, path: str):
        """Save model to file."""
        try:
            if hasattr(self, 'models') and self.models:
                with open(path, 'wb') as f:
                    pickle.dump(self.models, f)
                logger.info(f"XGBoost models saved to {path}")
        except Exception as e:
            logger.error(f"Error saving XGBoost models: {e}")
