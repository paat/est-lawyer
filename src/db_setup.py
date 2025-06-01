import sqlite3
import os
from dotenv import load_dotenv

def get_db_path():
    """Get the database directory and file path from environment variables."""
    database_dir = os.getenv('DATABASE_DIR', './data')
    database_filename = os.getenv('DATABASE_FILENAME', 'riigiteataja_docs.sqlite')

    # Construct the full path to the database file
    database_path = os.path.join(database_dir, database_filename)

    return database_dir, database_path

def initialize_database():
    """Initialize the SQLite database with the legal_documents table."""
    # Load environment variables from .env file
    load_dotenv()

    # Get the database directory and file path
    database_dir, database_path = get_db_path()

    # Ensure the database directory exists
    os.makedirs(database_dir, exist_ok=True)

    # Connect to the SQLite database (creates the file if it doesn't exist)
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Define the SQL statement to create the legal_documents table
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS legal_documents (
        full_text_id INTEGER PRIMARY KEY,      -- From API 'terviktekstID'
        rt_unique_id TEXT UNIQUE NOT NULL,      -- From API 'globaalID'
        title TEXT NOT NULL,                -- From API 'pealkiri'
        document_type TEXT NOT NULL,        -- From API 'liik' (e.g., 'SEADUS', 'MÄÄRUS')
        text_content_plain TEXT,            -- Plain text or HTML content from get_full_document_text()
        text_content_xml TEXT,              -- XML content from get_full_document_text()
        publication_date TEXT,              -- From API 'avaldamiseKuupaev' (YYYY-MM-DD)
        entry_into_force_date TEXT,         -- From API 'joustumiseKuupaev' (YYYY-MM-DD)
        repeal_date TEXT,                   -- From API 'kehtivuseLoppKp' (YYYY-MM-DD, can be NULL)
        status TEXT NOT NULL CHECK(status IN ('VALID', 'EXPIRED', 'PENDING_VALIDITY', 'UNKNOWN')), -- Derived
        source_url TEXT,                    -- Full URL to the document (e.g., HTML version)
        api_response_json TEXT,             -- JSON string of the act's metadata from the API list response
        retrieved_at TEXT NOT NULL,         -- ISO timestamp (YYYY-MM-DD HH:MM:SS) of when record was created
        last_checked_at TEXT NOT NULL       -- ISO timestamp (YYYY-MM-DD HH:MM:SS) of when record was last checked/created
    )
    '''

    # Drop the existing table (if any) and recreate it to ensure the new schema
    cursor.execute("DROP TABLE IF EXISTS legal_documents")
    cursor.execute(create_table_sql)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Print a success message
    print(f"Database '{os.path.basename(database_path)}' initialized successfully with 'legal_documents' table in '{database_dir}'. The table uses 'rt_unique_id' as the primary key.")

if __name__ == "__main__":
    initialize_database()