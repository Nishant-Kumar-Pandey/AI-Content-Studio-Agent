import os
import psycopg2
import psycopg2.extras
from services.auth_service import encrypt_data, decrypt_data

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id),
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            session_id TEXT REFERENCES sessions(id),
            content TEXT,
            is_ai BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def create_session(session_id, user_id, title="New Conversation"):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO sessions (id, user_id, title) VALUES (%s, %s, %s)",
            (session_id, user_id, title)
        )
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()  # Required for PostgreSQL after an error
    finally:
        conn.close()


def update_session_title(session_id, title):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sessions SET title = %s WHERE id = %s",
        (title, session_id)
    )
    conn.commit()
    conn.close()


def save_message(session_id, content, is_ai):
    conn = get_db_connection()
    cursor = conn.cursor()
    encrypted_content = encrypt_data(content)
    cursor.execute(
        "INSERT INTO messages (session_id, content, is_ai) VALUES (%s, %s, %s)",
        (session_id, encrypted_content, is_ai)
    )
    conn.commit()
    conn.close()


def get_sessions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT * FROM sessions WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    sessions = cursor.fetchall()
    conn.close()
    return sessions


def get_messages(session_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # Check if session belongs to user
    cursor.execute(
        "SELECT user_id FROM sessions WHERE id = %s",
        (session_id,)
    )
    row = cursor.fetchone()
    if not row or row['user_id'] != user_id:
        conn.close()
        return []

    cursor.execute(
        "SELECT content, is_ai FROM messages WHERE session_id = %s ORDER BY created_at ASC",
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
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def create_user(user_id, email, hashed_password, full_name, provider='local'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (id, email, hashed_password, full_name, provider) VALUES (%s, %s, %s, %s, %s)",
        (user_id, email, hashed_password, full_name, provider)
    )
    conn.commit()
    conn.close()


# Initialize database on import
if DATABASE_URL:
    init_db()
