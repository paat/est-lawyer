# est-lawyer

Est-Lawyer is a Python-based tool for retrieving and managing legal documents from the Estonian Riigi Teataja (State Gazette) API. This project allows you to search for legal acts, retrieve their metadata, and store them in a local SQLite database for further analysis.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Initializing the Database](#initializing-the-database)
  - [Fetching Legal Acts](#fetching-legal-acts)
  - [Retrieving Document Text](#retrieving-document-text)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features

- Search for legal acts using the Riigi Teataja API
- Handle pagination to retrieve all results for a query
- Store legal document metadata in a SQLite database
- Placeholder functionality for retrieving full document text
- Configurable request delays to comply with API usage policies

## Installation

1. Clone the repository:

```bash
git clone https://github.com/paat/est-lawyer.git
cd est-lawyer
```

2. Create a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root directory by copying the example file:

```bash
cp .env.example .env
```

Edit the `.env` file to set appropriate values for your environment, especially:

- `DATABASE_FILENAME` and `DATABASE_DIR` for database configuration
- `API_BASE_URL` if the API endpoint changes
- `DEFAULT_REQUEST_DELAY_SECONDS` to control the delay between API requests
- `USER_AGENT` to set a custom user agent string with your contact information

## Usage

### Initializing the Database

Before you can store legal documents, you need to initialize the SQLite database:

```bash
python src/db_setup.py
```

This will create a `legal_documents` table in the specified database file.

### Downloading Legal Acts to the Database

You can use the command line to download legal acts from the Riigi Teataja API and store them in your local database. The `data_retriever.py` script provides a convenient way to do this with various options.

#### Basic Usage

To download all laws (seadus) and store them in the database:

```bash
python src/data_retriever.py
```

#### Searching for Specific Document Types

You can specify the type of document to search for using the `--search-document-type` parameter:

```bash
# Download all regulations (määrus)
python src/data_retriever.py --search-document-type "määrus"
```

#### Searching for Documents Valid on a Specific Date

You can search for documents that are valid on a specific date using the `--search-date` parameter:

```bash
# Download all laws valid on January 1, 2024
python src/data_retriever.py --search-date "2024-01-01"
```

#### Limiting the Number of Acts

For testing purposes, you can limit the total number of acts to process:

```bash
# Download only 50 laws
python src/data_retriever.py --limit-acts 50
```

#### Limiting the Number of API Pages

You can also limit the number of pages fetched from the API:

```bash
# Download laws but only fetch 2 pages of results
python src/data_retriever.py --page-limit 2
```

#### Setting Items per Page

You can control how many items are requested per page from the API:

```bash
# Download laws with 50 items per page instead of the default 100
python src/data_retriever.py --items-per-page 50
```

#### Example: Combining Multiple Options

You can combine multiple options to customize your download:

```bash
# Download up to 100 regulations valid on January 1, 2024, with 25 items per page
python src/data_retriever.py --search-document-type "määrus" --search-date "2024-01-01" --limit-acts 100 --items-per-page 25
# Page limit example
python src/data_retriever.py --search-document-type "seadus" --search-date "2025-05-31" --page-limit 2 --items-per-page 25
```

### Fetching Legal Acts Programmatically

If you prefer to use the API client programmatically, you can use the `rt_api_client.py` module to search for legal acts. Here's an example of how to fetch all acts of a specific type:

```python
from src.rt_api_client import get_all_acts_for_query

# Define your search parameters
params = {
    'dokument': 'seadus',  # Document type (e.g., 'seadus' for laws)
    'limiit': 100,         # Number of results per page
}

# Fetch all acts matching the query
all_acts = get_all_acts_for_query(params)

# Print the number of acts retrieved
print(f"Total acts retrieved: {len(all_acts)}")
```

### Retrieving Document Text

The `get_full_document_text` function retrieves the full text of legal documents from the Riigi Teataja API. It attempts to fetch both plain text and XML content for each document.

## Testing

The project includes test scripts to verify the functionality of the API client:

- `test_rt_api_client.py`: Tests the `fetch_acts_list` and `get_all_acts_for_query` functions
- `test_get_full_document_text.py`: Tests the placeholder implementation of `get_full_document_text`

To run the tests, simply execute the test scripts:

```bash
python test_rt_api_client.py
python test_get_full_document_text.py
```

## Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and send pull requests.

## Customizing OpenHands Behavior

You can customize the behavior of OpenHands by using microagent markdown files. The microagents are stored in the `.openhands/microagents` directory.

### Directory Structure

```
.openhands/
└── microagents/
    └── repo.md          # General guidelines for the repository
    └── trigger_database.md  # Microagent triggered by database-related keywords
    └── trigger_api.md       # Microagent triggered by API-related keywords
```

### Creating Microagents

To create a new microagent:
1. Create a new markdown file in the `.openhands/microagents` directory
2. Add content with instructions and examples related to specific functionality
3. Use keywords in the filename and content to trigger the microagent

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.