"""
PPO (Proximal Policy Optimization) Agent for trading
"""

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import gym
from gym import spaces
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TradingEnv(gym.Env):
    """
    Custom trading environment for PPO.
    """
    
    def __init__(self, data: np.ndarray):
        """
        Initialize trading environment.
        
        Args:
            data: Historical price data
        """
        super(TradingEnv, self).__init__()
        
        self.data = data
        self.current_step = 0
        self.max_steps = len(data) - 1
        
        # Define action and observation space
        # Actions: 0=HOLD, 1=BUY, 2=SELL
        self.action_space = spaces.Discrete(3)
        
        # Observation space: OHLCV + indicators
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(data.shape[1],), 
            dtype=np.float32
        )
        
        self.reset()
    
    def reset(self):
        """Reset environment to initial state."""
        self.current_step = 0
        self.position = 0  # 0=no position, 1=long, -1=short
        self.entry_price = 0
        self.profit = 0
        
        return self.data[self.current_step]
    
    def step(self, action: int):
        """
        Execute one step in the environment.
        
        Args:
            action: Action to take
        
        Returns:
            observation, reward, done, info
        """
        current_price = self.data[self.current_step][3]  # Close price
        reward = 0
        
        # Execute action
        if action == 1 and self.position == 0:  # BUY
            self.position = 1
            self.entry_price = current_price
        
        elif action == 2 and self.position == 0:  # SELL
            self.position = -1
            self.entry_price = current_price
        
        elif action == 0 and self.position != 0:  # CLOSE position
            if self.position == 1:
                reward = current_price - self.entry_price
            else:
                reward = self.entry_price - current_price
            
            self.profit += reward
            self.position = 0
            self.entry_price = 0
        
        # Move to next step
        self.current_step += 1
        done = self.current_step >= self.max_steps
        
        # Get next observation
        if not done:
            obs = self.data[self.current_step]
        else:
            obs = self.data[self.current_step - 1]
        
        info = {'profit': self.profit}
        
        return obs, reward, done, info
    
    def render(self, mode='human'):
        """Render the environment."""
        pass

class PPOAgent:
    """
    PPO agent for trading optimization.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize PPO agent.
        
        Args:
            model_path: Path to saved model (optional)
        """
        self.model = None
        self.env = None
        
        if model_path:
            try:
                self.model = PPO.load(model_path)
                logger.info(f"PPO model loaded from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load PPO model: {e}")
    
    def build(self, data: np.ndarray):
        """
        Build new PPO model.
        
        Args:
            data: Training data
        """
        try:
            self.env = DummyVecEnv([lambda: TradingEnv(data)])
            
            self.model = PPO(
                "MlpPolicy",
                self.env,
                learning_rate=0.0003,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                verbose=0
            )
            
            logger.info("PPO model built successfully")
        
        except Exception as e:
            logger.error(f"Error building PPO model: {e}")
            raise
    
    def train(self, data: np.ndarray, total_timesteps: int = 100000):
        """
        Train the PPO model.
        
        Args:
            data: Training data
            total_timesteps: Total training steps
        """
        try:
            if self.model is None:
                self.build(data)
            
            self.model.learn(total_timesteps=total_timesteps)
            
            logger.info("PPO model trained successfully")
        
        except Exception as e:
            logger.error(f"Error training PPO: {e}")
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions for ensemble.
        
        Args:
            X: Input features (batch, sequence, features)
        
        Returns:
            Predictions array (batch, 30)
        """
        try:
            if self.model is None:
                logger.warning("PPO model not trained yet")
                return np.zeros((X.shape[0], 30))
            
            # Use policy network features for prediction
            predictions = []
            
            for i in range(X.shape[0]):
                # Get last observation from sequence
                obs = X[i, -1, :]
                
                # Get action probabilities
                action, _ = self.model.predict(obs, deterministic=True)
                
                # Simple prediction based on action
                # This is a simplified approach for ensemble
                base_value = obs[3] if len(obs) > 3 else 0  # Close price
                
                if action == 1:  # BUY signal - predict upward
                    pred = np.linspace(base_value, base_value * 1.01, 30)
                elif action == 2:  # SELL signal - predict downward
                    pred = np.linspace(base_value, base_value * 0.99, 30)
                else:  # HOLD - predict sideways
                    pred = np.full(30, base_value)
                
                predictions.append(pred)
            
            return np.array(predictions)
        
        except Exception as e:
            logger.error(f"Error in PPO prediction: {e}")
            return np.zeros((X.shape[0], 30))
    
    def save(self, path: str):
        """Save model to file."""
        try:
            if self.model:
                self.model.save(path)
                logger.info(f"PPO model saved to {path}")
        except Exception as e:
            logger.error(f"Error saving PPO model: {e}")
