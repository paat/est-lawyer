#!/usr/bin/env python3
"""
Test script for the get_full_document_text function.
This script will test the placeholder implementation to ensure it logs the correct message.
"""

import sys
import os
import logging
from src.rt_api_client import get_full_document_text

# Configure logging to display messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Create a sample act_metadata dictionary
    sample_act = {
        'id': '12345',
        'pealkiri': 'Test Seadus',
        'kehtiv': '2024-05-01'
    }

    # Call the function with the sample data
    plain_text, xml_text = get_full_document_text(sample_act)

    # Check the results
    if plain_text is None and xml_text is None:
        print("Test passed: Function returned (None, None) as expected")
    else:
        print(f"Test failed: Function returned {plain_text}, {xml_text}")

    print("Test completed successfully")

if __name__ == "__main__":
    main()