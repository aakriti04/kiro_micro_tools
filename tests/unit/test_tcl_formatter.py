"""
Unit tests for TCLFormatter class.

These tests verify the core formatting functionality including file I/O,
syntax validation integration, and formatting option application.
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from formatter import TCLFormatter, FormattingResult


class TestTCLFormatter(unittest.TestCase):
    """Test cases for TCLFormatter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
    
    def _create_test_file(self, filename, content):
        """Helper to create a test file."""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    
    def test_format_valid_file(self):
        """Test formatting a valid TCL file."""
        content = """proc test {arg} {
puts $arg
}"""
        input_path = self._create_test_file('test.tcl', content)
        
        formatter = TCLFormatter()
        result = formatter.format_file(input_path)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.output_path)
        self.assertIsNone(result.error_path)
        self.assertIsNone(result.errors)
        self.assertTrue(os.path.exists(result.output_path))
    
    def test_format_invalid_file(self):
        """Test formatting a file with syntax errors."""
        content = """proc test {arg} {
puts $arg
# Missing closing brace"""
        input_path = self._create_test_file('invalid.tcl', content)
        
        formatter = TCLFormatter()
        result = formatter.format_file(input_path)
        
        self.assertFalse(result.success)
        self.assertIsNone(result.output_path)
        self.assertIsNotNone(result.error_path)
        self.assertIsNotNone(result.errors)
        self.assertTrue(len(result.errors) > 0)
        self.assertTrue(os.path.exists(result.error_path))
    
    def test_output_file_naming(self):
        """Test that output file follows naming convention."""
        content = """set x 10"""
        input_path = self._create_test_file('myfile.tcl', content)
        
        formatter = TCLFormatter()
        result = formatter.format_file(input_path)
        
        self.assertTrue(result.success)
        expected_name = 'myfile_formatted.tcl'
        actual_name = os.path.basename(result.output_path)
        self.assertEqual(expected_name, actual_name)
    
    def test_output_file_location(self):
        """Test that output file is in same directory as input."""
        content = """set x 10"""
        input_path = self._create_test_file('test.tcl', content)
        
        formatter = TCLFormatter()
        result = formatter.format_file(input_path)
        
        self.assertTrue(result.success)
        input_dir = os.path.dirname(input_path)
        output_dir = os.path.dirname(result.output_path)
        self.assertEqual(input_dir, output_dir)
    
    def test_output_file_overwriting(self):
        """Test that existing output file is overwritten."""
        content = """set x 10"""
        input_path = self._create_test_file('test.tcl', content)
        
        # Create formatter and format once
        formatter = TCLFormatter()
        result1 = formatter.format_file(input_path)
        self.assertTrue(result1.success)
        
        # Get modification time of first output
        mtime1 = os.path.getmtime(result1.output_path)
        
        # Wait a tiny bit and format again
        import time
        time.sleep(0.01)
        
        result2 = formatter.format_file(input_path)
        self.assertTrue(result2.success)
        
        # Check that file was overwritten (modification time changed)
        mtime2 = os.path.getmtime(result2.output_path)
        self.assertNotEqual(mtime1, mtime2)
    
    def test_align_set_option(self):
        """Test that align_set option is applied."""
        content = """set x 10
set variable_name 20
set y 30"""
        input_path = self._create_test_file('test.tcl', content)
        
        # Format with alignment enabled
        formatter = TCLFormatter(align_set=True)
        result = formatter.format_file(input_path)
        
        self.assertTrue(result.success)
        
        # Read output and check alignment
        with open(result.output_path, 'r') as f:
            lines = f.readlines()
        
        # All set commands should have aligned values
        # The longest variable name is "variable_name" (13 chars)
        # So other lines should have extra spaces
        self.assertIn('set x', lines[0])
        self.assertIn('set variable_name', lines[1])
        self.assertIn('set y', lines[2])
        
        # Check that x line has more spaces than variable_name line
        x_spaces = lines[0].count(' ', lines[0].index('x') + 1, lines[0].index('10'))
        var_spaces = lines[1].count(' ', lines[1].index('variable_name') + 13, lines[1].index('20'))
        self.assertGreater(x_spaces, var_spaces)
    
    def test_expand_lists_option(self):
        """Test that expand_lists option is applied."""
        # Create a long list that exceeds 80 characters
        content = """set long_list {item1 item2 item3 item4 item5 item6 item7 item8 item9 item10 item11 item12}"""
        input_path = self._create_test_file('test.tcl', content)
        
        # Format with list expansion enabled
        formatter = TCLFormatter(expand_lists=True)
        result = formatter.format_file(input_path)
        
        self.assertTrue(result.success)
        
        # Read output and check that list was expanded
        with open(result.output_path, 'r') as f:
            lines = f.readlines()
        
        # Should have multiple lines (more than 1)
        self.assertGreater(len(lines), 1)
        
        # First line should end with opening brace
        self.assertTrue(lines[0].strip().endswith('{'))
    
    def test_strict_indent_option(self):
        """Test that strict_indent option is passed to IndentationEngine."""
        content = """proc test {arg} {
puts $arg
}"""
        input_path = self._create_test_file('test.tcl', content)
        
        # Format with strict indentation
        formatter = TCLFormatter(strict_indent=True)
        result = formatter.format_file(input_path)
        
        self.assertTrue(result.success)
        # Just verify it doesn't crash - strict mode behavior is tested in IndentationEngine tests
    
    def test_error_log_format(self):
        """Test that error log follows correct format."""
        content = """proc test {arg} {
puts $arg
# Missing closing brace"""
        input_path = self._create_test_file('test.tcl', content)
        
        formatter = TCLFormatter()
        result = formatter.format_file(input_path)
        
        self.assertFalse(result.success)
        
        # Read error log
        with open(result.error_path, 'r') as f:
            error_lines = f.readlines()
        
        # Each error should start with "Line X:"
        for line in error_lines:
            self.assertTrue(line.startswith('Line '))
            self.assertIn(':', line)
    
    def test_error_log_location(self):
        """Test that error log is in same directory as input."""
        content = """proc test {arg} {
# Missing closing brace"""
        input_path = self._create_test_file('test.tcl', content)
        
        formatter = TCLFormatter()
        result = formatter.format_file(input_path)
        
        self.assertFalse(result.success)
        
        input_dir = os.path.dirname(input_path)
        error_dir = os.path.dirname(result.error_path)
        self.assertEqual(input_dir, error_dir)
        
        # Error log should be named "errors.log"
        error_name = os.path.basename(result.error_path)
        self.assertEqual('errors.log', error_name)
    
    def test_comment_preservation(self):
        """Test that comments are preserved during formatting."""
        content = """# This is a comment
set x 10
# Another comment"""
        input_path = self._create_test_file('test.tcl', content)
        
        formatter = TCLFormatter()
        result = formatter.format_file(input_path)
        
        self.assertTrue(result.success)
        
        # Read output and check comments are present
        with open(result.output_path, 'r') as f:
            output = f.read()
        
        self.assertIn('# This is a comment', output)
        self.assertIn('# Another comment', output)
    
    def test_empty_file(self):
        """Test formatting an empty file."""
        content = ""
        input_path = self._create_test_file('empty.tcl', content)
        
        formatter = TCLFormatter()
        result = formatter.format_file(input_path)
        
        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(result.output_path))
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        formatter = TCLFormatter()
        result = formatter.format_file('nonexistent.tcl')
        
        self.assertFalse(result.success)
        self.assertIn('error', result.message.lower())
    
    def test_encoding_detection(self):
        """Test that file encoding is properly detected."""
        content = """# UTF-8 content with special chars: café, naïve
set message "Hello, 世界" """
        input_path = self._create_test_file('utf8.tcl', content)
        
        formatter = TCLFormatter()
        result = formatter.format_file(input_path)
        
        self.assertTrue(result.success)
        
        # Read output and verify special characters are preserved
        with open(result.output_path, 'r', encoding='utf-8') as f:
            output = f.read()
        
        self.assertIn('café', output)
        self.assertIn('世界', output)


if __name__ == '__main__':
    unittest.main()
