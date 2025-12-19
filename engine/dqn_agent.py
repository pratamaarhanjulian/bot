"""
Deep Q-Network (DQN) Agent for trading optimization
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from collections import deque
import random
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class DQNAgent:
    """
    DQN agent for entry/exit optimization.
    """
    
    def __init__(self, state_size: int, action_size: int = 3, 
                 model_path: Optional[str] = None):
        """
        Initialize DQN agent.
        
        Args:
            state_size: Size of state space
            action_size: Number of actions (BUY, SELL, HOLD)
            model_path: Path to saved model (optional)
        """
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        
        if model_path:
            try:
                self.model = keras.models.load_model(model_path)
                logger.info(f"DQN model loaded from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load DQN model: {e}")
                self.model = self._build_model()
        else:
            self.model = self._build_model()
    
    def _build_model(self) -> keras.Model:
        """Build the DQN neural network."""
        try:
            model = keras.Sequential([
                keras.layers.Dense(128, activation='relu', 
                                  input_shape=(self.state_size,)),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(64, activation='relu'),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(32, activation='relu'),
                keras.layers.Dense(self.action_size, activation='linear')
            ])
            
            model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
                loss='mse'
            )
            
            logger.info("DQN model built successfully")
            return model
        
        except Exception as e:
            logger.error(f"Error building DQN model: {e}")
            raise
    
    def remember(self, state: np.ndarray, action: int, reward: float, 
                 next_state: np.ndarray, done: bool):
        """Store experience in memory."""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state: np.ndarray, training: bool = False) -> int:
        """
        Choose action based on state.
        
        Args:
            state: Current state
            training: If True, use epsilon-greedy policy
        
        Returns:
            Action index (0=BUY, 1=SELL, 2=HOLD)
        """
        try:
            if training and np.random.rand() <= self.epsilon:
                return random.randrange(self.action_size)
            
            state = np.reshape(state, [1, self.state_size])
            act_values = self.model.predict(state, verbose=0)
            return np.argmax(act_values[0])
        
        except Exception as e:
            logger.error(f"Error in DQN action: {e}")
            return 2  # Default to HOLD
    
    def replay(self, batch_size: int = 32):
        """
        Train the model using experience replay.
        
        Args:
            batch_size: Size of training batch
        """
        try:
            if len(self.memory) < batch_size:
                return
            
            minibatch = random.sample(self.memory, batch_size)
            
            states = np.array([i[0] for i in minibatch])
            actions = np.array([i[1] for i in minibatch])
            rewards = np.array([i[2] for i in minibatch])
            next_states = np.array([i[3] for i in minibatch])
            dones = np.array([i[4] for i in minibatch])
            
            # Reshape states
            states = np.reshape(states, (batch_size, self.state_size))
            next_states = np.reshape(next_states, (batch_size, self.state_size))
            
            # Get Q-values
            targets = self.model.predict(states, verbose=0)
            next_q_values = self.model.predict(next_states, verbose=0)
            
            # Update Q-values
            for i in range(batch_size):
                if dones[i]:
                    targets[i][actions[i]] = rewards[i]
                else:
                    targets[i][actions[i]] = rewards[i] + self.gamma * np.max(next_q_values[i])
            
            # Train the model
            self.model.fit(states, targets, epochs=1, verbose=0)
            
            # Decay epsilon
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
        
        except Exception as e:
            logger.error(f"Error in DQN replay: {e}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions for ensemble.
        
        Args:
            X: Input features (batch, sequence, features)
        
        Returns:
            Predictions array (batch, 30)
        """
        try:
            # Flatten input for DQN
            X_flat = X.reshape(X.shape[0], -1)
            
            # Use last layer before output as features
            feature_model = keras.Model(
                inputs=self.model.input,
                outputs=self.model.layers[-2].output
            )
            
            features = feature_model.predict(X_flat, verbose=0)
            
            # Simple linear projection to 30 outputs
            predictions = np.tile(features.mean(axis=1, keepdims=True), (1, 30))
            
            return predictions
        
        except Exception as e:
            logger.error(f"Error in DQN prediction: {e}")
            return np.zeros((X.shape[0], 30))
    
    def save(self, path: str):
        """Save model to file."""
        try:
            self.model.save(path)
            logger.info(f"DQN model saved to {path}")
        except Exception as e:
            logger.error(f"Error saving DQN model: {e}")
