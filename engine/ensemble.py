"""
Ensemble Predictor combining 6 AI models
"""

import numpy as np
import os
import logging
from typing import Dict, Tuple, Optional

from .lstm_model import LSTMPredictor
from .transformer_model import TransformerPredictor
from .cnn_lstm_model import CNNLSTMPredictor
from .xgboost_model import XGBoostPredictor
from .dqn_agent import DQNAgent
from .ppo_agent import PPOAgent

logger = logging.getLogger(__name__)

class EnsemblePredictor:
    """
    Ensemble predictor combining 6 AI models with weighted averaging.
    
    Model weights:
    - LSTM: 25%
    - Transformer: 20%
    - CNN-LSTM: 20%
    - XGBoost: 15%
    - DQN: 10%
    - PPO: 10%
    
    CRITICAL: Only trades if confidence >= 85%
    """
    
    def __init__(self, models_dir: str = 'models'):
        """
        Initialize ensemble predictor.
        
        Args:
            models_dir: Directory containing saved models
        """
        self.models_dir = models_dir
        
        # Model weights (must sum to 1.0)
        self.weights = {
            'lstm': 0.25,
            'transformer': 0.20,
            'cnn_lstm': 0.20,
            'xgboost': 0.15,
            'dqn': 0.10,
            'ppo': 0.10
        }
        
        # Confidence threshold
        self.min_confidence = 85.0
        
        # Initialize models
        self.models = {}
        self._load_models()
    
    def _load_models(self):
        """Load all models if they exist."""
        try:
            # LSTM
            lstm_path = os.path.join(self.models_dir, 'lstm_model.h5')
            self.models['lstm'] = LSTMPredictor(
                lstm_path if os.path.exists(lstm_path) else None
            )
            
            # Transformer
            transformer_path = os.path.join(self.models_dir, 'transformer_model.h5')
            self.models['transformer'] = TransformerPredictor(
                transformer_path if os.path.exists(transformer_path) else None
            )
            
            # CNN-LSTM
            cnn_lstm_path = os.path.join(self.models_dir, 'cnn_lstm_model.h5')
            self.models['cnn_lstm'] = CNNLSTMPredictor(
                cnn_lstm_path if os.path.exists(cnn_lstm_path) else None
            )
            
            # XGBoost
            xgb_path = os.path.join(self.models_dir, 'xgboost_model.pkl')
            self.models['xgboost'] = XGBoostPredictor(
                xgb_path if os.path.exists(xgb_path) else None
            )
            
            # DQN
            dqn_path = os.path.join(self.models_dir, 'dqn_model.h5')
            state_size = 100 * 10  # sequence_length * features
            self.models['dqn'] = DQNAgent(
                state_size=state_size,
                model_path=dqn_path if os.path.exists(dqn_path) else None
            )
            
            # PPO
            ppo_path = os.path.join(self.models_dir, 'ppo_model.zip')
            self.models['ppo'] = PPOAgent(
                ppo_path if os.path.exists(ppo_path) else None
            )
            
            logger.info("All models initialized successfully")
        
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def predict(self, X: np.ndarray, return_details: bool = False) -> Tuple[np.ndarray, float, Optional[Dict]]:
        """
        Make ensemble prediction.
        
        Args:
            X: Input features (batch, sequence, features)
            return_details: If True, return individual model predictions
        
        Returns:
            predictions: Ensemble predictions (batch, 30)
            confidence: Prediction confidence (0-100)
            details: Individual model predictions (if return_details=True)
        """
        try:
            individual_predictions = {}
            
            # Get predictions from each model
            logger.debug("Getting LSTM prediction...")
            individual_predictions['lstm'] = self.models['lstm'].predict(X)
            
            logger.debug("Getting Transformer prediction...")
            individual_predictions['transformer'] = self.models['transformer'].predict(X)
            
            logger.debug("Getting CNN-LSTM prediction...")
            individual_predictions['cnn_lstm'] = self.models['cnn_lstm'].predict(X)
            
            logger.debug("Getting XGBoost prediction...")
            individual_predictions['xgboost'] = self.models['xgboost'].predict(X)
            
            logger.debug("Getting DQN prediction...")
            individual_predictions['dqn'] = self.models['dqn'].predict(X)
            
            logger.debug("Getting PPO prediction...")
            individual_predictions['ppo'] = self.models['ppo'].predict(X)
            
            # Calculate weighted ensemble prediction
            ensemble_pred = np.zeros_like(individual_predictions['lstm'])
            
            for model_name, predictions in individual_predictions.items():
                weight = self.weights[model_name]
                ensemble_pred += weight * predictions
            
            # Calculate confidence
            confidence = self._calculate_confidence(individual_predictions)
            
            logger.info(f"Ensemble prediction confidence: {confidence:.2f}%")
            
            if return_details:
                details = {
                    'individual': individual_predictions,
                    'weights': self.weights
                }
                return ensemble_pred, confidence, details
            
            return ensemble_pred, confidence, None
        
        except Exception as e:
            logger.error(f"Error in ensemble prediction: {e}")
            return np.zeros((X.shape[0], 30)), 0.0, None
    
    def _calculate_confidence(self, predictions: Dict[str, np.ndarray]) -> float:
        """
        Calculate prediction confidence based on model agreement.
        
        Args:
            predictions: Dictionary of model predictions
        
        Returns:
            Confidence score (0-100)
        """
        try:
            # Calculate variance among predictions
            all_preds = np.array(list(predictions.values()))
            
            # Calculate coefficient of variation (lower is better)
            mean_pred = np.mean(all_preds, axis=0)
            std_pred = np.std(all_preds, axis=0)
            
            # Avoid division by zero
            cv = np.divide(std_pred, np.abs(mean_pred) + 1e-8)
            
            # Convert to confidence (lower variance = higher confidence)
            # Normalize to 0-100 scale
            avg_cv = np.mean(cv)
            confidence = max(0, min(100, 100 - (avg_cv * 100)))
            
            return float(confidence)
        
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.0
    
    def should_trade(self, confidence: float) -> bool:
        """
        Check if confidence meets minimum threshold.
        
        Args:
            confidence: Prediction confidence
        
        Returns:
            True if should trade, False otherwise
        """
        return confidence >= self.min_confidence
    
    def get_signal(self, X: np.ndarray) -> Dict:
        """
        Get trading signal with confidence check.
        
        Args:
            X: Input features
        
        Returns:
            Dictionary with signal information
        """
        try:
            # Get ensemble prediction
            predictions, confidence, _ = self.predict(X, return_details=False)
            
            # Check confidence threshold
            if not self.should_trade(confidence):
                return {
                    'action': None,
                    'predictions': predictions[0].tolist(),
                    'confidence': confidence,
                    'message': f'Confidence too low: {confidence:.2f}% < {self.min_confidence}%'
                }
            
            # Determine action based on prediction trend
            pred_first = predictions[0][0]
            pred_last = predictions[0][-1]
            pred_change = (pred_last - pred_first) / pred_first * 100
            
            if pred_change > 0.1:  # Bullish
                action = 'BUY'
            elif pred_change < -0.1:  # Bearish
                action = 'SELL'
            else:
                action = None
            
            return {
                'action': action,
                'predictions': predictions[0].tolist(),
                'confidence': confidence,
                'pred_change': pred_change,
                'message': 'Signal generated' if action else 'No clear signal'
            }
        
        except Exception as e:
            logger.error(f"Error getting signal: {e}")
            return {
                'action': None,
                'predictions': [],
                'confidence': 0.0,
                'message': f'Error: {str(e)}'
            }
    
    def save_all_models(self):
        """Save all models to disk."""
        try:
            os.makedirs(self.models_dir, exist_ok=True)
            
            self.models['lstm'].save(os.path.join(self.models_dir, 'lstm_model.h5'))
            self.models['transformer'].save(os.path.join(self.models_dir, 'transformer_model.h5'))
            self.models['cnn_lstm'].save(os.path.join(self.models_dir, 'cnn_lstm_model.h5'))
            self.models['xgboost'].save(os.path.join(self.models_dir, 'xgboost_model.pkl'))
            self.models['dqn'].save(os.path.join(self.models_dir, 'dqn_model.h5'))
            self.models['ppo'].save(os.path.join(self.models_dir, 'ppo_model.zip'))
            
            logger.info("All models saved successfully")
        
        except Exception as e:
            logger.error(f"Error saving models: {e}")
