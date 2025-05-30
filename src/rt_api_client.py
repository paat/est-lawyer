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

def get_all_acts_for_query(initial_params: dict, max_pages: int | None = None) -> list[dict]:
    """
    Retrieve all legal acts for a given query by handling pagination.

    Parameters:
    - initial_params (dict): The initial set of query parameters
                             (e.g., {'dokument': 'seadus', 'kehtiv': 'YYYY-MM-DD', 'limiit': 100}).
                             Do not include 'leht' (page number) in this parameter.
    - max_pages (int | None): Optional. Maximum number of pages to fetch. If None, fetch all pages.

    Returns:
    - list[dict]: A list of all retrieved act metadata.
    """
    # Initialize list to store all acts
    all_acts = []

    # Start with the first page
    current_page = 1

    # Loop to handle pagination
    while True:
        # Check if we've reached the max_pages limit
        if max_pages is not None and current_page > max_pages:
            logging.info(f"Reached max_pages limit ({max_pages}). Stopping pagination.")
            break

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

def get_full_document_text(act_metadata: dict) -> tuple[str | None, str | None]:
    """
    Retrieve the full text of a legal act, either in plain text or XML format.

    Parameters:
    - act_metadata (dict): A dictionary representing a single act's metadata,
                           as retrieved from get_all_acts_for_query().
                           This dictionary should contain URLs for the document in various formats.

    Returns:
    - tuple[str | None, str | None]: A tuple containing (plain_text, xml_text).
                                     Returns (None, None) if URLs are not available or retrieval fails.
    """
    # Ensure we have a delay between requests
    time.sleep(DEFAULT_REQUEST_DELAY_SECONDS)

    # Get the act ID or title for logging purposes
    act_id = act_metadata.get('id', 'unknown')
    act_title = act_metadata.get('pealkiri', 'untitled')

    # Load the document base URL from environment variables
    document_base_url = os.getenv('RT_DOCUMENT_BASE_URL', 'https://www.riigiteataja.ee')

    # Initialize content variables
    plain_text_content = None
    xml_content = None

    # Set up headers for requests
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

    # Log the start of document retrieval
    logging.info(f"Starting full text retrieval for act ID {act_id} ('{act_title}')")

    # Try to fetch plain text content first (from dokumentTekst URL)
    try:
        text_url = act_metadata.get('dokumentTekst')
        if text_url:
            # Construct full URL if it's relative
            full_text_url = text_url if text_url.startswith('http') else f"{document_base_url}{text_url}"
            logging.info(f"Attempting to fetch plain text from: {full_text_url}")

            # Make the request
            response = requests.get(full_text_url, headers=headers, timeout=30)
            response.raise_for_status()

            # Store the content
            plain_text_content = response.text
            logging.info(f"Successfully retrieved plain text for act ID {act_id}")
        else:
            logging.info(f"No plain text URL (dokumentTekst) found for act ID {act_id}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching plain text for act ID {act_id}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error fetching plain text for act ID {act_id}: {str(e)}")

    # If no plain text was retrieved, try HTML content (from dokumentHtml URL)
    if plain_text_content is None:
        try:
            html_url = act_metadata.get('dokumentHtml')
            if html_url:
                # Construct full URL if it's relative
                full_html_url = html_url if html_url.startswith('http') else f"{document_base_url}{html_url}"
                logging.info(f"Attempting to fetch HTML content from: {full_html_url}")

                # Make the request
                response = requests.get(full_html_url, headers=headers, timeout=30)

                # Check if we got a successful response (status code < 400)
                if response.status_code < 400:
                    # Store the content
                    plain_text_content = response.text
                    logging.info(f"Successfully retrieved HTML content for act ID {act_id}")
                else:
                    logging.warning(f"HTML content retrieval failed with status code {response.status_code} for act ID {act_id}")
            else:
                logging.info(f"No HTML URL (dokumentHtml) found for act ID {act_id}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching HTML content for act ID {act_id}: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error fetching HTML content for act ID {act_id}: {str(e)}")

    # Try to fetch XML content (from dokumentXML URL)
    try:
        xml_url = act_metadata.get('dokumentXML')
        if xml_url:
            # Construct full URL if it's relative
            full_xml_url = xml_url if xml_url.startswith('http') else f"{document_base_url}{xml_url}"
            logging.info(f"Attempting to fetch XML content from: {full_xml_url}")

            # Make the request
            response = requests.get(full_xml_url, headers=headers, timeout=30)
            response.raise_for_status()

            # Store the content
            xml_content = response.text
            logging.info(f"Successfully retrieved XML content for act ID {act_id}")
        else:
            logging.info(f"No XML URL (dokumentXML) found for act ID {act_id}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching XML content for act ID {act_id}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error fetching XML content for act ID {act_id}: {str(e)}")

    # Log the result of the retrieval
    text_type = "HTML" if plain_text_content and "html" in plain_text_content.lower() else "Plain text"
    logging.info(f"Retrieval complete for act ID {act_id}: {text_type}={plain_text_content is not None}, XML={xml_content is not None}")

    # Return the retrieved content
    return plain_text_content, xml_content