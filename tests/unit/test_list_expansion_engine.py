"""
Unit tests for ListExpansionEngine.

Tests the list expansion functionality including detection, expansion,
and preservation of formatting.
"""

import unittest
from src.formatter import ListExpansionEngine


class TestListExpansionEngine(unittest.TestCase):
    """Test cases for ListExpansionEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = ListExpansionEngine()
    
    def test_long_list_detection(self):
        """Test detection of lists exceeding 80 characters."""
        # Requirement 9.1: Detect list structures exceeding 80 characters
        long_list = "set mylist {item1 item2 item3 item4 item5 item6 item7 item8 item9 item10 item11 item12}"
        self.assertTrue(self.engine._should_expand_list(long_list))
        self.assertGreater(len(long_list), 80)
    
    def test_short_list_not_detected(self):
        """Test that short lists are not detected for expansion."""
        # Requirement 9.4: Preserve original formatting when disabled
        short_list = "set x {a b c}"
        self.assertFalse(self.engine._should_expand_list(short_list))
        self.assertLess(len(short_list), 80)
    
    def test_list_expansion_formatting(self):
        """Test that expanded lists have proper formatting."""
        # Requirement 9.2: Place each list element on a separate line with increased indentation
        long_list = "set mylist {item1 item2 item3 item4 item5 item6 item7 item8 item9 item10 item11 item12}"
        expanded = self.engine._expand_list(long_list)
        
        # Should have: opening line + items + closing line
        self.assertGreater(len(expanded), 3)
        
        # First line should end with opening brace
        self.assertTrue(expanded[0].strip().endswith('{'))
        
        # Last line should start with closing brace
        self.assertTrue(expanded[-1].strip().startswith('}'))
        
        # Middle lines should be indented (2 spaces)
        for line in expanded[1:-1]:
            self.assertTrue(line.startswith('  '))
    
    def test_closing_brace_placement(self):
        """Test that closing brace is at original indentation level."""
        # Requirement 9.3: Place closing brace at original indentation level
        long_list = "    set mylist {item1 item2 item3 item4 item5 item6 item7 item8 item9 item10 item11 item12}"
        expanded = self.engine._expand_list(long_list)
        
        # Original indentation is 4 spaces
        original_indent = '    '
        
        # Closing brace should be at original indentation
        self.assertTrue(expanded[-1].startswith(original_indent + '}'))
    
    def test_preserve_original_when_short(self):
        """Test that short lists are preserved in original format."""
        # Requirement 9.4: Preserve original formatting when disabled
        lines = [
            "set x {a b c}",
            "set y {1 2 3}",
            "# Comment",
            "set z {short}"
        ]
        
        result = self.engine.expand_long_lists(lines)
        
        # Should have same number of lines (no expansion)
        self.assertEqual(len(result), len(lines))
        
        # Lines should be unchanged
        for i, line in enumerate(lines):
            self.assertEqual(result[i], line)
    
    def test_mixed_long_and_short_lists(self):
        """Test processing of mixed long and short lists."""
        lines = [
            "set short {a b}",
            "set long {item1 item2 item3 item4 item5 item6 item7 item8 item9 item10 item11 item12}",
            "set another_short {x y z}"
        ]
        
        result = self.engine.expand_long_lists(lines)
        
        # Should have more lines due to expansion of the long list
        self.assertGreater(len(result), len(lines))
        
        # First line should be unchanged (short list)
        self.assertEqual(result[0], lines[0])
        
        # Second line should be expanded (starts with "set long {")
        self.assertTrue(result[1].strip().startswith('set long {'))
    
    def test_comment_lines_not_expanded(self):
        """Test that comment lines are not treated as lists."""
        comment = "# This is a comment with {braces} and more than 80 characters in total length"
        self.assertFalse(self.engine._should_expand_list(comment))
    
    def test_empty_list_not_expanded(self):
        """Test that empty lists are not expanded."""
        empty_list = "set x {}"
        self.assertFalse(self.engine._should_expand_list(empty_list))
    
    def test_single_item_list_not_expanded(self):
        """Test that single-item lists without spaces are not expanded."""
        single_item = "set x {$variable}"
        self.assertFalse(self.engine._should_expand_list(single_item))
    
    def test_parse_list_items(self):
        """Test parsing of list items."""
        list_content = "item1 item2 item3 item4"
        items = self.engine._parse_list_items(list_content)
        
        self.assertEqual(len(items), 4)
        self.assertEqual(items[0], "item1")
        self.assertEqual(items[1], "item2")
        self.assertEqual(items[2], "item3")
        self.assertEqual(items[3], "item4")
    
    def test_parse_list_items_with_nested_braces(self):
        """Test parsing of list items with nested braces."""
        list_content = "item1 {nested item} item3"
        items = self.engine._parse_list_items(list_content)
        
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0], "item1")
        self.assertEqual(items[1], "{nested item}")
        self.assertEqual(items[2], "item3")
    
    def test_parse_list_items_with_quotes(self):
        """Test parsing of list items with quoted strings."""
        list_content = 'item1 "quoted item" item3'
        items = self.engine._parse_list_items(list_content)
        
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0], "item1")
        self.assertEqual(items[1], '"quoted item"')
        self.assertEqual(items[2], "item3")
    
    def test_indentation_preserved_in_expansion(self):
        """Test that original indentation is preserved in expanded lists."""
        indented_list = "  set mylist {item1 item2 item3 item4 item5 item6 item7 item8 item9 item10 item11 item12}"
        expanded = self.engine._expand_list(indented_list)
        
        # First line should have original indentation (2 spaces)
        self.assertTrue(expanded[0].startswith('  '))
        
        # Item lines should have original + 2 more spaces (4 total)
        for line in expanded[1:-1]:
            self.assertTrue(line.startswith('    '))
        
        # Closing brace should have original indentation (2 spaces)
        self.assertTrue(expanded[-1].startswith('  }'))
    
    def test_list_with_trailing_content(self):
        """Test expansion of list with content after closing brace."""
        list_with_trailing = "set x {item1 item2 item3 item4 item5 item6 item7 item8 item9 item10 item11 item12} ;# comment"
        expanded = self.engine._expand_list(list_with_trailing)
        
        # Last line should include the trailing content
        self.assertTrue(expanded[-1].strip().endswith(';# comment'))
    
    def test_empty_lines_input(self):
        """Test that empty input is handled correctly."""
        result = self.engine.expand_long_lists([])
        self.assertEqual(result, [])
    
    def test_no_lists_in_input(self):
        """Test processing of input with no lists."""
        lines = [
            "puts hello",
            "# Comment",
            "set x 5"
        ]
        
        result = self.engine.expand_long_lists(lines)
        self.assertEqual(result, lines)


if __name__ == '__main__':
    unittest.main()
