import sqlite3
import os
from datetime import datetime

# Define the path for the SQLite database file within the 'api' directory
DB_PATH = os.path.join(os.path.dirname(__file__), 'monitoring.db')

def setup_database():
    """
    Sets up the database connection and creates the 'logs' table if it doesn't exist.
    This function should be called once when the FastAPI application starts.
    """
    try:
        # The connection will create the database file if it doesn't exist.
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()

        # Enable Write-Ahead Logging (WAL) for better concurrency.
        # This is crucial for web applications where multiple requests can occur at once.
        cursor.execute("PRAGMA journal_mode=WAL;")

        # Create the 'logs' table with the defined schema.
        # 'IF NOT EXISTS' prevents an error if the table is already there.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_ip TEXT,
            question TEXT,
            is_successful BOOLEAN,
            llm_response TEXT,
            llm_model_used TEXT,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            latency_ms INTEGER,
            error_message TEXT
        )
        """)
        conn.commit()
        print("[INFO] Usage monitoring database setup complete.")
    except sqlite3.Error as e:
        print(f"[ERROR] Database setup failed: {e}")
    finally:
        if conn:
            conn.close()

def log_request(
    conn: sqlite3.Connection,  # Add SQLite connection object as a parameter
    user_ip: str,
    question: str,
    is_successful: bool,
    llm_response: str = None,
    llm_model_used: str = None,
    prompt_tokens: int = None,
    completion_tokens: int = None,
    total_tokens: int = None,
    latency_ms: int = None,
    error_message: str = None
):
    """
    Logs the details of a single API request to the provided SQLite database connection.
    """
    try:
        cursor = conn.cursor()

        # Insert a new record into the logs table.
        # Using placeholders (?) is a security best practice to prevent SQL injection.
        cursor.execute("""
        INSERT INTO logs (
            user_ip, question, is_successful, llm_response, llm_model_used,
            prompt_tokens, completion_tokens, total_tokens, latency_ms, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_ip, question, is_successful, llm_response, llm_model_used,
            prompt_tokens, completion_tokens, total_tokens, latency_ms, error_message
        ))

        conn.commit()
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to log request to database: {e}")
