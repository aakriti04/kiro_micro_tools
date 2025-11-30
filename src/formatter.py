"""
TCL Formatter and Syntax Validator

This module provides the core formatting and validation functionality for TCL files.
"""

import os
import chardet
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path


@dataclass
class SyntaxError:
    """Represents a syntax error found during validation."""
    line_number: int
    message: str
    error_type: str  # 'brace', 'quote', 'other'


@dataclass
class StackFrame:
    """Represents an item on the validation stack."""
    char: str  # '{', '}', '"'
    line_number: int
    position: int


class SyntaxValidator:
    """
    Validates TCL syntax using stack-based approach for brace and quote matching.
    
    This validator detects unmatched braces and quotes by maintaining a stack
    of opening characters and matching them with closing characters.
    """
    
    def __init__(self):
        """Initialize validator with empty stack."""
        self.stack: List[StackFrame] = []
        self.errors: List[SyntaxError] = []
    
    def validate(self, lines: List[str]) -> List[SyntaxError]:
        """
        Validate braces and quotes using stack-based approach.
        
        Args:
            lines: List of code lines to validate
            
        Returns:
            List of SyntaxError objects describing any errors found
        """
        self.stack = []
        self.errors = []
        
        # Handle line continuations by joining lines ending with backslash
        processed_lines = self._handle_line_continuations(lines)
        
        for line_num, line in processed_lines:
            self._process_line(line, line_num)
        
        # Check for unmatched opening characters at end of file
        self._check_remaining_stack()
        
        return self.errors
    
    def _handle_line_continuations(self, lines: List[str]) -> List[Tuple[int, str]]:
        """
        Handle line continuations (lines ending with backslash).
        
        Args:
            lines: List of code lines
            
        Returns:
            List of tuples (line_number, processed_line)
        """
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            line_num = i + 1
            
            # Check if line ends with backslash (continuation)
            while i < len(lines) - 1 and line.rstrip().endswith('\\'):
                # Remove the backslash and join with next line
                line = line.rstrip()[:-1] + lines[i + 1]
                i += 1
            
            result.append((line_num, line))
            i += 1
        
        return result
    
    def _process_line(self, line: str, line_num: int):
        """
        Process a single line, tracking braces and quotes.
        
        Args:
            line: The line to process
            line_num: The line number (1-indexed)
        """
        # Skip comment lines
        stripped = line.strip()
        if stripped.startswith('#'):
            return
        
        in_string = False
        i = 0
        
        while i < len(line):
            char = line[i]
            
            # Handle escaped characters
            if char == '\\' and i + 1 < len(line):
                i += 2  # Skip the escaped character
                continue
            
            # Handle quotes
            if char == '"':
                if in_string:
                    # Closing quote
                    error = self._pop('"', line_num, i)
                    if error:
                        self.errors.append(error)
                    in_string = False
                else:
                    # Opening quote
                    self._push('"', line_num, i)
                    in_string = True
            
            # Handle braces (only when not in string)
            elif not in_string:
                if char == '{':
                    self._push('{', line_num, i)
                elif char == '}':
                    error = self._pop('}', line_num, i)
                    if error:
                        self.errors.append(error)
            
            i += 1
    
    def _push(self, char: str, line_num: int, position: int):
        """
        Push opening character onto stack.
        
        Args:
            char: The character to push ('{' or '"')
            line_num: The line number where the character appears
            position: The position in the line
        """
        frame = StackFrame(char=char, line_number=line_num, position=position)
        self.stack.append(frame)
    
    def _pop(self, char: str, line_num: int, position: int) -> Optional[SyntaxError]:
        """
        Pop and validate matching character.
        
        Args:
            char: The closing character ('}' or '"')
            line_num: The line number where the character appears
            position: The position in the line
            
        Returns:
            SyntaxError if there's a mismatch, None otherwise
        """
        if not self.stack:
            # Unexpected closing character with no matching opening
            error_type = 'brace' if char == '}' else 'quote'
            return SyntaxError(
                line_number=line_num,
                message=f"Unexpected closing {char} with no matching opening",
                error_type=error_type
            )
        
        frame = self.stack.pop()
        
        # Check if the characters match
        if char == '}' and frame.char != '{':
            # Mismatched: expected closing brace but found quote on stack
            self.stack.append(frame)  # Put it back
            return SyntaxError(
                line_number=line_num,
                message=f"Unexpected closing brace, expected closing quote from line {frame.line_number}",
                error_type='brace'
            )
        elif char == '"' and frame.char != '"':
            # Mismatched: expected closing quote but found brace on stack
            self.stack.append(frame)  # Put it back
            return SyntaxError(
                line_number=line_num,
                message=f"Unexpected closing quote, expected closing brace from line {frame.line_number}",
                error_type='quote'
            )
        
        return None
    
    def _check_remaining_stack(self):
        """
        Check for unmatched opening characters after processing all lines.
        Reports errors for each unmatched opening character.
        """
        for frame in self.stack:
            if frame.char == '{':
                error = SyntaxError(
                    line_number=frame.line_number,
                    message=f"Unmatched opening brace",
                    error_type='brace'
                )
            else:  # frame.char == '"'
                error = SyntaxError(
                    line_number=frame.line_number,
                    message=f"Unmatched opening quote",
                    error_type='quote'
                )
            self.errors.append(error)


class IndentationEngine:
    """
    Applies consistent indentation to TCL code based on block structures.
    
    This engine tracks brace nesting levels and block keywords to determine
    proper indentation for each line.
    """
    
    INDENT_SIZE = 2
    BLOCK_KEYWORDS = ['if', 'else', 'foreach', 'while', 'switch', 'proc', 'namespace']
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize indentation engine.
        
        Args:
            strict_mode: If True, enforce consistent indentation for continuation lines
        """
        self.strict_mode = strict_mode
    
    def apply_indentation(self, lines: List[str]) -> List[str]:
        """
        Apply indentation rules to all lines.
        
        Args:
            lines: List of code lines to indent
            
        Returns:
            List of indented code lines
        """
        if not lines:
            return lines
        
        result = []
        current_level = 0
        in_string = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip empty lines - preserve them as-is
            if not stripped:
                result.append(line)
                continue
            
            # Skip comment lines - preserve original indentation
            if stripped.startswith('#'):
                result.append(line)
                continue
            
            # Calculate indentation for this line
            line_level = self._calculate_indent_level(stripped, current_level, in_string)
            
            # Apply indentation
            indented_line = ' ' * (line_level * self.INDENT_SIZE) + stripped
            result.append(indented_line)
            
            # Update current level for next line based on this line's content
            current_level = self._update_level_after_line(stripped, line_level, in_string)
            
            # Track if we're in a string (for multi-line strings)
            in_string = self._update_string_state(stripped, in_string)
        
        return result
    
    def _calculate_indent_level(self, line: str, current_level: int, in_string: bool) -> int:
        """
        Calculate indentation level for a line.
        
        Args:
            line: The stripped line to calculate indentation for
            current_level: The current indentation level
            in_string: Whether we're currently in a multi-line string
            
        Returns:
            The indentation level for this line
        """
        # If we're in a string, maintain current level
        if in_string:
            return current_level
        
        # If line starts with closing brace, decrease indentation
        if line.startswith('}'):
            return max(0, current_level - 1)
        
        # For continuation lines in strict mode
        if self.strict_mode and self._is_continuation_line(line):
            # Continuation lines get extra indentation
            return current_level + 1
        
        return current_level
    
    def _update_level_after_line(self, line: str, line_level: int, in_string: bool) -> int:
        """
        Update indentation level after processing a line.
        
        Args:
            line: The stripped line that was just processed
            line_level: The indentation level used for this line
            in_string: Whether we're currently in a multi-line string
            
        Returns:
            The new indentation level for subsequent lines
        """
        if in_string:
            return line_level
        
        # Count braces in the line (excluding those in strings)
        open_braces = 0
        close_braces = 0
        in_line_string = False
        i = 0
        
        while i < len(line):
            char = line[i]
            
            # Handle escaped characters
            if char == '\\' and i + 1 < len(line):
                i += 2
                continue
            
            # Handle quotes
            if char == '"':
                in_line_string = not in_line_string
            
            # Count braces only when not in string
            if not in_line_string:
                if char == '{':
                    open_braces += 1
                elif char == '}':
                    close_braces += 1
            
            i += 1
        
        # Calculate net change in brace level
        net_change = open_braces - close_braces
        
        # If line starts with closing brace, we already decreased for this line
        # So we need to account for that
        if line.startswith('}'):
            return line_level + net_change + 1
        else:
            return line_level + net_change
    
    def _update_string_state(self, line: str, in_string: bool) -> bool:
        """
        Update whether we're in a multi-line string.
        
        Args:
            line: The stripped line to check
            in_string: Current string state
            
        Returns:
            Updated string state
        """
        # Count unescaped quotes
        quote_count = 0
        i = 0
        
        while i < len(line):
            char = line[i]
            
            # Handle escaped characters
            if char == '\\' and i + 1 < len(line):
                i += 2
                continue
            
            if char == '"':
                quote_count += 1
            
            i += 1
        
        # Toggle string state for each quote
        for _ in range(quote_count):
            in_string = not in_string
        
        return in_string
    
    def _is_continuation_line(self, line: str) -> bool:
        """
        Check if a line is a continuation line.
        
        In strict mode, continuation lines are lines that don't start with
        a keyword or brace and appear to be continuing a previous statement.
        
        Args:
            line: The stripped line to check
            
        Returns:
            True if this is a continuation line
        """
        # This is a simplified heuristic
        # A line is NOT a continuation if it starts with:
        # - A block keyword
        # - A brace
        # - A comment
        
        if line.startswith('#'):
            return False
        
        if line.startswith('{') or line.startswith('}'):
            return False
        
        # Check if line starts with a block keyword
        first_word = line.split()[0] if line.split() else ''
        if first_word in self.BLOCK_KEYWORDS:
            return False
        
        # Check for common TCL commands that start statements
        common_commands = ['set', 'puts', 'return', 'source', 'package', 'namespace']
        if first_word in common_commands:
            return False
        
        # If none of the above, it might be a continuation
        # But we need more context to be sure, so default to False
        return False


class ListExpansionEngine:
    """
    Expands long list structures to multiple lines for improved readability.
    
    This engine detects list structures exceeding 80 characters and expands
    them to multiple lines with proper indentation.
    """
    
    LIST_LENGTH_THRESHOLD = 80
    
    def __init__(self):
        """Initialize list expansion engine."""
        pass
    
    def expand_long_lists(self, lines: List[str]) -> List[str]:
        """
        Expand lists exceeding 80 characters to multiple lines.
        
        Args:
            lines: List of code lines to process
            
        Returns:
            List of lines with expanded lists
        """
        if not lines:
            return lines
        
        result = []
        
        for line in lines:
            # Check if this line contains a list that should be expanded
            if self._should_expand_list(line):
                expanded = self._expand_list(line)
                result.extend(expanded)
            else:
                result.append(line)
        
        return result
    
    def _should_expand_list(self, line: str) -> bool:
        """
        Determine if a line contains a list that should be expanded.
        
        A list should be expanded if:
        1. The line exceeds 80 characters
        2. The line contains a list structure (braces with content)
        
        Args:
            line: The line to check
            
        Returns:
            True if the list should be expanded
        """
        # Check length threshold
        if len(line) < self.LIST_LENGTH_THRESHOLD:
            return False
        
        stripped = line.strip()
        
        # Skip comments
        if stripped.startswith('#'):
            return False
        
        # Check if line contains a list structure
        # A simple heuristic: line contains { and } with content between
        if '{' not in stripped or '}' not in stripped:
            return False
        
        # Find the list structure
        # Look for patterns like: set var {item1 item2 item3}
        # or: list {item1 item2 item3}
        open_brace_idx = stripped.find('{')
        close_brace_idx = stripped.rfind('}')
        
        if open_brace_idx == -1 or close_brace_idx == -1:
            return False
        
        if close_brace_idx <= open_brace_idx:
            return False
        
        # Check if there's content between braces
        list_content = stripped[open_brace_idx + 1:close_brace_idx].strip()
        if not list_content:
            return False
        
        # Check if the list content looks like a list (has spaces, suggesting multiple items)
        # This is a heuristic to avoid expanding things like {$variable}
        if ' ' in list_content or '\t' in list_content:
            return True
        
        return False
    
    def _expand_list(self, line: str) -> List[str]:
        """
        Expand a list to multiple lines.
        
        Args:
            line: The line containing the list to expand
            
        Returns:
            List of expanded lines
        """
        # Get the original indentation
        indent = line[:len(line) - len(line.lstrip())]
        stripped = line.strip()
        
        # Find the list structure
        open_brace_idx = stripped.find('{')
        close_brace_idx = stripped.rfind('}')
        
        # Extract parts
        before_list = stripped[:open_brace_idx + 1]  # Everything up to and including {
        list_content = stripped[open_brace_idx + 1:close_brace_idx].strip()
        after_list = stripped[close_brace_idx + 1:]  # Everything after }
        
        # Split list content into items
        # Handle both space-separated and nested structures
        items = self._parse_list_items(list_content)
        
        # Build expanded lines
        result = []
        
        # First line: before_list (e.g., "set var {")
        result.append(indent + before_list)
        
        # Item lines: each item indented
        item_indent = indent + ' ' * IndentationEngine.INDENT_SIZE
        for item in items:
            result.append(item_indent + item)
        
        # Last line: closing brace at original indentation + after_list
        closing_line = indent + '}' + after_list
        result.append(closing_line)
        
        return result
    
    def _parse_list_items(self, list_content: str) -> List[str]:
        """
        Parse list content into individual items.
        
        This handles simple space-separated items and respects nested braces.
        
        Args:
            list_content: The content between the list braces
            
        Returns:
            List of item strings
        """
        items = []
        current_item = []
        brace_depth = 0
        in_string = False
        i = 0
        
        while i < len(list_content):
            char = list_content[i]
            
            # Handle escaped characters
            if char == '\\' and i + 1 < len(list_content):
                current_item.append(char)
                current_item.append(list_content[i + 1])
                i += 2
                continue
            
            # Handle quotes
            if char == '"':
                in_string = not in_string
                current_item.append(char)
                i += 1
                continue
            
            # Handle braces (only when not in string)
            if not in_string:
                if char == '{':
                    brace_depth += 1
                    current_item.append(char)
                    i += 1
                    continue
                elif char == '}':
                    brace_depth -= 1
                    current_item.append(char)
                    i += 1
                    continue
            
            # Handle whitespace (item separator when not nested)
            if not in_string and brace_depth == 0 and char in ' \t':
                # End of current item
                if current_item:
                    items.append(''.join(current_item))
                    current_item = []
                # Skip whitespace
                while i < len(list_content) and list_content[i] in ' \t':
                    i += 1
                continue
            
            # Regular character
            current_item.append(char)
            i += 1
        
        # Don't forget the last item
        if current_item:
            items.append(''.join(current_item))
        
        return items


class AlignmentEngine:
    """
    Aligns set commands within blocks for improved readability.
    
    This engine detects consecutive set commands and aligns their assignment
    values at the same column position based on the longest variable name.
    """
    
    def __init__(self):
        """Initialize alignment engine."""
        pass
    
    def align_set_commands(self, lines: List[str]) -> List[str]:
        """
        Align set commands within blocks.
        
        Args:
            lines: List of code lines to process
            
        Returns:
            List of lines with aligned set commands
        """
        if not lines:
            return lines
        
        # Find all blocks of consecutive set commands
        set_blocks = self._find_set_blocks(lines)
        
        # If no set blocks found, return original lines
        if not set_blocks:
            return lines
        
        # Create a copy of lines to modify
        result = lines.copy()
        
        # Align each block
        for block_indices in set_blocks:
            aligned_block = self._align_block(result, block_indices)
            # Replace the lines in result with aligned versions
            for i, line_idx in enumerate(block_indices):
                result[line_idx] = aligned_block[i]
        
        return result
    
    def _find_set_blocks(self, lines: List[str]) -> List[List[int]]:
        """
        Identify blocks of consecutive set commands.
        
        A block is a sequence of consecutive lines that are set commands,
        ignoring empty lines and comments.
        
        Args:
            lines: List of code lines
            
        Returns:
            List of blocks, where each block is a list of line indices
        """
        blocks = []
        current_block = []
        current_indent = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip empty lines - they don't break blocks
            if not stripped:
                continue
            
            # Comments break blocks
            if stripped.startswith('#'):
                if len(current_block) > 1:  # Only save blocks with 2+ set commands
                    blocks.append(current_block)
                current_block = []
                current_indent = None
                continue
            
            # Check if this is a set command
            if self._is_set_command(stripped):
                # Get the indentation level of this line
                indent = len(line) - len(line.lstrip())
                
                # If this is the first set in a potential block, or same indent level
                if current_indent is None or indent == current_indent:
                    current_block.append(i)
                    current_indent = indent
                else:
                    # Different indent level - start new block
                    if len(current_block) > 1:
                        blocks.append(current_block)
                    current_block = [i]
                    current_indent = indent
            else:
                # Not a set command - save current block if it has 2+ commands
                if len(current_block) > 1:
                    blocks.append(current_block)
                current_block = []
                current_indent = None
        
        # Don't forget the last block
        if len(current_block) > 1:
            blocks.append(current_block)
        
        return blocks
    
    def _is_set_command(self, line: str) -> bool:
        """
        Check if a line is a set command.
        
        Args:
            line: The stripped line to check
            
        Returns:
            True if the line is a set command
        """
        # A set command starts with 'set' followed by whitespace
        if not line.startswith('set '):
            return False
        
        # Make sure it's not part of a larger word (e.g., 'setup')
        # The 'set ' check above handles this, but let's be explicit
        parts = line.split(None, 1)  # Split on first whitespace
        return len(parts) >= 1 and parts[0] == 'set'
    
    def _align_block(self, lines: List[str], block_indices: List[int]) -> List[str]:
        """
        Align set commands in a single block.
        
        Args:
            lines: The full list of lines
            block_indices: Indices of lines in this block
            
        Returns:
            List of aligned lines for this block
        """
        # Extract the set commands from the block
        set_lines = [lines[i] for i in block_indices]
        
        # Parse each set command to extract variable name and value
        parsed_commands = []
        for line in set_lines:
            parsed = self._parse_set_command(line)
            if parsed:
                parsed_commands.append(parsed)
        
        # Find the maximum variable name length
        max_var_length = max(len(cmd['variable']) for cmd in parsed_commands)
        
        # Rebuild each line with aligned values
        aligned_lines = []
        for cmd in parsed_commands:
            indent = cmd['indent']
            variable = cmd['variable']
            value = cmd['value']
            
            # Calculate padding needed
            padding = max_var_length - len(variable)
            
            # Rebuild the line: indent + "set " + variable + spaces + value
            aligned_line = indent + 'set ' + variable + ' ' * (padding + 1) + value
            aligned_lines.append(aligned_line)
        
        return aligned_lines
    
    def _parse_set_command(self, line: str) -> Optional[dict]:
        """
        Parse a set command line into its components.
        
        Args:
            line: The line containing a set command
            
        Returns:
            Dictionary with 'indent', 'variable', and 'value' keys, or None if parsing fails
        """
        # Get the indentation
        indent = line[:len(line) - len(line.lstrip())]
        stripped = line.strip()
        
        # Remove 'set ' from the beginning
        if not stripped.startswith('set '):
            return None
        
        remainder = stripped[4:]  # Remove 'set '
        
        # Split into variable and value
        # The variable is the first token, value is everything after
        parts = remainder.split(None, 1)  # Split on first whitespace
        
        if len(parts) < 2:
            # No value provided (edge case)
            return None
        
        variable = parts[0]
        value = parts[1]
        
        return {
            'indent': indent,
            'variable': variable,
            'value': value
        }
    
    def apply_single_space(self, lines: List[str]) -> List[str]:
        """
        Ensure set commands have single-space separation when alignment is disabled.
        
        Args:
            lines: List of code lines to process
            
        Returns:
            List of lines with single-space separation for set commands
        """
        if not lines:
            return lines
        
        result = []
        
        for line in lines:
            stripped = line.strip()
            
            # Check if this is a set command
            if self._is_set_command(stripped):
                # Parse and rebuild with single space
                parsed = self._parse_set_command(line)
                if parsed:
                    indent = parsed['indent']
                    variable = parsed['variable']
                    value = parsed['value']
                    
                    # Rebuild with exactly one space between variable and value
                    normalized_line = indent + 'set ' + variable + ' ' + value
                    result.append(normalized_line)
                else:
                    # Parsing failed, keep original
                    result.append(line)
            else:
                # Not a set command, keep as-is
                result.append(line)
        
        return result


@dataclass
class FormattingResult:
    """Represents the result of a formatting operation."""
    success: bool
    output_path: Optional[str] = None
    error_path: Optional[str] = None
    errors: Optional[List[SyntaxError]] = None
    message: str = ""


class TCLFormatter:
    """
    Main formatter class that orchestrates TCL file formatting.
    
    This class integrates syntax validation, indentation, alignment, and list
    expansion to produce properly formatted TCL code. It handles file I/O,
    encoding detection, and error reporting.
    """
    
    def __init__(self, align_set: bool = False, expand_lists: bool = False, 
                 strict_indent: bool = False):
        """
        Initialize formatter with formatting options.
        
        Args:
            align_set: If True, align set command values
            expand_lists: If True, expand long lists to multiple lines
            strict_indent: If True, enforce strict indentation for continuation lines
        """
        self.align_set = align_set
        self.expand_lists = expand_lists
        self.strict_indent = strict_indent
        
        # Initialize component engines
        self.syntax_validator = SyntaxValidator()
        self.indentation_engine = IndentationEngine(strict_mode=strict_indent)
        self.alignment_engine = AlignmentEngine()
        self.list_expansion_engine = ListExpansionEngine()
    
    def format_file(self, input_path: str) -> FormattingResult:
        """
        Format a TCL file and return the result.
        
        This method:
        1. Reads the input file with proper encoding detection
        2. Validates syntax for errors
        3. If errors found, generates error log and returns
        4. If no errors, applies formatting based on options
        5. Writes formatted output to new file
        
        Args:
            input_path: Path to the input TCL file
            
        Returns:
            FormattingResult object containing success status, paths, and messages
        """
        try:
            # Read the input file with encoding detection
            lines = self._read_file(input_path)
            
            # Validate syntax
            errors = self.syntax_validator.validate(lines)
            
            if errors:
                # Syntax errors found - generate error log
                error_log_path = self._generate_error_log(input_path, errors)
                return FormattingResult(
                    success=False,
                    error_path=error_log_path,
                    errors=errors,
                    message=f"Syntax validation failed with {len(errors)} error(s). See {error_log_path}"
                )
            
            # No syntax errors - proceed with formatting
            formatted_lines = self._format_lines(lines)
            
            # Write output file
            output_path = self._generate_output_path(input_path)
            self._write_file(output_path, formatted_lines)
            
            return FormattingResult(
                success=True,
                output_path=output_path,
                message=f"Successfully formatted to {output_path}"
            )
            
        except IOError as e:
            return FormattingResult(
                success=False,
                message=f"File I/O error: {str(e)}"
            )
        except PermissionError as e:
            return FormattingResult(
                success=False,
                message=f"Permission denied: {str(e)}"
            )
        except Exception as e:
            return FormattingResult(
                success=False,
                message=f"Unexpected error: {str(e)}"
            )
    
    def _read_file(self, file_path: str) -> List[str]:
        """
        Read file with proper encoding detection.
        
        This method attempts to detect the file encoding using chardet,
        falling back to UTF-8 and then system default encoding if needed.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            List of lines from the file
            
        Raises:
            IOError: If file cannot be read
        """
        # First, try to detect encoding
        encoding = 'utf-8'  # Default
        
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                
            # Detect encoding
            detected = chardet.detect(raw_data)
            if detected and detected['encoding']:
                encoding = detected['encoding']
        except Exception:
            # If detection fails, stick with UTF-8
            pass
        
        # Read the file with detected encoding
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            # Remove newline characters but preserve empty lines
            lines = [line.rstrip('\r\n') for line in lines]
            return lines
            
        except UnicodeDecodeError:
            # If detected encoding fails, try UTF-8
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                lines = [line.rstrip('\r\n') for line in lines]
                return lines
            except UnicodeDecodeError:
                # Last resort: use system default with error handling
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                lines = [line.rstrip('\r\n') for line in lines]
                return lines
    
    def _format_lines(self, lines: List[str]) -> List[str]:
        """
        Apply formatting rules to lines based on configured options.
        
        This method applies formatting in the following order:
        1. Indentation (always applied)
        2. List expansion (if enabled)
        3. Set command alignment (if enabled)
        
        Comments and line continuations are preserved throughout.
        
        Args:
            lines: List of code lines to format
            
        Returns:
            List of formatted lines
        """
        if not lines:
            return lines
        
        # Apply indentation first (always applied)
        formatted = self.indentation_engine.apply_indentation(lines)
        
        # Apply list expansion if enabled
        if self.expand_lists:
            formatted = self.list_expansion_engine.expand_long_lists(formatted)
        
        # Apply set command alignment if enabled
        if self.align_set:
            formatted = self.alignment_engine.align_set_commands(formatted)
        else:
            # Ensure single-space separation when alignment is disabled
            formatted = self.alignment_engine.apply_single_space(formatted)
        
        return formatted
    
    def _generate_output_path(self, input_path: str) -> str:
        """
        Generate output file path with "_formatted.tcl" suffix.
        
        Args:
            input_path: Path to the input file
            
        Returns:
            Path for the output file
        """
        path = Path(input_path)
        
        # Get the directory, stem (filename without extension), and extension
        directory = path.parent
        stem = path.stem
        extension = path.suffix
        
        # Create new filename with "_formatted" suffix
        output_filename = f"{stem}_formatted{extension}"
        output_path = directory / output_filename
        
        return str(output_path)
    
    def _write_file(self, file_path: str, lines: List[str]) -> None:
        """
        Write formatted lines to output file.
        
        Args:
            file_path: Path to the output file
            lines: List of formatted lines to write
            
        Raises:
            IOError: If file cannot be written
            PermissionError: If write permission is denied
        """
        # Check if output directory is writable
        directory = Path(file_path).parent
        
        if not os.access(directory, os.W_OK):
            raise PermissionError(f"Cannot write to directory: {directory}")
        
        # Write the file with UTF-8 encoding
        try:
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                for line in lines:
                    f.write(line + '\n')
        except Exception as e:
            raise IOError(f"Failed to write file {file_path}: {str(e)}")
    
    def _generate_error_log(self, input_path: str, errors: List[SyntaxError]) -> str:
        """
        Generate error log file with syntax errors.
        
        The error log is created in the same directory as the input file
        with the name "errors.log". Each error is written on a separate line
        with the format "Line X: [error description]".
        
        Args:
            input_path: Path to the input file
            errors: List of syntax errors to log
            
        Returns:
            Path to the generated error log file
            
        Raises:
            IOError: If error log cannot be written
        """
        path = Path(input_path)
        directory = path.parent
        error_log_path = directory / "errors.log"
        
        # Format errors
        error_lines = []
        for error in errors:
            error_line = f"Line {error.line_number}: {error.message}"
            error_lines.append(error_line)
        
        # Write error log
        try:
            with open(error_log_path, 'w', encoding='utf-8') as f:
                for error_line in error_lines:
                    f.write(error_line + '\n')
        except Exception as e:
            raise IOError(f"Failed to write error log {error_log_path}: {str(e)}")
        
        return str(error_log_path)
