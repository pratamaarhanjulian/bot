"""
Signal Sender for transmitting signals to EA
"""

import logging
import json
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class SignalSender:
    """
    Signal sender for formatting and sending trading signals to EA.
    """
    
    def __init__(self):
        """Initialize signal sender."""
        logger.info("Signal Sender initialized")
    
    def format_signal(self, signal: Dict) -> Dict:
        """
        Format signal for EA consumption.
        
        Args:
            signal: Signal dictionary from ML Engine
        
        Returns:
            Formatted signal dictionary
        """
        try:
            if signal.get('action') is None:
                return {
                    'action': None,
                    'message': signal.get('message', 'No signal'),
                    'confidence': signal.get('confidence', 0),
                    'timestamp': datetime.now().isoformat()
                }
            
            formatted = {
                'action': signal['action'],
                'entry': round(signal['entry'], 5),
                'sl': round(signal['sl'], 5),
                'tp': round(signal['tp'], 5),
                'lot': round(signal['lot'], 2),
                'confidence': round(signal['confidence'], 2),
                'predictions': signal.get('predictions', []),
                'atr': signal.get('atr', 0),
                'rr_ratio': signal.get('rr_ratio', 2.0),
                'message': signal.get('message', 'Signal ready'),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Signal formatted: {formatted['action']} @ {formatted['entry']}")
            
            return formatted
        
        except Exception as e:
            logger.error(f"Error formatting signal: {e}")
            return {
                'action': None,
                'message': f'Format error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def validate_signal(self, signal: Dict) -> bool:
        """
        Validate signal before sending.
        
        Args:
            signal: Signal dictionary
        
        Returns:
            True if valid
        """
        try:
            if signal.get('action') is None:
                return True  # No-signal is valid
            
            required_fields = ['action', 'entry', 'sl', 'tp', 'lot', 'confidence']
            
            for field in required_fields:
                if field not in signal:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate action
            if signal['action'] not in ['BUY', 'SELL']:
                logger.error(f"Invalid action: {signal['action']}")
                return False
            
            # Validate prices
            if signal['entry'] <= 0 or signal['sl'] <= 0 or signal['tp'] <= 0:
                logger.error("Invalid prices (must be positive)")
                return False
            
            # Validate SL/TP logic
            if signal['action'] == 'BUY':
                if signal['sl'] >= signal['entry']:
                    logger.error("Invalid BUY signal: SL >= Entry")
                    return False
                if signal['tp'] <= signal['entry']:
                    logger.error("Invalid BUY signal: TP <= Entry")
                    return False
            
            elif signal['action'] == 'SELL':
                if signal['sl'] <= signal['entry']:
                    logger.error("Invalid SELL signal: SL <= Entry")
                    return False
                if signal['tp'] >= signal['entry']:
                    logger.error("Invalid SELL signal: TP >= Entry")
                    return False
            
            # Validate lot size
            if signal['lot'] <= 0 or signal['lot'] > 10:
                logger.error(f"Invalid lot size: {signal['lot']}")
                return False
            
            # Validate confidence
            if signal['confidence'] < 0 or signal['confidence'] > 100:
                logger.error(f"Invalid confidence: {signal['confidence']}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error validating signal: {e}")
            return False
    
    def to_json(self, signal: Dict) -> str:
        """
        Convert signal to JSON string.
        
        Args:
            signal: Signal dictionary
        
        Returns:
            JSON string
        """
        try:
            return json.dumps(signal, indent=2)
        except Exception as e:
            logger.error(f"Error converting signal to JSON: {e}")
            return json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
