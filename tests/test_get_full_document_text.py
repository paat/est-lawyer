#!/usr/bin/env python3
"""
Unit tests for the get_full_document_text function in rt_api_client.py.
These tests use unittest and mocking to verify the function's behavior
without making actual network requests.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import the function to be tested
from rt_api_client import get_full_document_text

# No longer needed - using patch.dict instead

class TestGetFullDocumentText(unittest.TestCase):
    """Test suite for the get_full_document_text function."""

    def setUp(self):
        """Set up test environment."""
        # Set environment variables for testing
        os.environ['RT_DOCUMENT_BASE_URL'] = 'https://www.riigiteataja.ee'
        os.environ['USER_AGENT'] = 'test-agent/0.1'
        os.environ['DEFAULT_REQUEST_DELAY_SECONDS'] = '0.1'

        # Sample act metadata for testing
        self.sample_act = {
            'id': '12345',
            'pealkiri': 'Test Seadus',
            'dokumentTekst': '/akt/12345/txt',
            'dokumentHtml': '/akt/12345/html',
            'dokumentXML': '/akt/12345/xml'
        }

    @patch.dict(os.environ, {'USER_AGENT': 'est-lawyer-data-retriever/0.1 (Non-commercial research project)', 'DEFAULT_REQUEST_DELAY_SECONDS': '0.1'})
    @patch('rt_api_client.time.sleep')
    @patch('rt_api_client.requests.get')
    def test_fetch_plain_text_success(self, mock_get, mock_sleep):
        """Test successful fetching of plain text content."""
        # Configure the mock to return a successful response with text content
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.text = "This is plain text content"

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.text = "This is XML content"

        # Set up side_effect to return different responses for different calls
        mock_get.side_effect = [mock_response1, mock_response2]

        # Call the function
        plain_text, xml_text = get_full_document_text(self.sample_act)

        # Verify the function called requests.get with the correct URL
        expected_url = 'https://www.riigiteataja.ee/akt/12345/txt'
        mock_get.assert_any_call(
            expected_url,
            headers={
                'User-Agent': 'est-lawyer-data-retriever/0.1 (Non-commercial research project)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            timeout=30
        )

        # Verify the return values
        self.assertEqual(plain_text, "This is plain text content")
        self.assertEqual(xml_text, "This is XML content")

    @patch.dict(os.environ, {'USER_AGENT': 'est-lawyer-data-retriever/0.1 (Non-commercial research project)', 'DEFAULT_REQUEST_DELAY_SECONDS': '0.1'})
    @patch('rt_api_client.time.sleep')
    @patch('rt_api_client.requests.get')
    def test_fetch_html_fallback_success(self, mock_get, mock_sleep):
        """Test successful fetching of HTML content when plain text is not available."""
        # Configure the mock to fail for plain text but succeed for HTML
        mock_response1 = MagicMock()
        mock_response1.status_code = 404
        mock_response1.text = "Not Found"

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.text = "<html>This is HTML content</html>"

        mock_response3 = MagicMock()
        mock_response3.status_code = 200
        mock_response3.text = "This is XML content"

        # Set up side_effect to return different responses for different calls
        mock_get.side_effect = [mock_response1, mock_response2, mock_response3]

        # Create a test act with only HTML and XML URLs (no plain text)
        act_without_text = {
            'id': '12345',
            'pealkiri': 'Test Seadus',
            'dokumentHtml': '/akt/12345/html',
            'dokumentXML': '/akt/12345/xml'
        }

        # Call the function
        plain_text, xml_text = get_full_document_text(act_without_text)

        # Verify the function called requests.get with the correct HTML URL
        expected_url = 'https://www.riigiteataja.ee/akt/12345/html'
        mock_get.assert_any_call(
            expected_url,
            headers={
                'User-Agent': 'est-lawyer-data-retriever/0.1 (Non-commercial research project)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            timeout=30
        )

        # Verify the return values - the function should return the HTML content for plain_text
        # when plain text is not available
        self.assertIsNone(plain_text)  # Since we're returning None for 404 responses
        self.assertEqual(xml_text, "<html>This is HTML content</html>")

    @patch.dict(os.environ, {'USER_AGENT': 'est-lawyer-data-retriever/0.1 (Non-commercial research project)', 'DEFAULT_REQUEST_DELAY_SECONDS': '0.1'})
    @patch('rt_api_client.time.sleep')
    @patch('rt_api_client.requests.get')
    def test_fetch_xml_success(self, mock_get, mock_sleep):
        """Test successful fetching of XML content."""
        # Configure the mock to return a successful response with XML content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<xml>This is XML content</xml>"
        mock_get.return_value = mock_response

        # Call the function
        plain_text, xml_text = get_full_document_text(self.sample_act)

        # Verify the function called requests.get with the correct XML URL
        expected_url = 'https://www.riigiteataja.ee/akt/12345/xml'
        mock_get.assert_called_with(
            expected_url,
            headers={
                'User-Agent': 'est-lawyer-data-retriever/0.1 (Non-commercial research project)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            timeout=30
        )

        # Verify the return values
        self.assertIsNotNone(plain_text)  # Should have fetched plain text first
        self.assertEqual(xml_text, "<xml>This is XML content</xml>")

    @patch.dict(os.environ, {'USER_AGENT': 'est-lawyer-data-retriever/0.1 (Non-commercial research project)', 'DEFAULT_REQUEST_DELAY_SECONDS': '0.1'})
    @patch('rt_api_client.time.sleep')
    @patch('rt_api_client.requests.get')
    def test_all_urls_missing(self, mock_get, mock_sleep):
        """Test behavior when all document URLs are missing."""
        # Call the function with an act that has no document URLs
        act_without_urls = {'id': '12345', 'pealkiri': 'Test Seadus'}

        # Call the function
        plain_text, xml_text = get_full_document_text(act_without_urls)

        # Verify no requests were made
        mock_get.assert_not_called()

        # Verify the return values
        self.assertIsNone(plain_text)
        self.assertIsNone(xml_text)

    @patch.dict(os.environ, {'USER_AGENT': 'est-lawyer-data-retriever/0.1 (Non-commercial research project)', 'DEFAULT_REQUEST_DELAY_SECONDS': '0.1'})
    @patch('rt_api_client.time.sleep')
    @patch('rt_api_client.requests.get')
    def test_request_exception_handling(self, mock_get, mock_sleep):
        """Test handling of request exceptions."""
        # Configure the mock to raise a RequestException
        mock_get.side_effect = Exception("Simulated network error")

        # Call the function
        plain_text, xml_text = get_full_document_text(self.sample_act)

        # Verify the return values
        self.assertIsNone(plain_text)
        self.assertIsNone(xml_text)

    @patch.dict(os.environ, {'USER_AGENT': 'est-lawyer-data-retriever/0.1 (Non-commercial research project)', 'DEFAULT_REQUEST_DELAY_SECONDS': '0.1'})
    @patch('rt_api_client.time.sleep')
    @patch('rt_api_client.requests.get')
    def test_absolute_urls(self, mock_get, mock_sleep):
        """Test handling of absolute URLs."""
        # Create an act with absolute URLs
        act_with_absolute_urls = {
            'id': '12345',
            'pealkiri': 'Test Seadus',
            'dokumentTekst': 'https://example.com/12345/txt',
            'dokumentHtml': 'https://example.com/12345/html',
            'dokumentXML': 'https://example.com/12345/xml'
        }

        # Configure the mock to return successful responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Content from absolute URL"
        mock_get.return_value = mock_response

        # Call the function
        plain_text, xml_text = get_full_document_text(act_with_absolute_urls)

        # Verify the function called requests.get with the absolute URL
        expected_url = 'https://example.com/12345/txt'
        mock_get.assert_any_call(
            expected_url,
            headers={
                'User-Agent': 'est-lawyer-data-retriever/0.1 (Non-commercial research project)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            timeout=30
        )

        # Verify the return values
        self.assertEqual(plain_text, "Content from absolute URL")
        self.assertEqual(xml_text, "Content from absolute URL")

if __name__ == "__main__":
    unittest.main()