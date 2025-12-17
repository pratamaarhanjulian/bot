"""
Main ML Engine orchestrator
"""

import numpy as np
import logging
from typing import Dict, Optional

from .ensemble import EnsemblePredictor
from .trade_manager import TradeManager
from .learning_engine import LearningEngine

logger = logging.getLogger(__name__)

class MLEngine:
    """
    Main ML Engine that orchestrates all AI components.
    """
    
    def __init__(self, models_dir: str = 'models'):
        """
        Initialize ML Engine.
        
        Args:
            models_dir: Directory containing models
        """
        self.models_dir = models_dir
        self.ensemble = EnsemblePredictor(models_dir)
        self.trade_manager = TradeManager()
        self.learning_engine = LearningEngine(models_dir)
        
        logger.info("ML Engine initialized")
    
    def process_signal(self, ohlc_data: np.ndarray, tier: str,
                      account_balance: float = 10000) -> Dict:
        """
        Process OHLC data and generate trading signal.
        
        Args:
            ohlc_data: OHLC data array (N, 5) - [open, high, low, close, volume]
            tier: User tier
            account_balance: Account balance
        
        Returns:
            Dictionary with signal information
        """
        try:
            # Prepare data for prediction
            X = self._prepare_features(ohlc_data)
            
            if X is None:
                return {
                    'action': None,
                    'message': 'Insufficient data'
                }
            
            # Get ensemble prediction
            predictions, confidence, _ = self.ensemble.predict(X)
            
            logger.info(f"Prediction confidence: {confidence:.2f}%")
            
            # Check confidence threshold
            if not self.ensemble.should_trade(confidence):
                return {
                    'action': None,
                    'predictions': predictions[0].tolist() if len(predictions) > 0 else [],
                    'confidence': confidence,
                    'message': f'Confidence too low: {confidence:.2f}% < 85%'
                }
            
            # Calculate trade parameters
            trade_params = self.trade_manager.calculate_trade_parameters(
                predictions=predictions[0],
                confidence=confidence,
                ohlc_data=ohlc_data,
                tier=tier,
                account_balance=account_balance
            )
            
            # Add predictions to result
            trade_params['predictions'] = predictions[0].tolist()
            
            return trade_params
        
        except Exception as e:
            logger.error(f"Error processing signal: {e}")
            return {
                'action': None,
                'message': f'Error: {str(e)}'
            }
    
    def _prepare_features(self, ohlc_data: np.ndarray) -> Optional[np.ndarray]:
        """
        Prepare features from OHLC data.
        
        Args:
            ohlc_data: OHLC data (N, 5)
        
        Returns:
            Features array (1, sequence_length, features) or None
        """
        try:
            sequence_length = 100
            
            # Check if we have enough data
            if len(ohlc_data) < sequence_length:
                logger.warning(f"Insufficient data: {len(ohlc_data)} < {sequence_length}")
                return None
            
            # Get last sequence_length candles
            recent_data = ohlc_data[-sequence_length:]
            
            # Calculate technical indicators
            features = []
            
            for i in range(len(recent_data)):
                candle = recent_data[i]
                
                # Basic features
                open_price = candle[0]
                high = candle[1]
                low = candle[2]
                close = candle[3]
                volume = candle[4]
                
                # Normalized features
                feature_vector = [
                    (close - open_price) / (open_price + 1e-8),  # Price change
                    (high - low) / (close + 1e-8),  # Range
                    (close - low) / (high - low + 1e-8),  # Close position
                    volume / (np.mean(recent_data[:, 4]) + 1e-8),  # Volume ratio
                ]
                
                # Simple moving averages (if enough history)
                if i >= 20:
                    sma_20 = np.mean(recent_data[i-20:i+1, 3])
                    feature_vector.append((close - sma_20) / (sma_20 + 1e-8))
                else:
                    feature_vector.append(0)
                
                if i >= 50:
                    sma_50 = np.mean(recent_data[i-50:i+1, 3])
                    feature_vector.append((close - sma_50) / (sma_50 + 1e-8))
                else:
                    feature_vector.append(0)
                
                # RSI (simplified)
                if i >= 14:
                    price_changes = np.diff(recent_data[i-14:i+1, 3])
                    gains = np.where(price_changes > 0, price_changes, 0)
                    losses = np.where(price_changes < 0, -price_changes, 0)
                    avg_gain = np.mean(gains)
                    avg_loss = np.mean(losses)
                    rs = avg_gain / (avg_loss + 1e-8)
                    rsi = 100 - (100 / (1 + rs))
                    feature_vector.append((rsi - 50) / 50)  # Normalize to [-1, 1]
                else:
                    feature_vector.append(0)
                
                # ATR (simplified)
                if i >= 14:
                    tr = []
                    for j in range(max(0, i-14), i):
                        tr.append(max(
                            recent_data[j+1][1] - recent_data[j+1][2],
                            abs(recent_data[j+1][1] - recent_data[j][3]),
                            abs(recent_data[j+1][2] - recent_data[j][3])
                        ))
                    atr = np.mean(tr)
                    feature_vector.append(atr / (close + 1e-8))
                else:
                    feature_vector.append(0)
                
                # MACD (simplified)
                if i >= 26:
                    ema_12 = np.mean(recent_data[i-12:i+1, 3])
                    ema_26 = np.mean(recent_data[i-26:i+1, 3])
                    macd = (ema_12 - ema_26) / (close + 1e-8)
                    feature_vector.append(macd)
                else:
                    feature_vector.append(0)
                
                # Bollinger Bands (simplified)
                if i >= 20:
                    sma = np.mean(recent_data[i-20:i+1, 3])
                    std = np.std(recent_data[i-20:i+1, 3])
                    bb_position = (close - sma) / (2 * std + 1e-8)
                    feature_vector.append(bb_position)
                else:
                    feature_vector.append(0)
                
                features.append(feature_vector)
            
            # Convert to numpy array and add batch dimension
            X = np.array(features).reshape(1, sequence_length, -1)
            
            return X.astype(np.float32)
        
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None
    
    def start_online_learning(self, interval_hours: int = 24):
        """Start online learning."""
        self.learning_engine.start_online_learning(interval_hours)
    
    def stop_online_learning(self):
        """Stop online learning."""
        self.learning_engine.stop_online_learning()
