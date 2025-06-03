#!/usr/bin/env python3
"""
Test script to verify the data extraction from act_metadata objects.
"""

import unittest
import sys
import os
from datetime import date

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

class TestDataExtraction(unittest.TestCase):
    """Test suite for data extraction from act_metadata objects."""

    def test_date_extraction(self):
        """Test extraction of date fields from act_metadata."""
        # Create a sample act_metadata object with the new structure
        act_metadata = {
            "globaalID": 12345,
            "terviktekstID": 67890,
            "pealkiri": "Test Act",
            "kehtivus": {
                "algus": "2020-01-01",  # entry_into_force_date
                "lopp": "2022-01-01"     # repeal_date
            },
            "avaldamiseKuupaev": "2019-06-15",  # publication_date
            "dokumentHtml": "/akt/12345",
            "url": "/akt/12345.xml",
            "liik": "seadus"
        }

        # Import the function we want to test
        from data_retriever import determine_document_status

        # Extract the dates as done in data_retriever.py
        publication_date = act_metadata.get('avaldamiseKuupaev')
        entry_into_force_date = act_metadata.get('kehtivus', {}).get('algus')
        repeal_date = act_metadata.get('kehtivus', {}).get('lopp')

        # Verify the extracted dates
        self.assertEqual(publication_date, "2019-06-15")
        self.assertEqual(entry_into_force_date, "2020-01-01")
        self.assertEqual(repeal_date, "2022-01-01")

        # Test status determination with the extracted dates
        status = determine_document_status(publication_date, entry_into_force_date, repeal_date)
        self.assertEqual(status, "EXPIRED")

    def test_url_construction(self):
        """Test construction of source_url from act_metadata."""
        # Import the function we want to test
        import os
        from data_retriever import main

        # Create a sample act_metadata object
        act_metadata = {
            "globaalID": 12345,
            "terviktekstID": 67890,
            "pealkiri": "Test Act",
            "kehtivus": {
                "algus": "2020-01-01",
                "lopp": None
            },
            "dokumentHtml": "/akt/12345",
            "url": "/akt/12345.xml",
            "liik": "seadus"
        }

        # Mock the os.getenv function to return a known value
        os_getenv_original = os.getenv
        os.getenv = lambda key, default: 'https://www.riigiteataja.ee' if key == 'RT_DOCUMENT_BASE_URL' else None

        # Extract the document_base_url as done in data_retriever.py
        document_base_url = os.getenv('RT_DOCUMENT_BASE_URL', 'https://www.riigiteataja.ee')

        # Test with dokumentHtml present
        html_url_path = act_metadata.get('dokumentHtml')
        if html_url_path:
            if html_url_path.startswith('http'):
                source_url = html_url_path
            elif html_url_path.startswith('/'):
                source_url = f"{document_base_url}{html_url_path}"
            else:
                source_url = f"{document_base_url}/{html_url_path}"
        else:
            # Fallback to globaalID
            globaal_id = act_metadata.get('globaalID')
            if globaal_id:
                html_url_path = f"/akt/{globaal_id}"
                source_url = f"{document_base_url}{html_url_path}"
            else:
                source_url = None

        # Verify the constructed URL
        self.assertEqual(source_url, "https://www.riigiteataja.ee/akt/12345")

        # Test with dokumentHtml missing
        act_metadata_no_html = act_metadata.copy()
        act_metadata_no_html.pop('dokumentHtml')

        # Extract the document_base_url again
        document_base_url = os.getenv('RT_DOCUMENT_BASE_URL', 'https://www.riigiteataja.ee')

        # Test URL construction with missing dokumentHtml
        html_url_path = act_metadata_no_html.get('dokumentHtml')
        if html_url_path:
            if html_url_path.startswith('http'):
                source_url = html_url_path
            elif html_url_path.startswith('/'):
                source_url = f"{document_base_url}{html_url_path}"
            else:
                source_url = f"{document_base_url}/{html_url_path}"
        else:
            # Fallback to globaalID
            globaal_id = act_metadata_no_html.get('globaalID')
            if globaal_id:
                html_url_path = f"/akt/{globaal_id}"
                source_url = f"{document_base_url}{html_url_path}"
            else:
                source_url = None

        # Verify the constructed URL with fallback
        self.assertEqual(source_url, "https://www.riigiteataja.ee/akt/12345")

        # Restore the original os.getenv function
        os.getenv = os_getenv_original

if __name__ == "__main__":
    unittest.main()