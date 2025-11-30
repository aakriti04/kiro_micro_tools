# Project Structure

## Directory Layout

```
tcl-formatter-debugger/
├── main.py              # Application entry point
├── src/                 # Source code
│   ├── __init__.py
│   ├── ui.py           # PyQt6 UI components and main window
│   └── formatter.py    # Core formatting engine and validators
├── tests/              # Test suite
│   ├── unit/          # Unit tests for individual components
│   ├── property/      # Property-based tests (hypothesis)
│   ├── integration/   # Integration tests
│   └── fixtures/      # Test data and fixtures
├── examples/          # Sample TCL files for testing
├── requirements.txt   # Python dependencies
└── README.md         # Documentation
```

## Module Organization

### `src/formatter.py`
Core formatting logic organized into specialized engines:
- `SyntaxValidator`: Stack-based brace and quote matching
- `IndentationEngine`: Applies consistent 2-space indentation
- `ListExpansionEngine`: Expands long lists (>80 chars) to multiline
- `AlignmentEngine`: Aligns set command assignments
- `TCLFormatter`: Main orchestrator class

### `src/ui.py`
PyQt6 GUI components:
- `TCLFormatterUI`: Main window with file selection, options, and status display
- `FormatterWorker`: QThread worker for background formatting operations

### `main.py`
Application entry point with error handling for startup failures.

## Code Conventions

### Indentation
- 2 spaces per indentation level (TCL formatting)
- 4 spaces for Python code (standard PEP 8)

### Docstrings
- All classes and public methods have docstrings
- Google-style docstring format with Args, Returns, and description

### Error Handling
- Graceful error handling with user-friendly messages
- Errors logged to `errors.log` in same directory as input file

### Testing
- Unit tests for each engine class
- Property-based tests for validation logic
- Integration tests for end-to-end workflows
- Test files follow `test_*.py` naming convention
