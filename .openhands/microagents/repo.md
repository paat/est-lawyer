# General Guidelines for est-lawyer

This microagent provides general guidelines for using the est-lawyer project.

## Key Features

- Search for legal acts using the Riigi Teataja API
- Store legal document metadata in a SQLite database
- Retrieve full document text

## Basic Usage

To get started with est-lawyer, follow these steps:

1. Initialize the database:
   ```bash
   python src/db_setup.py
   ```

2. Download legal acts:
   ```bash
   python src/data_retriever.py
   ```

## Customization

You can customize the behavior of est-lawyer by modifying the configuration in the `.env` file.