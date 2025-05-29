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
                        help="Optional. Limit the total number of acts to process (for testing purposes).")
    parser.add_argument("--page-limit", type=int, default=None,
                        help="Optional. Limit the number of pages fetched from the API for each query (for testing purposes).")
    parser.add_argument("--items-per-page", type=int, default=100,
                        help="Optional. The number of items to request per page from the API ('limiit' parameter). Default: 100.")

    args = parser.parse_args()

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

        # Fetch all acts for the query
        all_acts = get_all_acts_for_query(initial_params)

        # Process acts with pagination limit if specified
        if args.page_limit:
            all_acts = all_acts[:args.page_limit * args.items_per_page]

        # Limit acts if specified
        if args.limit_acts and args.limit_acts < len(all_acts):
            all_acts = all_acts[:args.limit_acts]

        # Process each act
        total_processed = 0
        total_inserted = 0
        total_ignored = 0

        for act_metadata in all_acts:
            total_processed += 1
            act_id = act_metadata.get('id')
            act_title = act_metadata.get('pealkiri', 'untitled')

            logging.info(f"Processing act {total_processed}/{len(all_acts)}: ID={act_id}, Title='{act_title}'")

            try:
                # Fetch full text
                plain_text, xml_text = get_full_document_text(act_metadata)

                # Extract fields
                rt_unique_id = act_metadata.get('id')
                title = act_metadata.get('pealkiri', '')
                document_type = act_metadata.get('liik', '')
                publication_date = act_metadata.get('avaldamiseKuupaev')
                entry_into_force_date = act_metadata.get('joustumiseKuupaev')
                repeal_date = act_metadata.get('kehtivuseLoppKp')

                # Determine status
                status = determine_document_status(
                    publication_date,
                    entry_into_force_date,
                    repeal_date
                )

                # Construct source URL
                document_base_url = os.getenv('RT_DOCUMENT_BASE_URL', 'https://www.riigiteataja.ee')
                html_url = act_metadata.get('dokumentHtml', '')
                source_url = f"{document_base_url}{html_url}" if html_url.startswith('/') else html_url

                # Prepare data for insertion
                data = (
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

                # Insert into database
                cursor.execute('''
                    INSERT OR IGNORE INTO legal_documents (
                        rt_unique_id, title, document_type, text_content_plain, text_content_xml,
                        publication_date, entry_into_force_date, repeal_date, status, source_url,
                        api_response_json, retrieved_at, last_checked_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data)

                # Check if insertion was successful (row count)
                if cursor.rowcount > 0:
                    total_inserted += 1
                    logging.info(f"Inserted act ID={act_id}")
                else:
                    total_ignored += 1
                    logging.info(f"Ignored act ID={act_id} (already exists)")

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
        logging.info(f"Processing complete. Total acts: {total_processed}, Inserted: {total_inserted}, Ignored: {total_ignored}")

    except Exception as e:
        logging.error(f"Critical error: {str(e)}")

if __name__ == "__main__":
    main()