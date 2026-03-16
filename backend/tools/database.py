import sqlite3
import os
from datetime import datetime
from services.auth_service import encrypt_data, decrypt_data

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "studio.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            hashed_password TEXT,
            full_name TEXT,
            provider TEXT DEFAULT 'local',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            title TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Migration: Add user_id column to sessions if it doesn't exist
    cursor.execute("PRAGMA table_info(sessions)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'user_id' not in columns:
        cursor.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT REFERENCES users(id)")
    
    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            content TEXT,
            is_ai BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    """)
    
    conn.commit()
    conn.close()

def create_session(session_id, user_id, title="New Conversation"):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO sessions (id, user_id, title) VALUES (?, ?, ?)", (session_id, user_id, title))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Already exists
    finally:
        conn.close()

def update_session_title(session_id, title):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))
    conn.commit()
    conn.close()

def save_message(session_id, content, is_ai):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Encrypt content before saving
    encrypted_content = encrypt_data(content)
    cursor.execute(
        "INSERT INTO messages (session_id, content, is_ai) VALUES (?, ?, ?)",
        (session_id, encrypted_content, is_ai)
    )
    conn.commit()
    conn.close()

def get_sessions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions

def get_messages(session_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if session belongs to user
    cursor.execute("SELECT user_id FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    if not row or row['user_id'] != user_id:
        conn.close()
        return []

    cursor.execute(
        "SELECT content, is_ai FROM messages WHERE session_id = ? ORDER BY created_at ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    messages = []
    for row in rows:
        msg = dict(row)
        msg['content'] = decrypt_data(msg['content'])
        messages.append(msg)
    conn.close()
    return messages

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(user_id, email, hashed_password, full_name, provider='local'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (id, email, hashed_password, full_name, provider) VALUES (?, ?, ?, ?, ?)",
        (user_id, email, hashed_password, full_name, provider)
    )
    conn.commit()
    conn.close()

# Initialize database on import
init_db()
