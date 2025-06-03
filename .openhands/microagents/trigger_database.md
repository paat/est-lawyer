# Database Operations

This microagent is triggered by keywords related to database operations in est-lawyer.

## Initializing the Database

To initialize the SQLite database, run:
```bash
python src/db_setup.py
```

## Database Configuration

You can configure the database by modifying the `.env` file:
- `DATABASE_FILENAME`: Name of the database file
- `DATABASE_DIR`: Directory where the database file is stored