#!/usr/bin/env python3
"""
Test script to verify UTF-8 decoding of special Estonian characters.
This script fetches a document that contains special characters (ä, ö, ü, õ, š, ž)
and checks if they are correctly decoded.
"""

import os
import sys
import logging
from src.rt_api_client import get_full_document_text

# Configure logging to display messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Set environment variables for testing
    os.environ['RT_DOCUMENT_BASE_URL'] = 'https://www.riigiteataja.ee'
    os.environ['USER_AGENT'] = 'test-agent/0.1'
    os.environ['DEFAULT_REQUEST_DELAY_SECONDS'] = '0.1'

    # Create a sample act_metadata dictionary with a known document that contains special characters
    # Use local file paths
    sample_act = {
        'globaalID': 'test123',
        'pealkiri': 'Test Seadus',
        'dokumentTekst': '/workspace/est-lawyer/test_data/test_estonian_chars.txt',
        'dokumentHtml': '/workspace/est-lawyer/test_data/test_estonian_chars.html',
        'dokumentXML': '/workspace/est-lawyer/test_data/test_estonian_chars.xml'
    }

    # Call the function with the sample data
    plain_text, xml_text = get_full_document_text(sample_act)

    # Check for special Estonian characters in the retrieved content
    special_chars = ['ä', 'ö', 'ü', 'õ', 'š', 'ž']
    has_special_chars = True

    if plain_text:
        print("Checking plain text content for special characters:")
        for char in special_chars:
            if char in plain_text:
                print(f"  Found '{char}' in plain text")
            else:
                has_special_chars = False
                print(f"  Missing '{char}' in plain text")

    if xml_text:
        print("\nChecking XML content for special characters:")
        for char in special_chars:
            if char in xml_text:
                print(f"  Found '{char}' in XML")
            else:
                has_special_chars = False
                print(f"  Missing '{char}' in XML")

    if has_special_chars:
        print("\nTest PASSED: Special characters were correctly decoded")
    else:
        print("\nTest FAILED: Some special characters were not correctly decoded")

    print("\nTest completed")

if __name__ == "__main__":
    main()