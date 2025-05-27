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

### Fetching Legal Acts

You can use the `rt_api_client.py` module to search for legal acts. Here's an example of how to fetch all acts of a specific type:

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

The `get_full_document_text` function is currently a placeholder and logs that the functionality is not yet implemented. You can extend this function to retrieve the full text of legal documents from the Riigi Teataja API.

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.