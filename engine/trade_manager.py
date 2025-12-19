"""
Adaptive Trade Manager for SL/TP/Lot calculation
"""

import numpy as np
import logging
from typing import Dict, Tuple

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    # Fallback values if config doesn't exist
    class config:
        MIN_CONFIDENCE = 85.0
        LOT_SIZES = {
            'FREE': 0.01,
            'PREMIUM': {'min': 0.02, 'max': 0.05},
            'SUPER': {'min': 0.05, 'max': 0.10},
            'SUPREME': {'min': 0.05, 'max': 0.10}
        }

logger = logging.getLogger(__name__)

class TradeManager:
    """
    Adaptive trade management with risk-based calculations.
    """
    
    def __init__(self):
        """Initialize trade manager."""
        self.atr_period = 14
        self.min_confidence = getattr(config, 'MIN_CONFIDENCE', 85.0)
    
    def calculate_atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                      period: int = 14) -> float:
        """
        Calculate Average True Range (ATR).
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period
        
        Returns:
            ATR value
        """
        try:
            # True Range calculation
            tr1 = high[1:] - low[1:]
            tr2 = np.abs(high[1:] - close[:-1])
            tr3 = np.abs(low[1:] - close[:-1])
            
            tr = np.maximum(tr1, np.maximum(tr2, tr3))
            
            # ATR = average of TR over period
            atr = np.mean(tr[-period:]) if len(tr) >= period else np.mean(tr)
            
            return float(atr)
        
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return 0.0
    
    def calculate_sl_multiplier(self, confidence: float, volatility: float) -> float:
        """
        Calculate Stop Loss multiplier based on confidence and volatility.
        
        Args:
            confidence: Prediction confidence (0-100)
            volatility: Market volatility (normalized)
        
        Returns:
            SL multiplier
        """
        try:
            # Base multiplier
            base_multiplier = 2.0
            
            # Adjust for confidence (higher confidence = tighter SL)
            if confidence >= 95:
                confidence_adj = 0.8
            elif confidence >= 90:
                confidence_adj = 1.0
            else:
                confidence_adj = 1.2
            
            # Adjust for volatility (higher volatility = wider SL)
            volatility_adj = 1.0 + (volatility * 0.5)
            
            multiplier = base_multiplier * confidence_adj * volatility_adj
            
            return multiplier
        
        except Exception as e:
            logger.error(f"Error calculating SL multiplier: {e}")
            return 2.0
    
    def calculate_rr_ratio(self, confidence: float) -> float:
        """
        Calculate Risk-Reward ratio based on confidence.
        
        Args:
            confidence: Prediction confidence (0-100)
        
        Returns:
            RR ratio
        """
        try:
            if confidence >= 90:
                return 3.0  # 3:1 RR for high confidence
            elif confidence >= 85:
                return 2.0  # 2:1 RR for medium confidence
            else:
                return 1.5  # 1.5:1 RR for low confidence
        
        except Exception as e:
            logger.error(f"Error calculating RR ratio: {e}")
            return 2.0
    
    def calculate_lot_size(self, tier: str, confidence: float, 
                           account_balance: float = 10000) -> float:
        """
        Calculate lot size based on tier and confidence.
        
        Args:
            tier: User tier (FREE, PREMIUM, SUPER, SUPREME)
            confidence: Prediction confidence
            account_balance: Account balance in USD
        
        Returns:
            Lot size
        """
        try:
            lot_config = getattr(config, 'LOT_SIZES', {})
            
            if tier == 'FREE':
                return lot_config.get('FREE', 0.01)
            
            elif tier in ['PREMIUM', 'SUPER', 'SUPREME']:
                tier_config = lot_config.get(tier, {'min': 0.02, 'max': 0.05})
                min_lot = tier_config['min']
                max_lot = tier_config['max']
                
                # Scale lot size based on confidence
                confidence_factor = (confidence - 85) / 15  # 0-1 scale for 85-100%
                lot_size = min_lot + (max_lot - min_lot) * confidence_factor
                
                # Risk management: max 2% of balance per trade
                max_risk = account_balance * 0.02
                risk_based_lot = max_risk / 1000  # Assuming 1 lot = $1000 risk
                
                lot_size = min(lot_size, risk_based_lot)
                
                return round(lot_size, 2)
            
            else:
                return 0.01
        
        except Exception as e:
            logger.error(f"Error calculating lot size: {e}")
            return 0.01
    
    def calculate_trade_parameters(self, predictions: np.ndarray, confidence: float,
                                   ohlc_data: np.ndarray, tier: str,
                                   account_balance: float = 10000) -> Dict:
        """
        Calculate complete trade parameters.
        
        Args:
            predictions: Price predictions (30 values)
            confidence: Prediction confidence
            ohlc_data: Recent OHLC data (open, high, low, close, volume)
            tier: User tier
            account_balance: Account balance
        
        Returns:
            Dictionary with trade parameters
        """
        try:
            # Extract OHLC components
            high = ohlc_data[:, 1]
            low = ohlc_data[:, 2]
            close = ohlc_data[:, 3]
            
            # Current price (last close)
            current_price = close[-1]
            
            # Entry price (from first prediction)
            entry_price = predictions[0]
            
            # Determine action
            price_change = (predictions[-1] - predictions[0]) / predictions[0] * 100
            
            if price_change > 0.1:
                action = 'BUY'
                direction = 1
            elif price_change < -0.1:
                action = 'SELL'
                direction = -1
            else:
                return {
                    'action': None,
                    'entry': current_price,
                    'sl': 0,
                    'tp': 0,
                    'lot': 0,
                    'confidence': confidence,
                    'message': 'No clear signal'
                }
            
            # Calculate ATR for volatility
            atr = self.calculate_atr(high, low, close)
            volatility = atr / current_price  # Normalized volatility
            
            # Calculate Stop Loss
            sl_multiplier = self.calculate_sl_multiplier(confidence, volatility)
            sl_distance = atr * sl_multiplier
            
            if action == 'BUY':
                sl_price = entry_price - sl_distance
            else:
                sl_price = entry_price + sl_distance
            
            # Calculate Take Profit based on RR ratio
            rr_ratio = self.calculate_rr_ratio(confidence)
            tp_distance = sl_distance * rr_ratio
            
            if action == 'BUY':
                tp_price = entry_price + tp_distance
            else:
                tp_price = entry_price - tp_distance
            
            # Calculate lot size
            lot_size = self.calculate_lot_size(tier, confidence, account_balance)
            
            return {
                'action': action,
                'entry': round(entry_price, 5),
                'sl': round(sl_price, 5),
                'tp': round(tp_price, 5),
                'lot': lot_size,
                'confidence': confidence,
                'atr': round(atr, 5),
                'rr_ratio': rr_ratio,
                'message': f'{action} signal with {confidence:.1f}% confidence'
            }
        
        except Exception as e:
            logger.error(f"Error calculating trade parameters: {e}")
            return {
                'action': None,
                'entry': 0,
                'sl': 0,
                'tp': 0,
                'lot': 0,
                'confidence': 0,
                'message': f'Error: {str(e)}'
            }
