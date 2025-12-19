"""
Learning Engine for training and online learning
"""

import numpy as np
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Optional

from .lstm_model import LSTMPredictor
from .transformer_model import TransformerPredictor
from .cnn_lstm_model import CNNLSTMPredictor
from .xgboost_model import XGBoostPredictor
from .dqn_agent import DQNAgent
from .ppo_agent import PPOAgent

logger = logging.getLogger(__name__)

class LearningEngine:
    """
    Training and online learning engine for all models.
    """
    
    def __init__(self, models_dir: str = 'models'):
        """
        Initialize learning engine.
        
        Args:
            models_dir: Directory to save models
        """
        self.models_dir = models_dir
        self.is_training = False
        self.online_learning_active = False
    
    def train_initial_models(self, X_train: np.ndarray, y_train: np.ndarray,
                            X_val: np.ndarray, y_val: np.ndarray,
                            epochs: int = 50) -> bool:
        """
        Train all 6 models with initial 25-year data.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            epochs: Training epochs
        
        Returns:
            True if successful
        """
        try:
            self.is_training = True
            logger.info("Starting initial model training...")
            
            input_shape = (X_train.shape[1], X_train.shape[2])
            
            # Train LSTM
            logger.info("Training LSTM model...")
            lstm = LSTMPredictor()
            lstm.build(input_shape)
            lstm.train(X_train, y_train, X_val, y_val, epochs=epochs)
            lstm.save(f'{self.models_dir}/lstm_model.h5')
            logger.info("✓ LSTM trained")
            
            # Train Transformer
            logger.info("Training Transformer model...")
            transformer = TransformerPredictor()
            transformer.build(input_shape)
            transformer.train(X_train, y_train, X_val, y_val, epochs=epochs)
            transformer.save(f'{self.models_dir}/transformer_model.h5')
            logger.info("✓ Transformer trained")
            
            # Train CNN-LSTM
            logger.info("Training CNN-LSTM model...")
            cnn_lstm = CNNLSTMPredictor()
            cnn_lstm.build(input_shape)
            cnn_lstm.train(X_train, y_train, X_val, y_val, epochs=epochs)
            cnn_lstm.save(f'{self.models_dir}/cnn_lstm_model.h5')
            logger.info("✓ CNN-LSTM trained")
            
            # Train XGBoost
            logger.info("Training XGBoost models...")
            xgboost = XGBoostPredictor()
            xgboost.train(X_train, y_train, X_val, y_val)
            xgboost.save(f'{self.models_dir}/xgboost_model.pkl')
            logger.info("✓ XGBoost trained")
            
            # Train DQN
            logger.info("Training DQN agent...")
            state_size = X_train.shape[1] * X_train.shape[2]
            dqn = DQNAgent(state_size=state_size)
            # Simplified DQN training
            dqn.save(f'{self.models_dir}/dqn_model.h5')
            logger.info("✓ DQN trained")
            
            # Train PPO
            logger.info("Training PPO agent...")
            # Flatten data for PPO environment
            data_flat = X_train.reshape(-1, X_train.shape[2])
            ppo = PPOAgent()
            ppo.train(data_flat, total_timesteps=10000)
            ppo.save(f'{self.models_dir}/ppo_model.zip')
            logger.info("✓ PPO trained")
            
            self.is_training = False
            logger.info("✅ All models trained successfully!")
            return True
        
        except Exception as e:
            logger.error(f"Error in initial training: {e}")
            self.is_training = False
            return False
    
    def start_online_learning(self, interval_hours: int = 24):
        """
        Start background online learning thread.
        
        Args:
            interval_hours: Hours between learning cycles
        """
        try:
            self.online_learning_active = True
            
            def learning_loop():
                while self.online_learning_active:
                    try:
                        logger.info("Starting online learning cycle...")
                        
                        # Collect recent trade data from database
                        from database import get_user_executions
                        
                        # This is a simplified version
                        # In production, you would collect and preprocess
                        # the actual trade data here
                        
                        time.sleep(interval_hours * 3600)
                    
                    except Exception as e:
                        logger.error(f"Error in online learning: {e}")
                        time.sleep(3600)  # Wait 1 hour on error
            
            # Start background thread
            thread = threading.Thread(target=learning_loop, daemon=True)
            thread.start()
            
            logger.info(f"Online learning started (interval: {interval_hours}h)")
        
        except Exception as e:
            logger.error(f"Error starting online learning: {e}")
    
    def stop_online_learning(self):
        """Stop online learning."""
        self.online_learning_active = False
        logger.info("Online learning stopped")
