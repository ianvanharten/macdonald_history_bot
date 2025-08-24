import sqlite3
import os
import secrets
import json

# Use the same database file as the usage logger for simplicity
DB_PATH = os.path.join(os.path.dirname(__file__), 'monitoring.db')

def setup_share_database(conn: sqlite3.Connection):
    """
    Creates the 'shares' table in the database if it doesn't exist.
    This should be called on application startup.
    """
    try:
        cursor = conn.cursor()
        # Ensure WAL mode is enabled, in case this runs before the logger setup.
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS shares (
            share_id TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT
        )
        """)
        conn.commit()
        print("[INFO] Share link database setup complete.")
    except sqlite3.Error as e:
        print(f"[ERROR] Share database setup failed: {e}")

def create_share_link(conn: sqlite3.Connection, question: str, answer: str, sources: list) -> str:
    """
    Saves a Q&A pair to the database and returns a unique share ID.
    """
    try:
        cursor = conn.cursor()

        # Generate a new, unique share_id that is not already in the database
        while True:
            share_id = secrets.token_urlsafe(6)  # Generates an ~8 character URL-safe string
            cursor.execute("SELECT 1 FROM shares WHERE share_id = ?", (share_id,))
            if cursor.fetchone() is None:
                break  # The ID is unique, we can exit the loop

        # Convert the list of sources into a JSON string for storage
        sources_json = json.dumps(sources)

        cursor.execute(
            "INSERT INTO shares (share_id, question, answer, sources) VALUES (?, ?, ?, ?)",
            (share_id, question, answer, sources_json)
        )
        conn.commit()
        return share_id
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to create share link: {e}")
        return None

def get_shared_link(conn: sqlite3.Connection, share_id: str):
    """
    Retrieves a shared Q&A pair from the database by its ID.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer, sources FROM shares WHERE share_id = ?", (share_id,))
        record = cursor.fetchone()

        if record:
            question, answer, sources_json = record
            # Convert the sources from a JSON string back into a Python list
            sources = json.loads(sources_json) if sources_json else []
            return {"question": question, "answer": answer, "sources": sources}
        else:
            return None # No record found for this ID
    except (sqlite3.Error, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to retrieve or parse shared link: {e}")
        return None