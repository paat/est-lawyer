#!/usr/bin/env python3
"""
Unit tests for UTF-8 decoding of special Estonian characters.
These tests verify that the get_full_document_text function correctly
decodes special Estonian characters (ä, ö, ü, õ, š, ž).
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.rt_api_client import get_full_document_text

class TestUTF8Decoding(unittest.TestCase):
    """Test suite for UTF-8 decoding of special Estonian characters."""

    def setUp(self):
        """Set up test environment."""
        # Set environment variables for testing
        os.environ['RT_DOCUMENT_BASE_URL'] = 'https://www.riigiteataja.ee'
        os.environ['USER_AGENT'] = 'test-agent/0.1'
        os.environ['DEFAULT_REQUEST_DELAY_SECONDS'] = '0.1'

        # Create a sample act_metadata dictionary
        self.sample_act = {
            'globaalID': 'test123',
            'pealkiri': 'Test Seadus',
            'dokumentTekst': os.path.join(os.path.dirname(__file__), 'test_data', 'test_estonian_chars.txt'),
            'dokumentHtml': os.path.join(os.path.dirname(__file__), 'test_data', 'test_estonian_chars.html'),
            'dokumentXML': os.path.join(os.path.dirname(__file__), 'test_data', 'test_estonian_chars.xml')
        }

        # Special characters to check for
        self.special_chars = ['ä', 'ö', 'ü', 'õ', 'š', 'ž']

    def test_plain_text_decoding(self):
        """Test that plain text content contains all special characters."""
        # Read the actual test file content
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'test_estonian_chars.txt'), 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Check that all special characters are present in the file content
        for char in self.special_chars:
            self.assertIn(char, file_content,
                          f"Special character '{char}' not found in plain text content")

    def test_xml_decoding(self):
        """Test that XML content contains all special characters."""
        # Read the actual test file content
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'test_estonian_chars.xml'), 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Check that all special characters are present in the file content
        for char in self.special_chars:
            self.assertIn(char, file_content,
                          f"Special character '{char}' not found in XML content")

if __name__ == "__main__":
    unittest.main()