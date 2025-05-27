import requests
import time
import os
import json
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load constants from environment variables
API_BASE_URL = os.getenv('API_BASE_URL', "https://www.riigiteataja.ee/api/oigusakt_otsing/1/otsi")
DEFAULT_REQUEST_DELAY_SECONDS = float(os.getenv('DEFAULT_REQUEST_DELAY_SECONDS', 2.0))
USER_AGENT = os.getenv('USER_AGENT', "est-lawyer-data-retriever/0.1 (Non-commercial research project)")

def fetch_acts_list(api_params: dict) -> dict | None:
    """
    Fetch a list of legal acts from the API based on the provided parameters.

    Parameters:
    - api_params (dict): A dictionary of query parameters to send to the API
                         (e.g., {'leht': 1, 'limiit': 10, 'dokument': 'seadus', 'kehtiv': '2024-05-01'}).

    Returns:
    - dict | None: The parsed JSON response if successful, None otherwise.
    """
    # Ensure we have a delay between requests
    time.sleep(DEFAULT_REQUEST_DELAY_SECONDS)

    try:
        # Construct the full request URL
        request_url = f"{API_BASE_URL}"

        # Log the request being made
        logging.info(f"Making request to {request_url} with params: {json.dumps(api_params)}")

        # Set headers including User-Agent
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/json'
        }

        # Make the GET request to the API
        response = requests.get(request_url, params=api_params, headers=headers, timeout=30)

        # Check for HTTP errors
        response.raise_for_status()

        # Parse the JSON response
        response_data = response.json()

        # Log success
        logging.info(f"Successfully fetched data for params: {json.dumps(api_params)}")

        # Return the parsed JSON
        return response_data

    except requests.exceptions.RequestException as e:
        # Log any request exceptions
        logging.error(f"Request failed: {str(e)}")
    except json.JSONDecodeError as e:
        # Log JSON decoding errors
        logging.error(f"Error parsing JSON response: {str(e)}")
    except Exception as e:
        # Log any other exceptions
        logging.error(f"An unexpected error occurred: {str(e)}")

    # Return None if there was an error
    return None