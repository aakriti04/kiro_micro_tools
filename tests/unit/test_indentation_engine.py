"""
Unit tests for IndentationEngine class.
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from formatter import IndentationEngine


class TestIndentationEngine(unittest.TestCase):
    """Test cases for IndentationEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = IndentationEngine()
    
    def test_simple_block_indentation(self):
        """Test basic indentation with opening and closing braces."""
        lines = [
            'if {$x > 5} {',
            'puts "hello"',
            '}'
        ]
        result = self.engine.apply_indentation(lines)
        self.assertEqual(result[0], 'if {$x > 5} {')
        self.assertEqual(result[1], '  puts "hello"')
        self.assertEqual(result[2], '}')
    
    def test_nested_blocks(self):
        """Test nested block indentation."""
        lines = [
            'if {$x > 5} {',
            'if {$y > 10} {',
            'puts "nested"',
            '}',
            '}'
        ]
        result = self.engine.apply_indentation(lines)
        self.assertEqual(result[0], 'if {$x > 5} {')
        self.assertEqual(result[1], '  if {$y > 10} {')
        self.assertEqual(result[2], '    puts "nested"')
        self.assertEqual(result[3], '  }')
        self.assertEqual(result[4], '}')
    
    def test_indent_size_two_spaces(self):
        """Test that indentation uses exactly 2 spaces per level."""
        lines = [
            'proc test {} {',
            'set x 10',
            '}'
        ]
        result = self.engine.apply_indentation(lines)
        # First level should have 2 spaces
        self.assertTrue(result[1].startswith('  '))
        self.assertFalse(result[1].startswith('   '))  # Not 3 spaces
        self.assertFalse(result[1].startswith('    '))  # Not 4 spaces
    
    def test_closing_brace_decreases_indent(self):
        """Test that lines starting with closing brace have decreased indentation."""
        lines = [
            'if {$x > 5} {',
            'puts "hello"',
            '}',
            'puts "after"'
        ]
        result = self.engine.apply_indentation(lines)
        self.assertEqual(result[2], '}')
        self.assertEqual(result[3], 'puts "after"')
    
    def test_empty_lines_preserved(self):
        """Test that empty lines are preserved."""
        lines = [
            'set x 10',
            '',
            'set y 20'
        ]
        result = self.engine.apply_indentation(lines)
        self.assertEqual(result[1], '')
    
    def test_comment_lines_preserved(self):
        """Test that comment lines are preserved with original indentation."""
        lines = [
            '# This is a comment',
            'set x 10',
            '# Another comment'
        ]
        result = self.engine.apply_indentation(lines)
        self.assertEqual(result[0], '# This is a comment')
        self.assertEqual(result[2], '# Another comment')
    
    def test_block_keywords_indentation(self):
        """Test indentation with various block keywords."""
        keywords = ['if', 'foreach', 'while', 'switch', 'proc']
        for keyword in keywords:
            lines = [
                f'{keyword} {{condition}} {{',
                'puts "inside"',
                '}'
            ]
            result = self.engine.apply_indentation(lines)
            self.assertEqual(result[1], '  puts "inside"')
    
    def test_multiple_braces_on_line(self):
        """Test handling of multiple braces on a single line."""
        lines = [
            'if {$x > 5} { puts "hello" }',
            'set y 20'
        ]
        result = self.engine.apply_indentation(lines)
        # Net change is 0 (one open, one close)
        self.assertEqual(result[1], 'set y 20')
    
    def test_braces_in_strings_ignored(self):
        """Test that braces inside strings don't affect indentation."""
        lines = [
            'set x "this has { in it"',
            'set y 20'
        ]
        result = self.engine.apply_indentation(lines)
        # Should not increase indentation
        self.assertEqual(result[1], 'set y 20')
    
    def test_strict_mode_disabled(self):
        """Test that strict mode is disabled by default."""
        engine = IndentationEngine(strict_mode=False)
        self.assertFalse(engine.strict_mode)
    
    def test_strict_mode_enabled(self):
        """Test that strict mode can be enabled."""
        engine = IndentationEngine(strict_mode=True)
        self.assertTrue(engine.strict_mode)


if __name__ == '__main__':
    unittest.main()
