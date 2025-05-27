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
        document_id TEXT PRIMARY KEY,
        rt_unique_id TEXT UNIQUE,
        title TEXT NOT NULL,
        document_type TEXT NOT NULL,
        text_content_plain TEXT,
        text_content_xml TEXT,
        publication_date TEXT,  -- Store dates as ISO format strings (YYYY-MM-DD)
        entry_into_force_date TEXT,
        repeal_date TEXT,
        status TEXT NOT NULL CHECK(status IN ('VALID', 'EXPIRED', 'PENDING_VALIDITY', 'UNKNOWN')),
        source_url TEXT UNIQUE,
        api_response_json TEXT,
        retrieved_at TEXT NOT NULL,  -- Store timestamps as ISO format strings (YYYY-MM-DD HH:MM:SS)
        last_checked_at TEXT NOT NULL
    )
    '''

    # Execute the SQL statement
    cursor.execute(create_table_sql)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Print a success message
    print(f"Database '{os.path.basename(database_path)}' initialized successfully with 'legal_documents' table in '{database_dir}'.")

if __name__ == "__main__":
    initialize_database()