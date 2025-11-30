# TCL Formatter & Syntax Debugger

A tool for automated formatting and syntax validation of TCL (Tool Command Language) script files. Available as both a desktop application (PyQt6) and a web interface (Flask), this tool helps developers maintain consistent code style and quickly identify syntax errors.

## Features

- **Syntax Validation**: Detects unmatched braces and quotes with line-by-line error reporting
- **Automatic Formatting**: Applies consistent indentation based on TCL block structures
- **Set Command Alignment**: Optionally aligns variable assignments for better readability
- **List Expansion**: Expands long lists to multiple lines for improved clarity
- **Strict Indentation Mode**: Enforces consistent indentation for continuation lines
- **Error Reporting**: Generates detailed error logs with line numbers
- **Desktop GUI**: PyQt6-based interface for local file processing
- **Web Interface**: Browser-based interface for formatting without installation

## Requirements

### Desktop Application
- Python 3.8 or higher (Python 3.10+ recommended)
- PyQt6 for the graphical interface

### Web Interface
- Python 3.8 or higher (Python 3.10+ recommended)
- Flask 3.0+ for the web server
- All desktop application dependencies

### Testing
- Hypothesis and pytest for testing

## Installation

### Method 1: Install from Source

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Method 2: Install Dependencies Individually

```bash
pip install PyQt6>=6.4.0
pip install hypothesis>=6.0.0
pip install pytest>=7.0.0
```

## Usage

### Option 1: Desktop Application

#### Running the Desktop Application

From the project directory, run:

```bash
python main.py
```

#### Using the Desktop Application

1. **Select a TCL File**
   - Click the "Browse" button
   - Navigate to your TCL file (must have .tcl extension)
   - The file path will be displayed in the text field

2. **Configure Formatting Options**
   - **Align set commands**: Aligns variable assignments in consecutive set statements
   - **Expand long lists to multiline formatting**: Breaks lists longer than 80 characters into multiple lines
   - **Strict indentation mode**: Enforces consistent indentation for continuation lines

3. **Format the File**
   - Click the "Format" button
   - Wait for processing to complete
   - Check the status output for results

#### Desktop Output Files

- **Successful Formatting**: Creates `filename_formatted.tcl` in the same directory as the input file
- **Syntax Errors**: Creates `errors.log` in the same directory with line-numbered error descriptions

### Option 2: Web Interface

#### Running the Web Server

From the project directory, run:

```bash
python web/app.py
```

The server will start on `http://localhost:5000` by default.

For production deployment with multiple workers:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web.app:app
```

#### Using the Web Interface

1. Open your web browser and navigate to `http://localhost:5000`
2. **Upload a TCL File**
   - Click "Choose File" or drag and drop a .tcl file
   - Only .tcl files are accepted (10MB maximum size)
3. **Configure Formatting Options**
   - Check the boxes for desired formatting options:
     - Align set commands
     - Expand long lists to multiline formatting
     - Strict indentation mode
4. **Format the File**
   - Click the "Format TCL File" button
   - The formatted file or error log will automatically download

#### Web Interface Output

- **Successful Formatting**: Downloads `filename_formatted.tcl` to your browser's download folder
- **Syntax Errors**: Downloads `errors.log` with line-numbered error descriptions
- **Status Messages**: Displayed on the page with color-coded feedback (green for success, red for errors)

#### Web API Endpoint

The web interface exposes a REST API endpoint for programmatic access:

**Endpoint**: `POST /format`

**Request**:
- Content-Type: `multipart/form-data`
- Fields:
  - `file`: TCL file (required, .tcl extension, max 10MB)
  - `align_set`: `true` or `false` (optional, default: `false`)
  - `expand_lists`: `true` or `false` (optional, default: `false`)
  - `strict_indent`: `true` or `false` (optional, default: `false`)

**Response (Success)**:
- Content-Type: `application/octet-stream`
- Content-Disposition: `attachment; filename="[original]_formatted.tcl"`
- Body: Formatted TCL file content

**Response (Syntax Errors)**:
- Content-Type: `application/octet-stream`
- Content-Disposition: `attachment; filename="errors.log"`
- Body: Error log content

**Response (Error)**:
- Status: 400 (Bad Request) or 500 (Internal Server Error)
- Content-Type: `application/json`
- Body: `{"error": "error message"}`

**Example using curl**:

```bash
# Format a file with all options enabled
curl -X POST http://localhost:5000/format \
  -F "file=@example.tcl" \
  -F "align_set=true" \
  -F "expand_lists=true" \
  -F "strict_indent=true" \
  -o output_formatted.tcl

# Format a file with default options
curl -X POST http://localhost:5000/format \
  -F "file=@example.tcl" \
  -o output_formatted.tcl
```

## Example Files

The `examples/` directory contains sample TCL files:

- `example_valid.tcl`: Demonstrates various TCL constructs that will be formatted
- `example_invalid.tcl`: Contains intentional syntax errors for testing error detection
- `example_formatted.tcl`: Shows expected output after formatting

## Formatting Rules

### Indentation
- 2 spaces per indentation level
- Increases after lines ending with `{`
- Decreases for lines starting with `}`
- Recognizes block keywords: `if`, `else`, `foreach`, `while`, `switch`, `proc`, `namespace`

### Set Command Alignment
When enabled, aligns assignment values:
```tcl
set short_var      "value1"
set longer_var     "value2"
set very_long_var  "value3"
```

### List Expansion
Lists exceeding 80 characters are expanded:
```tcl
set mylist {
  element1
  element2
  element3
}
```

## Development

### Running Tests

Run all tests:
```bash
pytest
```

Run unit tests only:
```bash
pytest tests/unit/
```

Run property-based tests:
```bash
pytest tests/property/
```

### Project Structure

```
tcl-formatter-debugger/
├── main.py               # Desktop application entry point
├── src/
│   ├── ui.py             # PyQt6 UI components
│   └── formatter.py      # Core formatting engine (shared)
├── web/
│   ├── app.py            # Flask web application
│   ├── static/
│   │   ├── css/          # Web interface styles
│   │   └── js/           # Client-side JavaScript
│   └── templates/
│       └── index.html    # Web interface HTML
├── tests/
│   ├── unit/             # Unit tests
│   ├── property/         # Property-based tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test data
├── examples/             # Example TCL files
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

