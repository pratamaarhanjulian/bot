"""
MT5 Connector for receiving OHLC data
"""

import logging
import numpy as np
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class MT5Connector:
    """
    Connector for handling MT5 OHLC data.
    """
    
    def __init__(self):
        """Initialize MT5 connector."""
        self.last_data = {}
        logger.info("MT5 Connector initialized")
    
    def parse_ohlc_message(self, message: Dict) -> Optional[np.ndarray]:
        """
        Parse OHLC message from EA.
        
        Args:
            message: OHLC message dictionary
        
        Returns:
            Numpy array of OHLC data or None
        """
        try:
            if 'data' not in message:
                logger.error("No data field in message")
                return None
            
            data = message['data']
            
            # Convert to numpy array
            # Expected format: [[time, open, high, low, close, volume], ...]
            ohlc_array = np.array(data, dtype=np.float32)
            
            # Validate shape
            if ohlc_array.ndim != 2 or ohlc_array.shape[1] != 6:
                logger.error(f"Invalid OHLC data shape: {ohlc_array.shape}")
                return None
            
            # Store last data for pair
            pair = message.get('pair', 'UNKNOWN')
            self.last_data[pair] = ohlc_array
            
            logger.debug(f"Parsed {len(ohlc_array)} candles for {pair}")
            
            return ohlc_array
        
        except Exception as e:
            logger.error(f"Error parsing OHLC message: {e}")
            return None
    
    def get_last_data(self, pair: str) -> Optional[np.ndarray]:
        """
        Get last OHLC data for a pair.
        
        Args:
            pair: Trading pair
        
        Returns:
            OHLC data or None
        """
        return self.last_data.get(pair)
    
    def validate_ohlc_data(self, ohlc_data: np.ndarray) -> bool:
        """
        Validate OHLC data quality.
        
        Args:
            ohlc_data: OHLC array
        
        Returns:
            True if valid
        """
        try:
            # Check for NaN or Inf values
            if np.any(np.isnan(ohlc_data)) or np.any(np.isinf(ohlc_data)):
                logger.warning("OHLC data contains NaN or Inf values")
                return False
            
            # Check for negative prices
            if np.any(ohlc_data[:, 1:5] <= 0):
                logger.warning("OHLC data contains negative or zero prices")
                return False
            
            # Check OHLC logic (high >= low, high >= open/close, low <= open/close)
            for i, candle in enumerate(ohlc_data):
                _, open_price, high, low, close, _ = candle
                
                if high < low:
                    logger.warning(f"Invalid candle {i}: high < low")
                    return False
                
                if high < max(open_price, close):
                    logger.warning(f"Invalid candle {i}: high < max(open, close)")
                    return False
                
                if low > min(open_price, close):
                    logger.warning(f"Invalid candle {i}: low > min(open, close)")
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error validating OHLC data: {e}")
            return False
