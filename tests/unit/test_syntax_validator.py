"""
Unit tests for SyntaxValidator class.
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from formatter import SyntaxValidator, SyntaxError


class TestSyntaxValidator(unittest.TestCase):
    """Test cases for SyntaxValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SyntaxValidator()
    
    def test_valid_code_no_errors(self):
        """Test that valid code produces no errors."""
        lines = [
            'set x 10',
            'if {$x > 5} {',
            '    puts "x is greater than 5"',
            '}'
        ]
        errors = self.validator.validate(lines)
        self.assertEqual(len(errors), 0)
    
    def test_unmatched_opening_brace(self):
        """Test detection of unmatched opening brace."""
        lines = [
            'if {$x > 5} {',
            '    puts "hello"',
            # Missing closing brace
        ]
        errors = self.validator.validate(lines)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_type, 'brace')
        self.assertEqual(errors[0].line_number, 1)
        self.assertIn('Unmatched opening brace', errors[0].message)
    
    def test_unmatched_closing_brace(self):
        """Test detection of unexpected closing brace."""
        lines = [
            'set x 10',
            '}',  # Unexpected closing brace
        ]
        errors = self.validator.validate(lines)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_type, 'brace')
        self.assertEqual(errors[0].line_number, 2)
        self.assertIn('Unexpected closing', errors[0].message)
    
    def test_unmatched_opening_quote(self):
        """Test detection of unmatched opening quote."""
        lines = [
            'set x "hello',
            # Missing closing quote
        ]
        errors = self.validator.validate(lines)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_type, 'quote')
        self.assertEqual(errors[0].line_number, 1)
        self.assertIn('Unmatched opening quote', errors[0].message)
    
    def test_unmatched_closing_quote(self):
        """Test detection of unexpected closing quote."""
        lines = [
            'set x 10',
            'puts "',  # Unexpected closing quote on next line would be caught
        ]
        errors = self.validator.validate(lines)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_type, 'quote')
    
    def test_nested_braces(self):
        """Test validation of nested braces."""
        lines = [
            'if {$x > 5} {',
            '    if {$y > 10} {',
            '        puts "nested"',
            '    }',
            '}'
        ]
        errors = self.validator.validate(lines)
        self.assertEqual(len(errors), 0)
    
    def test_escaped_characters(self):
        """Test that escaped characters are handled correctly."""
        lines = [
            'set x "hello \\" world"',
            'set y "path\\\\to\\\\file"'
        ]
        errors = self.validator.validate(lines)
        self.assertEqual(len(errors), 0)
    
    def test_braces_in_strings(self):
        """Test that braces inside strings don't affect validation."""
        lines = [
            'set x "this has { and } in it"',
            'puts "another {brace}"'
        ]
        errors = self.validator.validate(lines)
        self.assertEqual(len(errors), 0)
    
    def test_comments_ignored(self):
        """Test that comment lines are ignored."""
        lines = [
            '# This is a comment with { unmatched brace',
            'set x 10',
            '# Another comment with " unmatched quote'
        ]
        errors = self.validator.validate(lines)
        self.assertEqual(len(errors), 0)
    
    def test_multiple_errors(self):
        """Test detection of multiple errors."""
        lines = [
            'if {$x > 5} {',
            'set y "unclosed string',
            # Missing closing brace and quote
        ]
        errors = self.validator.validate(lines)
        self.assertEqual(len(errors), 2)
        error_types = {e.error_type for e in errors}
        self.assertIn('brace', error_types)
        self.assertIn('quote', error_types)
    
    def test_line_continuation(self):
        """Test that line continuations are handled correctly."""
        lines = [
            'set long_string "This is a long string that \\',
            'continues on the next line and \\',
            'ends here"'
        ]
        errors = self.validator.validate(lines)
        self.assertEqual(len(errors), 0)


if __name__ == '__main__':
    unittest.main()
