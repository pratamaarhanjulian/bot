"""
Payment database operations
"""

from datetime import datetime
from typing import Optional, Dict, List
from .setup_db import get_connection

def create_payment(user_id: int, package: str, duration: str, 
                   amount: int, proof_url: str) -> Optional[int]:
    """
    Create a new payment record.
    
    Args:
        user_id: Telegram user ID
        package: Package type (XAU, BTC, ALL, SUPER, SUPREME)
        duration: Duration (1M, 3M, 6M, 12M, LIFETIME)
        amount: Amount in IDR thousands
        proof_url: URL to payment proof image
    
    Returns:
        int: Payment ID or None if failed
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO payments (user_id, package, duration, amount, proof_url, 
                                status, created_at)
            VALUES (?, ?, ?, ?, ?, 'PENDING', ?)
        ''', (user_id, package, duration, amount, proof_url, datetime.now()))
        
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return payment_id
    
    except Exception as e:
        print(f"Error creating payment: {e}")
        return None

def get_payment(payment_id: int) -> Optional[Dict]:
    """
    Get payment information.
    
    Args:
        payment_id: Payment ID
    
    Returns:
        Dict with payment info or None
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    except Exception as e:
        print(f"Error getting payment: {e}")
        return None

def update_payment_status(payment_id: int, status: str) -> bool:
    """
    Update payment status.
    
    Args:
        payment_id: Payment ID
        status: New status (PENDING, APPROVED, REJECTED)
    
    Returns:
        bool: True if successful
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        verified_at = datetime.now() if status != 'PENDING' else None
        
        cursor.execute('''
            UPDATE payments 
            SET status = ?, verified_at = ?
            WHERE id = ?
        ''', (status, verified_at, payment_id))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error updating payment: {e}")
        return False

def get_pending_payments() -> List[Dict]:
    """
    Get all pending payments.
    
    Returns:
        List of payment dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, u.username 
            FROM payments p
            LEFT JOIN users u ON p.user_id = u.user_id
            WHERE p.status = 'PENDING'
            ORDER BY p.created_at ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"Error getting pending payments: {e}")
        return []

def get_user_payments(user_id: int) -> List[Dict]:
    """
    Get all payments for a user.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        List of payment dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM payments 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"Error getting user payments: {e}")
        return []
