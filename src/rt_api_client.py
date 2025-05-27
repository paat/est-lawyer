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

def get_all_acts_for_query(initial_params: dict) -> list[dict]:
    """
    Retrieve all legal acts for a given query by handling pagination.

    Parameters:
    - initial_params (dict): The initial set of query parameters
                             (e.g., {'dokument': 'seadus', 'kehtiv': 'YYYY-MM-DD', 'limiit': 100}).
                             Do not include 'leht' (page number) in this parameter.

    Returns:
    - list[dict]: A list of all retrieved act metadata.
    """
    # Initialize list to store all acts
    all_acts = []

    # Start with the first page
    current_page = 1

    # Loop to handle pagination
    while True:
        # Create a copy of initial_params and add/update the 'leht' parameter
        params_with_page = initial_params.copy()
        params_with_page['leht'] = current_page

        # Fetch acts for the current page
        page_data = fetch_acts_list(params_with_page)

        # If fetch failed, log the issue and return what we've got so far
        if page_data is None:
            logging.warning(f"No data returned for page {current_page}. Stopping pagination.")
            break

        # Extract the list of acts from the response
        # Based on the API response structure, the acts are under the 'aktid' key
        acts_on_page = page_data.get('aktid', [])

        # If no acts are returned, we've reached the end
        if not acts_on_page:
            logging.info(f"No more results found after page {current_page}. Total acts retrieved: {len(all_acts)}")
            break

        # Add the acts from this page to our total list
        all_acts.extend(acts_on_page)

        # Log progress
        logging.info(f"Page {current_page}: Retrieved {len(acts_on_page)} acts. Total: {len(all_acts)}")

        # Increment the page number
        current_page += 1

        # Optional: Check if we've reached the last page
        # This depends on the API's response structure
        # For example, if the number of results is less than the limit, it's likely the last page
        limit = params_with_page.get('limiit', 100)
        if len(acts_on_page) < limit:
            logging.info(f"Page {current_page - 1} returned fewer results than the limit, assuming last page.")
            break

    # Return all retrieved acts
    return all_acts