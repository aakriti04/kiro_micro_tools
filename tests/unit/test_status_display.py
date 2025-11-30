"""
Unit tests for status display and result reporting functionality.

Tests Requirements: 4.1, 4.2, 4.3, 4.4
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
import sys

from src.ui import TCLFormatterUI
from src.formatter import FormattingResult, SyntaxError


class TestStatusDisplay(unittest.TestCase):
    """Test status display and result reporting."""
    
    @classmethod
    def setUpClass(cls):
        """Create QApplication instance for all tests."""
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.ui = TCLFormatterUI()
    
    def test_update_status_with_success_message(self):
        """Test that update_status displays success messages with green color."""
        # Requirement 4.2: Display success message with output file path
        message = "✓ Formatting completed successfully!\n\nOutput file: /path/to/file_formatted.tcl"
        
        self.ui.update_status(message, is_error=False)
        
        # Verify the message is displayed
        self.assertEqual(self.ui.status_output.toPlainText(), message)
        
        # Verify green color is applied (check stylesheet contains green color)
        stylesheet = self.ui.status_output.styleSheet()
        self.assertIn("#2e7d32", stylesheet)  # Green color code
    
    def test_update_status_with_error_message(self):
        """Test that update_status displays error messages with red color."""
        # Requirement 4.3: Display error message with error log path and count
        message = "✗ Syntax validation failed!\n\nFound 2 error(s)."
        
        self.ui.update_status(message, is_error=True)
        
        # Verify the message is displayed
        self.assertEqual(self.ui.status_output.toPlainText(), message)
        
        # Verify red color is applied (check stylesheet contains red color)
        stylesheet = self.ui.status_output.styleSheet()
        self.assertIn("#d32f2f", stylesheet)  # Red color code
    
    def test_processing_message_displayed(self):
        """Test that 'Processing...' is displayed when operation starts."""
        # Requirement 4.1: Display "Processing..." when operation starts
        self.ui.selected_file_path = "test.tcl"
        
        # Mock the worker thread to prevent actual formatting
        with patch('src.ui.FormatterWorker') as mock_worker:
            mock_instance = Mock()
            mock_worker.return_value = mock_instance
            
            self.ui.format_file()
            
            # Verify "Processing..." message is displayed
            self.assertEqual(self.ui.status_output.toPlainText(), "Processing...")
    
    def test_success_result_display(self):
        """Test that successful formatting displays output file path."""
        # Requirement 4.2: Display success message with output file path
        result = FormattingResult(
            success=True,
            output_path="/path/to/file_formatted.tcl",
            message="Successfully formatted"
        )
        
        self.ui._on_formatting_complete(result)
        
        # Verify success message contains output path
        status_text = self.ui.status_output.toPlainText()
        self.assertIn("✓ Formatting completed successfully!", status_text)
        self.assertIn("/path/to/file_formatted.tcl", status_text)
        
        # Verify format button is re-enabled
        self.assertTrue(self.ui.format_button.isEnabled())
    
    def test_syntax_error_result_display(self):
        """Test that syntax errors display error log path and count."""
        # Requirement 4.3: Display error message with error log path and count
        errors = [
            SyntaxError(line_number=5, message="Unmatched opening brace", error_type="brace"),
            SyntaxError(line_number=10, message="Unmatched quote", error_type="quote")
        ]
        
        result = FormattingResult(
            success=False,
            error_path="/path/to/errors.log",
            errors=errors,
            message="Syntax validation failed"
        )
        
        self.ui._on_formatting_complete(result)
        
        # Verify error message contains error count and log path
        status_text = self.ui.status_output.toPlainText()
        self.assertIn("✗ Syntax validation failed!", status_text)
        self.assertIn("Found 2 error(s)", status_text)
        self.assertIn("/path/to/errors.log", status_text)
        self.assertIn("Line 5: Unmatched opening brace", status_text)
        self.assertIn("Line 10: Unmatched quote", status_text)
        
        # Verify format button is re-enabled
        self.assertTrue(self.ui.format_button.isEnabled())
    
    def test_file_access_error_display(self):
        """Test that file access errors display descriptive message."""
        # Requirement 4.4: Display descriptive error message on file access failures
        result = FormattingResult(
            success=False,
            message="Permission denied: Cannot write to directory /protected/path"
        )
        
        self.ui._on_formatting_complete(result)
        
        # Verify error message is displayed
        status_text = self.ui.status_output.toPlainText()
        self.assertIn("✗ Formatting failed!", status_text)
        self.assertIn("Permission denied", status_text)
        
        # Verify format button is re-enabled
        self.assertTrue(self.ui.format_button.isEnabled())
    
    def test_operation_flag_cleared_after_completion(self):
        """Test that operation flag is cleared after formatting completes."""
        # Set up initial state
        self.ui.operation_in_progress = True
        
        result = FormattingResult(
            success=True,
            output_path="/path/to/file_formatted.tcl"
        )
        
        self.ui._on_formatting_complete(result)
        
        # Verify operation flag is cleared
        self.assertFalse(self.ui.operation_in_progress)


if __name__ == '__main__':
    unittest.main()
