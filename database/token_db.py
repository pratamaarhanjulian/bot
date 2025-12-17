"""
Token database operations
"""

import random
import string
from datetime import datetime
from typing import Optional, Dict, List
from .setup_db import get_connection

def generate_token() -> str:
    """
    Generate a random 8-character token.
    
    Returns:
        str: Random token
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))

def create_token(mt5_id: str, tier: str, expired_at: datetime) -> Optional[str]:
    """
    Create a new token.
    
    Args:
        mt5_id: MT5 account ID
        tier: Tier level
        expired_at: Expiration datetime
    
    Returns:
        str: Generated token or None if failed
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Generate unique token
        token = generate_token()
        max_attempts = 10
        
        for _ in range(max_attempts):
            try:
                cursor.execute('''
                    INSERT INTO tokens (token, mt5_id, tier, expired_at, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (token, mt5_id, tier, expired_at, datetime.now()))
                
                conn.commit()
                conn.close()
                return token
            
            except sqlite3.IntegrityError:
                # Token already exists, generate new one
                token = generate_token()
                continue
        
        conn.close()
        return None
    
    except Exception as e:
        print(f"Error creating token: {e}")
        return None

def validate_token(token: str, mt5_id: str) -> bool:
    """
    Validate if token is valid and belongs to MT5 ID.
    
    Args:
        token: Access token
        mt5_id: MT5 account ID
    
    Returns:
        bool: True if valid
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tokens 
            WHERE token = ? AND mt5_id = ? AND expired_at > ?
        ''', (token, mt5_id, datetime.now()))
        
        row = cursor.fetchone()
        conn.close()
        
        return row is not None
    
    except Exception as e:
        print(f"Error validating token: {e}")
        return False

def get_token_info(token: str) -> Optional[Dict]:
    """
    Get token information.
    
    Args:
        token: Access token
    
    Returns:
        Dict with token info or None
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tokens WHERE token = ?', (token,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def delete_token(token: str) -> bool:
    """
    Delete a token.
    
    Args:
        token: Access token
    
    Returns:
        bool: True if successful
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tokens WHERE token = ?', (token,))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error deleting token: {e}")
        return False

def get_all_tokens() -> List[Dict]:
    """
    Get all tokens.
    
    Returns:
        List of token dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tokens ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"Error getting tokens: {e}")
        return []

import sqlite3
