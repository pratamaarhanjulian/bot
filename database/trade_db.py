"""
Trade database operations
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from .setup_db import get_connection

def save_signal(user_id: int, pair: str, action: str, entry: float,
                sl: float, tp: float, lot: float, confidence: float,
                predictions: List[float], tier: str) -> Optional[int]:
    """
    Save a trading signal.
    
    Args:
        user_id: Telegram user ID
        pair: Trading pair
        action: BUY or SELL
        entry: Entry price
        sl: Stop loss
        tp: Take profit
        lot: Lot size
        confidence: Prediction confidence
        predictions: List of predicted prices
        tier: User tier
    
    Returns:
        int: Signal ID or None if failed
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        predictions_json = json.dumps(predictions)
        
        cursor.execute('''
            INSERT INTO signals (user_id, pair, action, entry, sl, tp, lot,
                               confidence, predictions, tier, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, pair, action, entry, sl, tp, lot, confidence,
              predictions_json, tier, datetime.now()))
        
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return signal_id
    
    except Exception as e:
        print(f"Error saving signal: {e}")
        return None

def save_execution(user_id: int, mt5_id: str, signal_id: int, pair: str,
                   action: str, entry: float, exit_price: float, lot: float,
                   profit: float, result: str, tier: str) -> Optional[int]:
    """
    Save a trade execution.
    
    Args:
        user_id: Telegram user ID
        mt5_id: MT5 account ID
        signal_id: Related signal ID
        pair: Trading pair
        action: BUY or SELL
        entry: Entry price
        exit_price: Exit price
        lot: Lot size
        profit: Profit/loss amount
        result: WIN or LOSS
        tier: User tier
    
    Returns:
        int: Execution ID or None if failed
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO executions (user_id, mt5_id, signal_id, pair, action,
                                   entry, exit, lot, profit, result, tier,
                                   executed_at, closed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, mt5_id, signal_id, pair, action, entry, exit_price,
              lot, profit, result, tier, datetime.now(), datetime.now()))
        
        execution_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return execution_id
    
    except Exception as e:
        print(f"Error saving execution: {e}")
        return None

def get_user_signals(user_id: int, limit: int = 10) -> List[Dict]:
    """
    Get user's recent signals.
    
    Args:
        user_id: Telegram user ID
        limit: Maximum number of signals to return
    
    Returns:
        List of signal dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM signals 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"Error getting signals: {e}")
        return []

def get_user_executions(user_id: int, limit: int = 10) -> List[Dict]:
    """
    Get user's recent executions.
    
    Args:
        user_id: Telegram user ID
        limit: Maximum number of executions to return
    
    Returns:
        List of execution dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM executions 
            WHERE user_id = ?
            ORDER BY executed_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"Error getting executions: {e}")
        return []

def get_user_stats(user_id: int, days: int = 30) -> Dict:
    """
    Get user trading statistics.
    
    Args:
        user_id: Telegram user ID
        days: Number of days to calculate stats for
    
    Returns:
        Dict with statistics
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        # Get today's stats
        cursor.execute('''
            SELECT COUNT(*) as count, COALESCE(SUM(profit), 0) as profit
            FROM executions
            WHERE user_id = ? AND DATE(executed_at) = DATE('now')
        ''', (user_id,))
        
        today = dict(cursor.fetchone())
        
        # Get overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
                COALESCE(SUM(profit), 0) as total_profit,
                COALESCE(MAX(profit), 0) as max_profit,
                COALESCE(MIN(profit), 0) as max_drawdown
            FROM executions
            WHERE user_id = ? AND executed_at > ?
        ''', (user_id, since_date))
        
        overall = dict(cursor.fetchone())
        conn.close()
        
        # Calculate win rate
        if overall['total_trades'] > 0:
            win_rate = (overall['wins'] / overall['total_trades']) * 100
        else:
            win_rate = 0
        
        return {
            'today': today,
            'total_trades': overall['total_trades'],
            'wins': overall['wins'],
            'losses': overall['losses'],
            'win_rate': win_rate,
            'total_profit': overall['total_profit'],
            'max_profit': overall['max_profit'],
            'max_drawdown': overall['max_drawdown']
        }
    
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {
            'today': {'count': 0, 'profit': 0},
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0,
            'total_profit': 0,
            'max_profit': 0,
            'max_drawdown': 0
        }
