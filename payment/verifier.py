"""
Payment verifier for admin approval
"""

import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class PaymentVerifier:
    """
    Verify payment proofs submitted by users.
    """
    
    def __init__(self):
        """Initialize payment verifier."""
        logger.info("Payment Verifier initialized")
    
    def verify_payment(self, payment: Dict, admin_decision: str,
                       admin_notes: str = "") -> Dict:
        """
        Verify a payment.
        
        Args:
            payment: Payment dictionary
            admin_decision: 'APPROVED' or 'REJECTED'
            admin_notes: Optional notes
        
        Returns:
            Verification result
        """
        try:
            if admin_decision not in ['APPROVED', 'REJECTED']:
                logger.error(f"Invalid admin decision: {admin_decision}")
                return None
            
            result = {
                'payment_id': payment.get('id'),
                'user_id': payment.get('user_id'),
                'decision': admin_decision,
                'verified_at': datetime.now().isoformat(),
                'admin_notes': admin_notes
            }
            
            logger.info(f"Payment {result['payment_id']} {admin_decision}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            return None
    
    def validate_proof(self, proof_url: str) -> bool:
        """
        Validate payment proof URL.
        
        Args:
            proof_url: URL to payment proof
        
        Returns:
            True if valid
        """
        try:
            # Basic validation
            if not proof_url:
                return False
            
            # Check if it's a valid URL or file path
            if not (proof_url.startswith('http') or proof_url.startswith('file')):
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error validating proof: {e}")
            return False
    
    def check_amount(self, expected: int, received: int,
                     tolerance: float = 0.01) -> bool:
        """
        Check if received amount matches expected.
        
        Args:
            expected: Expected amount
            received: Received amount
            tolerance: Tolerance percentage
        
        Returns:
            True if amounts match within tolerance
        """
        try:
            diff = abs(expected - received)
            max_diff = expected * tolerance
            
            return diff <= max_diff
        
        except Exception as e:
            logger.error(f"Error checking amount: {e}")
            return False
