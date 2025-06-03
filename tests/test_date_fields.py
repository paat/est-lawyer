#!/usr/bin/env python3
"""
Test script to verify the date field extraction and source URL construction changes.
"""

import unittest
import sys
import os
from datetime import date

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import the function we want to test
from data_retriever import determine_document_status

class TestDateFields(unittest.TestCase):
    """Test suite for date field extraction and status determination."""

    def test_status_with_valid_dates(self):
        """Test status determination with valid dates."""
        # Test case 1: Document is valid (entry into force date is in the past)
        entry_into_force_date = "2020-01-01"
        status = determine_document_status(None, entry_into_force_date, None)
        self.assertEqual(status, "VALID")

        # Test case 2: Document is pending validity (entry into force date is in the future)
        future_date = (date.today().replace(year=date.today().year + 1)).isoformat()
        status = determine_document_status(None, future_date, None)
        self.assertEqual(status, "PENDING_VALIDITY")

        # Test case 3: Document is expired (repeal date is in the past)
        repeal_date = "2020-01-01"
        status = determine_document_status(None, "2019-01-01", repeal_date)
        self.assertEqual(status, "EXPIRED")

        # Test case 4: Document with publication date but no other dates
        publication_date = "2020-01-01"
        status = determine_document_status(publication_date, None, None)
        self.assertEqual(status, "UNKNOWN")

    def test_status_with_none_dates(self):
        """Test status determination with None dates."""
        # Test case: All dates are None
        status = determine_document_status(None, None, None)
        self.assertEqual(status, "UNKNOWN")

if __name__ == "__main__":
    unittest.main()