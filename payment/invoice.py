"""
Invoice generator for payments
"""

import logging
from datetime import datetime
from typing import Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        PRICING = {}

logger = logging.getLogger(__name__)

class InvoiceGenerator:
    """
    Generate invoices for payment requests.
    """
    
    def __init__(self):
        """Initialize invoice generator."""
        self.pricing = getattr(config, 'PRICING', {})
        logger.info("Invoice Generator initialized")
    
    def generate_invoice(self, user_id: int, username: str,
                        package: str, duration: str) -> Dict:
        """
        Generate invoice for a package purchase.
        
        Args:
            user_id: Telegram user ID
            username: Username
            package: Package type (XAU, BTC, ALL, SUPER, SUPREME)
            duration: Duration (1M, 3M, 6M, 12M, LIFETIME)
        
        Returns:
            Invoice dictionary
        """
        try:
            # Get pricing
            amount = self._get_price(package, duration)
            
            if amount is None:
                logger.error(f"Invalid package/duration: {package}/{duration}")
                return None
            
            # Generate invoice
            invoice = {
                'invoice_id': f"INV-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'user_id': user_id,
                'username': username,
                'package': package,
                'duration': duration,
                'amount': amount,
                'amount_formatted': f"Rp {amount}.000",
                'created_at': datetime.now().isoformat(),
                'status': 'PENDING',
                'payment_info': {
                    'bank': 'BCA',
                    'account': '1234567890',
                    'name': 'Aurea Prime Elite'
                }
            }
            
            logger.info(f"Invoice generated: {invoice['invoice_id']} - Rp {amount}k")
            
            return invoice
        
        except Exception as e:
            logger.error(f"Error generating invoice: {e}")
            return None
    
    def _get_price(self, package: str, duration: str) -> int:
        """
        Get price for package and duration.
        
        Args:
            package: Package type
            duration: Duration
        
        Returns:
            Price in thousands (IDR) or None
        """
        try:
            if package == 'SUPREME':
                return self.pricing.get('SUPREME_PRICE', 2999)
            
            elif package in ['XAU', 'BTC', 'ALL']:
                package_pricing = self.pricing.get(package, {})
                return package_pricing.get(duration)
            
            elif package.startswith('SUPER_'):
                # SUPER packages are Premium × 1.6
                base_package = package.replace('SUPER_', '')
                base_pricing = self.pricing.get(base_package, {})
                base_price = base_pricing.get(duration)
                
                if base_price:
                    multiplier = self.pricing.get('SUPER_MULTIPLIER', 1.6)
                    return int(base_price * multiplier)
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting price: {e}")
            return None
    
    def get_payment_info(self) -> Dict[str, str]:
        """
        Get payment information from config or environment.
        
        Returns:
            Dictionary with payment details
        """
        # Try to get from config first
        payment_info = getattr(config, 'PAYMENT_INFO', None)
        
        if payment_info:
            return payment_info
        
        # Fallback to environment variables
        import os
        return {
            'bank': os.getenv('PAYMENT_BANK', 'BCA'),
            'account': os.getenv('PAYMENT_ACCOUNT', '1234567890'),
            'name': os.getenv('PAYMENT_NAME', 'Aurea Prime Elite')
        }
    
    def format_invoice_text(self, invoice: Dict) -> str:
        """
        Format invoice as text for display.
        
        Args:
            invoice: Invoice dictionary
        
        Returns:
            Formatted text
        """
        try:
            payment_info = invoice.get('payment_info', self.get_payment_info())
            
            text = (
                f"📄 <b>INVOICE</b>\n\n"
                f"<b>Invoice ID:</b> {invoice['invoice_id']}\n"
                f"<b>Date:</b> {invoice['created_at']}\n\n"
                f"<b>Customer:</b>\n"
                f"├ User ID: {invoice['user_id']}\n"
                f"└ Username: @{invoice['username']}\n\n"
                f"<b>Package Details:</b>\n"
                f"├ Package: {invoice['package']}\n"
                f"├ Duration: {invoice['duration']}\n"
                f"└ Amount: {invoice['amount_formatted']}\n\n"
                f"<b>Payment Information:</b>\n"
                f"├ Bank: {payment_info['bank']}\n"
                f"├ Account: {payment_info['account']}\n"
                f"└ Name: {payment_info['name']}\n\n"
                f"<i>Please transfer the exact amount and upload payment proof.</i>"
            )
            
            return text
        
        except Exception as e:
            logger.error(f"Error formatting invoice: {e}")
            return "Error formatting invoice"
