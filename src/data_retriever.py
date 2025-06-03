import sqlite3
import json
import logging
import os
import datetime
from datetime import datetime, date
import argparse
from dotenv import load_dotenv
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rt_api_client import get_all_acts_for_query, get_full_document_text
from db_setup import get_db_path, initialize_database

def setup_logging():
    """Set up basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def determine_document_status(publication_date_str, entry_into_force_date_str, repeal_date_str) -> str:
    """
    Determine the status of a document based on its dates.

    Args:
        publication_date_str: Publication date as YYYY-MM-DD string
        entry_into_force_date_str: Entry into force date as YYYY-MM-DD string
        repeal_date_str: Repeal date as YYYY-MM-DD string (can be None)

    Returns:
        Status string ('VALID', 'EXPIRED', 'PENDING_VALIDITY', 'UNKNOWN')
    """
    try:
        current_date = date.today()

        # Parse dates if they exist
        parsed_publication_date = datetime.strptime(publication_date_str, '%Y-%m-%d').date() if publication_date_str else None
        parsed_entry_into_force_date = datetime.strptime(entry_into_force_date_str, '%Y-%m-%d').date() if entry_into_force_date_str else None
        parsed_repeal_date = datetime.strptime(repeal_date_str, '%Y-%m-%d').date() if repeal_date_str else None

        # Determine status based on dates
        if parsed_repeal_date and parsed_repeal_date < current_date:
            return 'EXPIRED'
        elif parsed_entry_into_force_date and parsed_entry_into_force_date <= current_date:
            return 'VALID'
        elif parsed_entry_into_force_date and parsed_entry_into_force_date > current_date:
            return 'PENDING_VALIDITY'
        else:
            return 'UNKNOWN'
    except ValueError as e:
        logging.error(f"Error parsing dates for status determination: {e}")
        return 'UNKNOWN'

def main():
    """Main function to retrieve legal acts and store them in the database."""
    # Load environment variables
    load_dotenv()

    # Set up logging
    setup_logging()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Retrieve legal acts from Riigi Teataja API and store them in a database.")
    parser.add_argument("--search-document-type", type=str, default="seadus",
                        help="The type of document to search for (e.g., 'seadus', 'määrus). Default: 'seadus'.")
    parser.add_argument("--search-date", type=str, default=None,
                        help="Optional. A specific date for which to find valid documents (YYYY-MM-DD).")
    parser.add_argument("--limit-acts", type=int, default=None,
                        help="Optional. Limit the total number of acts to process and the number of pages fetched (for testing purposes).")
    parser.add_argument("--page-limit", type=int, default=None,
                        help="Optional. Limit the number of pages fetched from the API for each query (for testing purposes).")
    parser.add_argument("--items-per-page", type=int, default=100,
                        help="Optional. The number of items to request per page from the API ('limiit' parameter). Default: 100.")
    parser.add_argument("--overwrite-full-text", action='store_true',
                        help="Optional. If specified, update the full text of existing records in the database. Default: False.")

    args = parser.parse_args()

    # Log the status of the overwrite-full-text flag
    logging.info(f"Overwrite full text flag set to: {args.overwrite_full_text}")

    # Get the database path
    _, database_path = get_db_path()

    # Ensure the database is initialized
    initialize_database()

    # Construct initial parameters for API query
    initial_params = {
        'dokument': args.search_document_type,
        'limiit': args.items_per_page
    }

    # Add search date if provided
    if args.search_date:
        initial_params['kehtiv'] = args.search_date

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Calculate max_pages based on limit_acts if specified
        if args.limit_acts:
            # Calculate the number of pages needed for the limit
            max_pages = (args.limit_acts + args.items_per_page - 1) // args.items_per_page
            # Fetch acts with the calculated page limit
            all_acts = get_all_acts_for_query(initial_params, max_pages=max_pages)
            # Apply the limit to the acts
            all_acts = all_acts[:args.limit_acts]
        else:
            # Fetch all acts for the query, with optional page limit
            all_acts = get_all_acts_for_query(initial_params, max_pages=args.page_limit)
            # Process acts with pagination limit if specified
            if args.page_limit:
                all_acts = all_acts[:args.page_limit * args.items_per_page]

        # Process each act
        total_processed = 0
        total_inserted = 0
        total_ignored = 0

        for act_metadata in all_acts:
            total_processed += 1
            act_id = act_metadata.get('globaalID')
            act_title = act_metadata.get('pealkiri', 'untitled')

            logging.info(f"Processing act {total_processed}/{len(all_acts)}: ID={act_id}, Title='{act_title}'")

            try:
                # Get the unique ID for this act
                rt_unique_id = act_metadata.get('globaalID')

                # Check if the act already exists in the database
                cursor.execute("SELECT full_text_id FROM legal_documents WHERE rt_unique_id = ?", (rt_unique_id,))
                existing_record = cursor.fetchone()

                if not existing_record:
                    # Case 1: Act ID NOT in Database - Fetch all data and insert new record
                    logging.info(f"Act ID {rt_unique_id} not found in database. Proceeding with full data retrieval and insertion.")

                    # Fetch full text
                    plain_text, xml_text = get_full_document_text(act_metadata)

                    # Extract fields and determine status
                    title = act_metadata.get('pealkiri', '')
                    document_type = act_metadata.get('liik', '')
                    publication_date = act_metadata.get('avaldamiseKuupaev')
                    entry_into_force_date = act_metadata.get('kehtivus', {}).get('algus')
                    repeal_date = act_metadata.get('kehtivus', {}).get('lopp')
                    status = determine_document_status(publication_date, entry_into_force_date, repeal_date)

                    # Construct source URL
                    document_base_url = os.getenv('RT_DOCUMENT_BASE_URL', 'https://www.riigiteataja.ee')
                    html_url_path = act_metadata.get('dokumentHtml')
                    if not html_url_path:
                        globaal_id = act_metadata.get('globaalID')
                        if globaal_id:
                            html_url_path = f"/akt/{globaal_id}"
                    if html_url_path:
                        if html_url_path.startswith('http'):
                            source_url = html_url_path
                        elif html_url_path.startswith('/'):
                            source_url = f"{document_base_url}{html_url_path}"
                        else:
                            source_url = f"{document_base_url}/{html_url_path}"
                    else:
                        source_url = None

                    # Prepare data for insertion
                    full_text_id = act_metadata.get('terviktekstID')
                    data = (
                        full_text_id,
                        rt_unique_id,
                        title,
                        document_type,
                        plain_text,
                        xml_text,
                        publication_date,
                        entry_into_force_date,
                        repeal_date,
                        status,
                        source_url,
                        json.dumps(act_metadata),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )

                    # Insert new record
                    cursor.execute('''
                        INSERT INTO legal_documents (
                            full_text_id, rt_unique_id, title, document_type, text_content_plain, text_content_xml,
                            publication_date, entry_into_force_date, repeal_date, status, source_url,
                            api_response_json, retrieved_at, last_checked_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', data)

                    # Check if insertion was successful
                    if cursor.rowcount > 0:
                        total_inserted += 1
                        logging.info(f"Inserted new act full_text_id={full_text_id} rt_unique_id={rt_unique_id}")
                    else:
                        logging.error(f"Failed to insert new act ID={rt_unique_id}")
                else:
                    # Case 2: Act ID ALREADY EXISTS in Database
                    if not args.overwrite_full_text:
                        # Subcase 2.1: --overwrite-full-text is FALSE (Default) - Skip this act
                        logging.info(f"Act ID {rt_unique_id} already exists in database. Skipping update as --overwrite-full-text is not specified.")
                        total_ignored += 1
                    else:
                        # Subcase 2.2: --overwrite-full-text is TRUE - Update only full text field
                        logging.info(f"Act ID {rt_unique_id} exists. --overwrite-full-text specified. Fetching and updating full text field only.")

                        # Fetch only the full text content
                        plain_text, xml_text = get_full_document_text(act_metadata)

                        # Update only the full_text fields and updated_at timestamp
                        cursor.execute('''
                            UPDATE legal_documents
                            SET text_content_plain = ?,
                                text_content_xml = ?,
                                last_checked_at = CURRENT_TIMESTAMP
                            WHERE rt_unique_id = ?
                        ''', (plain_text, xml_text, rt_unique_id))

                        # Check if update was successful
                        if cursor.rowcount > 0:
                            total_inserted += 1
                            logging.info(f"Updated full text for existing act rt_unique_id={rt_unique_id}")
                        else:
                            logging.error(f"Failed to update act ID={rt_unique_id}")

            except Exception as e:
                logging.error(f"Error processing act ID={act_id}: {str(e)}")

            # Commit periodically to avoid losing too much data on crash
            if total_processed % 10 == 0:
                conn.commit()

        # Final commit
        conn.commit()

        # Close the database connection
        conn.close()

        # Log summary
        overwrite_flag = "with" if args.overwrite_full_text else "without"
        logging.info(f"Processing complete {overwrite_flag} --overwrite-full-text flag. Total acts: {total_processed}, Inserted/Updated: {total_inserted}, Ignored: {total_ignored}")

    except Exception as e:
        logging.error(f"Critical error: {str(e)}")

if __name__ == "__main__":
    main()