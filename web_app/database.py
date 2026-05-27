import sqlite3
import os
from datetime import datetime

# Define database path inside the web_app directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nutrition.db')

def get_db_connection():
    """
    Establish a connection to the SQLite database and configure it to return Row objects.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize the database tables for user targets and food history if they don't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table to store user targets based on a unique session/device ID
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_targets (
            session_id TEXT PRIMARY KEY,
            target_calories INTEGER DEFAULT 2000,
            target_protein INTEGER DEFAULT 50,
            target_carbs INTEGER DEFAULT 250,
            target_fat INTEGER DEFAULT 70
        )
    ''')
    
    # Table to store the history of consumed food mapped to a session
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            food_name TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbs REAL NOT NULL,
            fat REAL NOT NULL,
            consumed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_target(session_id):
    """
    Fetch the nutrition target for a specific user session.
    If it doesn't exist, create a default target and return it.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM user_targets WHERE session_id = ?', (session_id,))
    target = cursor.fetchone()
    
    if target is None:
        # Create default fallback target if the user is new
        cursor.execute('''
            INSERT INTO user_targets (session_id) VALUES (?)
        ''', (session_id,))
        conn.commit()
        
        cursor.execute('SELECT * FROM user_targets WHERE session_id = ?', (session_id,))
        target = cursor.fetchone()
        
    conn.close()
    return target

def set_user_target(session_id, calories, protein, carbs, fat):
    """
    Update the manual nutrition target for a specific user session.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_targets (session_id, target_calories, target_protein, target_carbs, target_fat)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            target_calories=excluded.target_calories,
            target_protein=excluded.target_protein,
            target_carbs=excluded.target_carbs,
            target_fat=excluded.target_fat
    ''', (session_id, calories, protein, carbs, fat))
    
    conn.commit()
    conn.close()

def add_food_log(session_id, food_name, calories, protein, carbs, fat):
    """
    Insert a newly consumed food item into the user's history log.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO food_history (session_id, food_name, calories, protein, carbs, fat)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session_id, food_name, calories, protein, carbs, fat))
    
    conn.commit()
    conn.close()

def get_daily_history(session_id, target_date=None):
    """
    Retrieve all food consumed by a user on a specific date (defaults to today).
    """
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQLite datetime functions let us match the date part of the timestamp
    cursor.execute('''
        SELECT * FROM food_history 
        WHERE session_id = ? AND date(consumed_at) = ?
        ORDER BY consumed_at DESC
    ''', (session_id, target_date))
    
    records = cursor.fetchall()
    conn.close()
    return records

def delete_food_log(session_id, log_id):
    """
    Delete a specific food history record, ensuring it belongs to the active session.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM food_history WHERE id = ? AND session_id = ?
    ''', (log_id, session_id))
    
    conn.commit()
    conn.close()

# Initialize DB on script load to ensure tables exist
if __name__ != '__main__':
    init_db()
