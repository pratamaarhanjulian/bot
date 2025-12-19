"""
User database operations
"""

from datetime import datetime
from typing import Optional, List, Dict
from .setup_db import get_connection

def create_user(user_id: int, username: str = None, tier: str = 'FREE') -> bool:
    """
    Create a new user.
    
    Args:
        user_id: Telegram user ID
        username: Telegram username
        tier: User tier (FREE, PREMIUM, SUPER, SUPREME)
    
    Returns:
        bool: True if successful
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (user_id, username, tier, signal_quota, created_at)
            VALUES (?, ?, ?, 5, ?)
        ''', (user_id, username, tier, datetime.now()))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def get_user(user_id: int) -> Optional[Dict]:
    """
    Get user information.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        Dict with user info or None
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def user_exists(user_id: int) -> bool:
    """
    Check if user exists.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        bool: True if user exists
    """
    user = get_user(user_id)
    return user is not None

def update_user_tier(user_id: int, tier: str, token: str, mt5_id: str, 
                     expired_at: datetime) -> bool:
    """
    Update user tier and related information.
    
    Args:
        user_id: Telegram user ID
        tier: New tier
        token: Access token
        mt5_id: MT5 account ID
        expired_at: Expiration date
    
    Returns:
        bool: True if successful
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update quota based on tier
        quota = -1 if tier != 'FREE' else 5
        
        cursor.execute('''
            UPDATE users 
            SET tier = ?, token = ?, mt5_id = ?, expired_at = ?, signal_quota = ?
            WHERE user_id = ?
        ''', (tier, token, mt5_id, expired_at, quota, user_id))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error updating user tier: {e}")
        return False

def update_user_quota(user_id: int, quota_change: int) -> bool:
    """
    Update user signal quota.
    
    Args:
        user_id: Telegram user ID
        quota_change: Change in quota (negative to decrease)
    
    Returns:
        bool: True if successful
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET signal_quota = signal_quota + ?
            WHERE user_id = ?
        ''', (quota_change, user_id))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error updating quota: {e}")
        return False

def get_all_users(tier: str = None) -> List[Dict]:
    """
    Get all users, optionally filtered by tier.
    
    Args:
        tier: Filter by tier (optional)
    
    Returns:
        List of user dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if tier:
            cursor.execute('SELECT * FROM users WHERE tier = ?', (tier,))
        else:
            cursor.execute('SELECT * FROM users')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def reset_daily_quota() -> bool:
    """
    Reset daily quota for FREE tier users.
    
    Returns:
        bool: True if successful
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET signal_quota = 5
            WHERE tier = 'FREE'
        ''')
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error resetting quota: {e}")
        return False
