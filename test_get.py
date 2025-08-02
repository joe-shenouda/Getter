import unittest
import tkinter as tk
from unittest.mock import patch
import requests # Required for requests.exceptions.RequestException
import time # Required for testing delay
from get import Application

class TestApplication(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = Application(master=self.root)

    def tearDown(self):
        self.root.destroy()

    @patch('get.requests.get')
    def test_send_gets_success(self, mock_get):
        # Configure the mock for a successful response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = "Success"

        self.app.url_entry.insert(0, "http://example.com")
        self.app.num_gets_entry.insert(0, "1")
        self.app.delay_entry.insert(0, "0")

        self.app.start_gets()
        if self.app.thread:
            self.app.thread.join() # Wait for the thread to finish

        self.assertEqual(self.app.successful_gets, 1)
        self.assertEqual(self.app.errors, 0)
        # Check if status was updated (optional, but good for GUI testing)
        # self.assertIn("Successful GETs: 1", self.app.status_label.cget("text"))
        # self.assertIn("Errors: 0", self.app.status_label.cget("text"))

    @patch('get.requests.get')
    def test_send_gets_invalid_url(self, mock_get):
        # Configure the mock to raise an exception for an invalid URL
        mock_get.side_effect = requests.exceptions.RequestException("Test invalid URL")

        self.app.url_entry.insert(0, "invalid-url")
        self.app.num_gets_entry.insert(0, "1")
        self.app.delay_entry.insert(0, "0")

        self.app.start_gets()
        if self.app.thread:
            self.app.thread.join()

        self.assertEqual(self.app.successful_gets, 0)
        self.assertEqual(self.app.errors, 1)
        # self.assertIn("Successful GETs: 0", self.app.status_label.cget("text"))
        # self.assertIn("Errors: 1", self.app.status_label.cget("text"))

    @patch('get.requests.get')
    def test_send_gets_delay(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = "Success"

        self.app.url_entry.insert(0, "http://example.com")
        self.app.num_gets_entry.insert(0, "2")  # 2 GETs
        self.app.delay_entry.insert(0, "100") # 100 ms delay

        start_time = time.time()
        self.app.start_gets()
        if self.app.thread:
            self.app.thread.join()
        end_time = time.time()

        self.assertEqual(self.app.successful_gets, 2)
        self.assertEqual(self.app.errors, 0)

        elapsed_time = end_time - start_time
        # There's one delay period between the two requests.
        # Allow for some tolerance (e.g., 0.09s to 0.15s for a 100ms delay)
        # due to system overhead and timing inaccuracies.
        self.assertTrue(0.09 <= elapsed_time < 0.2, f"Elapsed time {elapsed_time}s was not close to the expected 0.1s delay.")


    @patch('get.requests.get')
    def test_send_gets_custom_port(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.text = "Success on custom port"

        self.app.url_entry.insert(0, "http://example.com")
        self.app.port_entry.insert(0, "8080") # Custom port
        self.app.num_gets_entry.insert(0, "1")
        self.app.delay_entry.insert(0, "0")

        self.app.start_gets()
        if self.app.thread:
            self.app.thread.join()

        self.assertEqual(self.app.successful_gets, 1)
        self.assertEqual(self.app.errors, 0)

        # Check that requests.get was called with the URL including the port
        mock_get.assert_called_once_with("http://example.com:8080/", timeout=5)

    def test_log_single_message(self):
        self.app.log("Test message 1")
        log_content = self.app.log_text.get(1.0, tk.END)
        self.assertEqual(log_content, "Test message 1\n")

    def test_log_multiple_messages(self):
        self.app.log("Test message 1")
        self.app.log("Test message 2")
        log_content = self.app.log_text.get(1.0, tk.END)
        self.assertEqual(log_content, "Test message 1\nTest message 2\n")

    @patch('get.requests.get')
    def test_send_gets_non_200_status(self, mock_get):
        # Configure the mock for a non-200 response
        mock_response = mock_get.return_value
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        self.app.url_entry.insert(0, "http://example.com/notfound")
        self.app.num_gets_entry.insert(0, "1")
        self.app.delay_entry.insert(0, "0")

        self.app.start_gets()
        if self.app.thread:
            self.app.thread.join()

        self.assertEqual(self.app.successful_gets, 0)
        self.assertEqual(self.app.errors, 1)
        # self.assertIn("Successful GETs: 0", self.app.status_label.cget("text"))
        # self.assertIn("Errors: 1", self.app.status_label.cget("text"))


if __name__ == '__main__':
    unittest.main()
