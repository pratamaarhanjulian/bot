"""
Database setup and initialization
"""

import sqlite3
import os
from typing import Optional

def get_connection() -> sqlite3.Connection:
    """
    Get database connection.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    try:
        # Try to import config
        import config
        db_path = config.DATABASE_PATH
    except ImportError:
        # Fallback if config doesn't exist yet
        db_path = "database/aurea_prime.db"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database() -> bool:
    """
    Initialize database with schema.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        # Execute schema
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executescript(schema)
        conn.commit()
        conn.close()
        
        print("✅ Database initialized successfully!")
        return True
    
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def execute_query(query: str, params: tuple = (), fetch_one: bool = False) -> Optional[any]:
    """
    Execute a database query.
    
    Args:
        query: SQL query
        params: Query parameters
        fetch_one: If True, fetch one result, else fetch all
    
    Returns:
        Query results or None
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchone() if fetch_one else cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid
        
        conn.close()
        return result
    
    except Exception as e:
        print(f"❌ Query execution failed: {e}")
        return None

if __name__ == "__main__":
    setup_database()
