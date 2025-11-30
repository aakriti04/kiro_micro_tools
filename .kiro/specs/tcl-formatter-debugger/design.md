# Design Document

## Overview

The TCL Formatter & Syntax Debugger is a desktop application built with PyQt6 that provides automated code formatting and syntax validation for TCL script files. The application follows a modular architecture with clear separation between the UI layer, formatting engine, and syntax validation components. The design emphasizes maintainability, extensibility, and robust error handling.

The application processes TCL files through a pipeline: file selection → syntax validation → formatting → output generation. If syntax errors are detected, the pipeline short-circuits to error reporting instead of formatting.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     UI Layer (ui.py)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ File Browser │  │   Options    │  │    Status    │  │
│  │    Widget    │  │  Checkboxes  │  │    Display   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Formatter Engine (formatter.py)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Syntax     │  │  Indentation │  │   Alignment  │  │
│  │  Validator   │  │    Engine    │  │    Engine    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  File System Operations                  │
│         (Read Input, Write Output/Errors)                │
└─────────────────────────────────────────────────────────┘
```

### Module Structure

**main.py**
- Application entry point
- Initializes PyQt6 application
- Creates and displays main window
- Handles application lifecycle

**ui.py**
- Defines `TCLFormatterUI` class (QMainWindow)
- Manages all UI components and layout
- Handles user interactions and events
- Invokes formatter engine with user-selected options
- Displays results and error messages

**formatter.py**
- Defines `TCLFormatter` class
- Implements `SyntaxValidator` for error detection
- Implements `IndentationEngine` for code formatting
- Implements `AlignmentEngine` for set command alignment
- Provides public API for formatting operations

## Components and Interfaces

### UI Component (ui.py)

**Class: TCLFormatterUI(QMainWindow)**

```python
class TCLFormatterUI(QMainWindow):
    def __init__(self):
        """Initialize the main window and all UI components."""
        
    def setup_ui(self):
        """Create and layout all UI widgets."""
        
    def browse_file(self):
        """Open file dialog and select TCL file."""
        
    def format_file(self):
        """Invoke formatter with selected options and display results."""
        
    def update_status(self, message: str, is_error: bool = False):
        """Update status display with message."""
```

**UI Components:**
- `QLineEdit`: Display selected file path (read-only)
- `QPushButton`: Browse button, Format button
- `QCheckBox`: Three checkboxes for formatting options
- `QTextEdit`: Status output area (read-only)
- `QVBoxLayout`: Main layout container

### Formatter Engine (formatter.py)

**Class: TCLFormatter**

```python
class TCLFormatter:
    def __init__(self, align_set: bool = False, 
                 expand_lists: bool = False, 
                 strict_indent: bool = False):
        """Initialize formatter with options."""
        
    def format_file(self, input_path: str) -> dict:
        """
        Format TCL file and return result.
        
        Returns:
            {
                'success': bool,
                'output_path': str or None,
                'error_path': str or None,
                'errors': list or None,
                'message': str
            }
        """
        
    def validate_syntax(self, lines: list) -> list:
        """Validate syntax and return list of errors."""
        
    def format_lines(self, lines: list) -> list:
        """Apply formatting rules to lines."""
```

**Class: SyntaxValidator**

```python
class SyntaxValidator:
    def __init__(self):
        """Initialize validator with empty stack."""
        
    def validate(self, lines: list) -> list:
        """
        Validate braces and quotes using stack-based approach.
        
        Returns:
            List of error dictionaries with 'line' and 'message' keys
        """
        
    def _push(self, char: str, line_num: int):
        """Push opening character onto stack."""
        
    def _pop(self, char: str, line_num: int) -> dict or None:
        """Pop and validate matching character."""
```

**Class: IndentationEngine**

```python
class IndentationEngine:
    INDENT_SIZE = 2
    BLOCK_KEYWORDS = ['if', 'else', 'foreach', 'while', 'switch', 'proc', 'namespace']
    
    def __init__(self, strict_mode: bool = False):
        """Initialize indentation engine."""
        
    def apply_indentation(self, lines: list) -> list:
        """Apply indentation rules to all lines."""
        
    def _calculate_indent_level(self, line: str, current_level: int) -> int:
        """Calculate indentation level for line."""
```

**Class: AlignmentEngine**

```python
class AlignmentEngine:
    def align_set_commands(self, lines: list) -> list:
        """Align set commands within blocks."""
        
    def _find_set_blocks(self, lines: list) -> list:
        """Identify blocks of consecutive set commands."""
        
    def _align_block(self, block: list) -> list:
        """Align set commands in a single block."""
```

## Data Models

### FormattingOptions

```python
@dataclass
class FormattingOptions:
    align_set: bool = False
    expand_lists: bool = False
    strict_indent: bool = False
```

### SyntaxError

```python
@dataclass
class SyntaxError:
    line_number: int
    message: str
    error_type: str  # 'brace', 'quote', 'other'
```

### FormattingResult

```python
@dataclass
class FormattingResult:
    success: bool
    output_path: Optional[str] = None
    error_path: Optional[str] = None
    errors: Optional[List[SyntaxError]] = None
    message: str = ""
```

### StackFrame

```python
@dataclass
class StackFrame:
    char: str  # '{', '}', '"'
    line_number: int
    position: int
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, several properties can be consolidated to reduce redundancy:

**Consolidations:**
- Properties 6.1, 6.2, 6.3 (unmatched braces/quotes detection) can be combined into a single comprehensive property about syntax error detection with correct line numbers
- Properties 10.1, 10.2, 10.3, 10.4, 10.5 (stack operations) can be combined into a single property about stack-based validation correctness
- Properties 7.1, 7.2, 7.3 (indentation rules) can be combined into a single property about indentation consistency
- Properties 8.1, 8.2, 8.3 (set command alignment) can be combined into a single property about alignment correctness

### Core Properties

**Property 1: File path display consistency**
*For any* valid TCL file selected through the file browser, the displayed file path in the UI should exactly match the absolute path of the selected file.
**Validates: Requirements 1.3**

**Property 2: Invalid file rejection**
*For any* file without a .tcl extension, the file selection should be rejected and an error message should be displayed.
**Validates: Requirements 1.4**

**Property 3: Formatting option persistence**
*For any* formatting option checkbox toggled during a session, the checkbox state should remain unchanged until explicitly toggled again or the application closes.
**Validates: Requirements 2.4**

**Property 4: Selective option application**
*For any* combination of formatting options selected, the formatter should apply only those specific options and no others to the output.
**Validates: Requirements 2.5**

**Property 5: Format button enablement**
*For any* valid TCL file selected, the format button should transition from disabled to enabled state.
**Validates: Requirements 3.1**

**Property 6: Operation completion state restoration**
*For any* formatting operation that completes (success or failure), the format button should be re-enabled after completion.
**Validates: Requirements 3.3**

**Property 7: Concurrent operation prevention**
*For any* formatting operation in progress, attempting to start another operation should be blocked until the first completes.
**Validates: Requirements 3.4**

**Property 8: Success status display**
*For any* successfully formatted file, the status display should contain both the output file path and a success message.
**Validates: Requirements 4.2**

**Property 9: Error status display**
*For any* file with syntax errors, the status display should contain both the error log file path and the count of errors detected.
**Validates: Requirements 4.3**

**Property 10: File access error reporting**
*For any* file operation that fails due to permissions or I/O errors, the status display should contain a descriptive error message explaining the failure reason.
**Validates: Requirements 4.4**

**Property 11: Output file location**
*For any* successfully formatted file, the output file should be created in the same directory as the input file.
**Validates: Requirements 5.1**

**Property 12: Output file naming convention**
*For any* formatted output file created, the filename should be the original name with "_formatted" inserted before the .tcl extension.
**Validates: Requirements 5.2**

**Property 13: Output file overwriting**
*For any* formatting operation where the output file already exists, the existing file should be replaced with the new formatted content.
**Validates: Requirements 5.3**

**Property 14: Write failure exception handling**
*For any* formatting operation that cannot write to the output directory, an exception should be raised with a message describing the write failure.
**Validates: Requirements 5.4**

**Property 15: Syntax error detection with line numbers**
*For any* TCL file with unmatched braces or quotes, the syntax validator should report each error with the exact line number where the mismatch occurs.
**Validates: Requirements 6.1, 6.2, 6.3**

**Property 16: Error log generation**
*For any* TCL file with syntax errors, an error log file named "errors.log" should be created in the same directory as the input file.
**Validates: Requirements 6.4**

**Property 17: Error log format consistency**
*For any* error log file created, each error should appear on a separate line following the format "Line X: [error description]".
**Validates: Requirements 6.5**

**Property 18: Indentation consistency**
*For any* formatted TCL file, lines following an opening brace should have indentation increased by exactly 2 spaces, and lines starting with a closing brace should have indentation decreased by exactly 2 spaces.
**Validates: Requirements 7.1, 7.2, 7.3**

**Property 19: Block keyword indentation**
*For any* TCL block keyword (if, else, foreach, while, switch, proc, namespace), the formatter should maintain proper indentation context for all lines within that block.
**Validates: Requirements 7.4**

**Property 20: Strict indentation enforcement**
*For any* file formatted with strict indentation mode enabled, all continuation lines should have consistent indentation aligned with their parent statement.
**Validates: Requirements 7.5**

**Property 21: Set command alignment**
*For any* block of consecutive set commands when alignment is enabled, all assignment values should be aligned at the same column position based on the longest variable name in the block.
**Validates: Requirements 8.1, 8.2, 8.3**

**Property 22: Set command spacing without alignment**
*For any* set command when alignment is disabled, there should be exactly one space between the variable name and the assignment value.
**Validates: Requirements 8.4**

**Property 23: Long list detection**
*For any* list structure exceeding 80 characters when list expansion is enabled, the formatter should detect it and expand it to multiple lines.
**Validates: Requirements 9.1**

**Property 24: List expansion formatting**
*For any* expanded list, each element should appear on a separate line with increased indentation, and the closing brace should be on a new line at the original indentation level.
**Validates: Requirements 9.2, 9.3**

**Property 25: List preservation without expansion**
*For any* list when expansion is disabled, the original formatting should be preserved exactly as it appears in the input.
**Validates: Requirements 9.4**

**Property 26: Stack-based validation correctness**
*For any* TCL file, the syntax validator should correctly match all opening and closing braces and quotes using a stack, reporting errors for any unmatched characters with their line numbers, and returning success only when all characters are properly matched.
**Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**

**Property 27: Function documentation completeness**
*For any* function defined in the codebase, the function should have a docstring that describes its parameters and return values.
**Validates: Requirements 12.5**

## Error Handling

### Error Categories

**1. File System Errors**
- File not found
- Permission denied (read/write)
- Disk full
- Invalid path

**Strategy:** Catch `IOError`, `OSError`, and `PermissionError` exceptions. Display user-friendly error messages in the status area. Log detailed error information for debugging.

**2. Syntax Validation Errors**
- Unmatched opening braces
- Unmatched closing braces
- Unmatched quotes
- Invalid TCL syntax

**Strategy:** Collect all errors during validation pass. Generate error log file with line numbers. Display error count and log location in status area. Do not proceed with formatting.

**3. UI Interaction Errors**
- Invalid file selection
- Concurrent operation attempts
- Widget state inconsistencies

**Strategy:** Validate user input before processing. Disable controls during operations. Use Qt signals/slots for thread-safe UI updates.

**4. Formatting Engine Errors**
- Unexpected token sequences
- Malformed block structures
- Edge cases in indentation logic

**Strategy:** Implement defensive programming with validation checks. Log warnings for unexpected patterns. Attempt best-effort formatting with warnings.

### Error Recovery

**File System Errors:** Display error message, allow user to select different file or location.

**Syntax Errors:** Generate error log, display errors, allow user to fix source file and retry.

**UI Errors:** Reset UI state, re-enable controls, clear status messages.

**Formatting Errors:** Log error details, display generic error message, preserve original file.

## Testing Strategy

### Unit Testing

The application will use Python's built-in `unittest` framework for unit testing. Unit tests will focus on:

**Formatter Engine Tests:**
- Test indentation calculation for various line patterns
- Test set command detection and alignment logic
- Test list detection and expansion logic
- Test edge cases: empty files, single-line files, files with only comments

**Syntax Validator Tests:**
- Test matching of simple brace pairs
- Test matching of nested braces
- Test matching of quotes
- Test error reporting for specific mismatch scenarios
- Test edge cases: empty files, files with only braces

**UI Component Tests:**
- Test file path display after selection
- Test button state changes during operations
- Test status message updates
- Test checkbox state persistence

**File Operations Tests:**
- Test output file naming convention
- Test file overwriting behavior
- Test error log generation
- Test handling of read-only directories

### Property-Based Testing

The application will use **Hypothesis** for property-based testing in Python. Property-based tests will verify universal properties across randomly generated inputs.

**Configuration:**
- Each property-based test will run a minimum of 100 iterations
- Tests will use Hypothesis strategies to generate valid and invalid TCL code
- Each test will be tagged with a comment referencing the design document property

**Property Test Coverage:**

Each correctness property listed above will be implemented as a property-based test. The tests will:

1. Generate random TCL code with various characteristics (nested braces, quotes, block keywords, set commands, lists)
2. Apply formatting with different option combinations
3. Verify that the specified property holds for all generated inputs
4. Use Hypothesis to automatically find counterexamples if properties fail

**Test Tagging Format:**
```python
# Feature: tcl-formatter-debugger, Property 18: Indentation consistency
@given(tcl_code_with_braces())
def test_indentation_consistency(code):
    # Test implementation
```

**Hypothesis Strategies:**

Custom strategies will be created for:
- Valid TCL code with balanced braces
- TCL code with intentional syntax errors
- Set command blocks
- Long lists
- Nested block structures
- Various indentation patterns

### Integration Testing

Integration tests will verify end-to-end workflows:

1. **Complete formatting workflow:** Select file → Format → Verify output file
2. **Error detection workflow:** Select file with errors → Format → Verify error log
3. **Option combination testing:** Test all combinations of formatting options
4. **File system edge cases:** Read-only directories, missing files, locked files

### Test Organization

```
tests/
├── unit/
│   ├── test_formatter.py
│   ├── test_syntax_validator.py
│   ├── test_indentation_engine.py
│   ├── test_alignment_engine.py
│   └── test_ui_components.py
├── property/
│   ├── test_properties_formatting.py
│   ├── test_properties_validation.py
│   └── test_properties_file_operations.py
├── integration/
│   └── test_end_to_end.py
└── fixtures/
    ├── valid_tcl_samples/
    └── invalid_tcl_samples/
```

## Implementation Notes

### TCL Syntax Considerations

**Comments:** Lines starting with `#` should be preserved without formatting changes.

**String Literals:** Content within quotes should not be analyzed for braces or formatting.

**Escaped Characters:** Backslash-escaped characters should be handled correctly.

**Line Continuations:** Lines ending with backslash should be treated as continuation of previous line.

**Command Substitution:** Brackets `[]` used for command substitution should not affect indentation.

### Performance Considerations

**Large Files:** For files over 10,000 lines, consider:
- Streaming line-by-line processing
- Progress indicator in UI
- Cancellation option

**Memory Usage:** Process files line-by-line rather than loading entire file into memory.

**UI Responsiveness:** Run formatting in separate thread to prevent UI freezing. Use Qt's `QThread` for background processing.

### Extensibility

**Plugin Architecture:** Design formatter engine to support additional formatting rules as plugins.

**Configuration File:** Consider adding support for `.tclformat` configuration file to persist user preferences.

**Custom Rules:** Allow users to define custom indentation rules for project-specific keywords.

### Platform Compatibility

**File Paths:** Use `pathlib.Path` for cross-platform path handling.

**Line Endings:** Detect and preserve original line endings (CRLF vs LF).

**File Encoding:** Default to UTF-8, with fallback to system encoding.

## Dependencies

### Required Python Packages

- **PyQt6** (>=6.4.0): GUI framework
- **Hypothesis** (>=6.0.0): Property-based testing framework
- **pytest** (>=7.0.0): Test runner (alternative to unittest)

### Python Version

- Minimum: Python 3.8
- Recommended: Python 3.10 or higher

### Development Dependencies

- **black**: Code formatting
- **pylint**: Code linting
- **mypy**: Type checking

## Deployment

### Distribution Format

**Standalone Executable:** Use PyInstaller to create standalone executables for Windows, macOS, and Linux.

**Python Package:** Distribute as pip-installable package via PyPI.

### Installation Methods

**Method 1: From Source**
```bash
pip install -r requirements.txt
python main.py
```

**Method 2: Standalone Executable**
```bash
./tcl-formatter  # Linux/macOS
tcl-formatter.exe  # Windows
```

**Method 3: Python Package**
```bash
pip install tcl-formatter
tcl-formatter
```

### Documentation

**README.md:** Installation instructions, usage guide, examples

**User Guide:** Detailed explanation of formatting options and syntax rules

**Developer Guide:** Architecture overview, contribution guidelines, testing instructions
