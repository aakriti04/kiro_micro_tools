# Design Document

## Overview

This design document describes the architecture for adding a web-based frontend to the TCL Formatter & Syntax Debugger application. The solution consists of:

1. **Flask Backend API** - A lightweight REST API that wraps the existing TCL formatter functionality
2. **HTML/CSS/JavaScript Frontend** - A single-page web interface that mimics the desktop application's functionality
3. **Shared Core Logic** - Reuse of existing formatter.py module for consistent behavior

The design prioritizes simplicity and code reuse, ensuring the web interface provides the same formatting capabilities as the desktop application while maintaining clean separation between the two interfaces.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (HTML/CSS/JS)  │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Flask Backend  │
│   (web_app.py)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  TCL Formatter  │
│ (formatter.py)  │
└─────────────────┘
```

### Technology Stack

**Backend:**
- Flask 3.0+ - Lightweight web framework
- Werkzeug - File upload handling and security
- Python 3.8+ - Existing requirement

**Frontend:**
- HTML5 - Structure
- CSS3 - Styling with responsive design
- Vanilla JavaScript - Client-side logic (no framework dependencies)

**Shared:**
- Existing src/formatter.py module
- Existing src/__init__.py

### Directory Structure

```
tcl-formatter-debugger/
├── web/
│   ├── app.py              # Flask application and API endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css   # Web interface styles
│   │   └── js/
│   │       └── main.js     # Client-side logic
│   └── templates/
│       └── index.html      # Main web interface
├── src/                    # Existing formatter code (unchanged)
│   ├── formatter.py
│   └── ui.py              # Desktop UI (unchanged)
├── main.py                # Desktop app entry point (unchanged)
└── requirements.txt       # Updated with Flask dependencies
```

## Components and Interfaces

### 1. Flask Backend (web/app.py)

**Responsibilities:**
- Serve the HTML interface
- Handle file uploads via multipart/form-data
- Invoke TCL formatter with user-specified options
- Return formatted files or error logs
- Manage temporary file storage and cleanup

**API Endpoints:**

#### GET /
- **Purpose:** Serve the main web interface
- **Response:** HTML page (index.html)

#### POST /format
- **Purpose:** Format uploaded TCL file
- **Request:**
  - Content-Type: multipart/form-data
  - Fields:
    - `file`: TCL file (required)
    - `align_set`: boolean (optional, default: false)
    - `expand_lists`: boolean (optional, default: false)
    - `strict_indent`: boolean (optional, default: false)
- **Response (Success):**
  - Content-Type: application/octet-stream
  - Content-Disposition: attachment; filename="[original]_formatted.tcl"
  - Body: Formatted TCL file content
- **Response (Syntax Errors):**
  - Content-Type: application/octet-stream
  - Content-Disposition: attachment; filename="errors.log"
  - Body: Error log content
- **Response (Error):**
  - Status: 400/500
  - Content-Type: application/json
  - Body: `{"error": "error message"}`

**Key Functions:**

```python
def format_tcl_file():
    """Handle file upload and formatting request"""
    # 1. Validate file upload
    # 2. Save to temporary location
    # 3. Parse formatting options
    # 4. Invoke TCLFormatter
    # 5. Return result file or error
    # 6. Clean up temporary files
```

### 2. Web Frontend

#### HTML Structure (templates/index.html)

**Sections:**
1. Header with title
2. File selection area with upload button
3. Formatting options (3 checkboxes)
4. Format button
5. Status display area

**Key Elements:**
- `<input type="file" accept=".tcl">` - File selection
- `<input type="checkbox">` - Three formatting options
- `<button id="formatBtn">` - Submit button
- `<div id="status">` - Status messages

#### CSS Styling (static/css/style.css)

**Design Principles:**
- Clean, modern interface matching desktop app aesthetic
- Responsive layout using flexbox
- Color scheme: Green for success, red for errors
- Card-based layout with subtle shadows

**Key Styles:**
- Container with max-width for readability
- Button styling matching desktop app
- Checkbox styling with labels
- Status area with color-coded messages

#### JavaScript Logic (static/js/main.js)

**Responsibilities:**
- Handle file selection and validation
- Collect formatting options
- Submit form data via fetch API
- Display status messages
- Trigger file downloads
- Handle errors

**Key Functions:**

```javascript
async function formatFile() {
    // 1. Validate file selection
    // 2. Build FormData with file and options
    // 3. POST to /format endpoint
    // 4. Handle response (download or error)
    // 5. Update status display
}

function updateStatus(message, isError) {
    // Update status area with colored message
}

function downloadFile(blob, filename) {
    // Trigger browser download
}
```

### 3. Integration with Existing Formatter

The Flask backend imports and uses the existing `TCLFormatter` class:

```python
from src.formatter import TCLFormatter, FormattingResult

def process_file(file_path, options):
    formatter = TCLFormatter(
        align_set=options['align_set'],
        expand_lists=options['expand_lists'],
        strict_indent=options['strict_indent']
    )
    result = formatter.format_file(file_path)
    return result
```

This ensures identical formatting behavior between desktop and web interfaces.

## Data Models

### FormData (Client to Server)

```
FormData {
    file: File (binary)
    align_set: "true" | "false"
    expand_lists: "true" | "false"
    strict_indent: "true" | "false"
}
```

### Response Models

**Success Response (File Download):**
```
Headers:
    Content-Type: application/octet-stream
    Content-Disposition: attachment; filename="..."
Body: File content (bytes)
```

**Error Response (JSON):**
```json
{
    "error": "Error message description"
}
```

### Temporary File Management

**Storage:**
- Location: System temp directory (via `tempfile` module)
- Naming: Secure random names (via `tempfile.NamedTemporaryFile`)
- Lifecycle: Created on upload, deleted after response

**Cleanup Strategy:**
- Use context managers for automatic cleanup
- Delete both input and output files after sending response
- Handle cleanup even on error conditions

## Co
rrectness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


Property 1: Valid TCL file acceptance
*For any* file with a .tcl extension, the backend should accept and process the file without rejecting it based on extension
**Validates: Requirements 2.1**

Property 2: Invalid extension rejection
*For any* file without a .tcl extension, the backend should reject the file and return an error message
**Validates: Requirements 2.2**

Property 3: Successful formatting returns formatted file
*For any* valid TCL file without syntax errors, the backend should return a formatted file with the expected naming convention
**Validates: Requirements 2.4**

Property 4: Syntax errors return error log
*For any* TCL file with syntax errors, the backend should return an error log file containing the error details
**Validates: Requirements 2.5**

Property 5: Formatting options affect output
*For any* valid TCL file, formatting with different option combinations should produce different outputs when those options would affect the formatting
**Validates: Requirements 3.3**

Property 6: Temporary file cleanup
*For any* formatting request (successful or failed), all temporary files created during processing should be deleted after the response is sent
**Validates: Requirements 5.4, 7.3**

Property 7: Web and desktop formatter consistency
*For any* valid TCL file and option combination, the web backend should produce identical output to the desktop application when given the same inputs
**Validates: Requirements 6.1, 6.2**

Property 8: Output filename convention
*For any* input file, the formatted output filename should follow the pattern "[original_name]_formatted.tcl"
**Validates: Requirements 6.3**

Property 9: File size validation
*For any* file exceeding 10MB, the backend should reject the upload and return an error message
**Validates: Requirements 7.1**

Property 10: Secure random filenames
*For any* two consecutive file uploads, the temporary filenames generated should be different and unpredictable
**Validates: Requirements 7.2**

## Error Handling

### Client-Side Error Handling

**File Selection Errors:**
- Invalid file extension: Display error message, prevent submission
- No file selected: Disable format button
- File too large: Display error message before upload

**Network Errors:**
- Connection failure: Display "Unable to connect to server" message
- Timeout: Display "Request timed out" message
- Server error (5xx): Display "Server error occurred" message

**Response Handling:**
- Parse error responses and display user-friendly messages
- Handle unexpected response formats gracefully

### Server-Side Error Handling

**File Upload Errors:**
- Missing file: Return 400 with error message
- Invalid extension: Return 400 with error message
- File too large: Return 413 (Payload Too Large) with error message
- Upload failure: Return 500 with error message

**Processing Errors:**
- Formatter exceptions: Catch and return 500 with error message
- File I/O errors: Return 500 with error message
- Permission errors: Return 500 with error message

**Cleanup Errors:**
- Log cleanup failures but don't fail the request
- Use try-finally blocks to ensure cleanup attempts

### Error Response Format

All error responses follow this JSON structure:
```json
{
    "error": "Human-readable error message"
}
```

## Testing Strategy

### Unit Testing

**Backend Unit Tests:**
- Test file extension validation logic
- Test file size validation logic
- Test temporary file creation and cleanup
- Test option parsing from form data
- Test error response formatting

**Frontend Unit Tests (Optional for MVP):**
- Test form validation logic
- Test option state management
- Test status message formatting

### Property-Based Testing

Property-based tests will use the `hypothesis` library (already in the project) to verify the correctness properties defined above.

**Test Configuration:**
- Minimum 100 iterations per property test
- Each property test tagged with: `# Feature: web-frontend, Property X: [property text]`

**Key Property Tests:**

1. **File Extension Validation** - Generate random filenames with various extensions
2. **File Size Validation** - Generate files of random sizes around the 10MB threshold
3. **Formatter Consistency** - Generate random valid TCL code and compare web vs desktop output
4. **Temporary File Cleanup** - Verify no temp files remain after random request sequences
5. **Filename Convention** - Verify output naming for random input filenames

### Integration Testing

**API Integration Tests:**
- Test complete request/response cycle for successful formatting
- Test complete request/response cycle for syntax errors
- Test file download functionality
- Test concurrent request handling

**End-to-End Tests (Optional for MVP):**
- Use Selenium or Playwright for browser automation
- Test complete user workflows
- Test UI feedback and status messages

### Manual Testing Checklist

- [ ] Upload valid TCL file and verify formatted output
- [ ] Upload file with syntax errors and verify error log
- [ ] Test each formatting option individually
- [ ] Test all formatting options combined
- [ ] Upload file with invalid extension
- [ ] Upload file exceeding size limit
- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Test on different screen sizes
- [ ] Verify desktop app still works independently

## Deployment Considerations

### Running the Web Application

**Development Mode:**
```bash
python web/app.py
```
- Flask development server
- Debug mode enabled
- Auto-reload on code changes
- Accessible at http://localhost:5000

**Production Mode:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 web.app:app
```
- Use production WSGI server (gunicorn)
- Multiple worker processes
- Proper error handling
- Behind reverse proxy (nginx/Apache)

### Configuration

**Environment Variables:**
- `FLASK_ENV`: development or production
- `MAX_CONTENT_LENGTH`: Maximum upload size (default: 10MB)
- `UPLOAD_FOLDER`: Temporary file storage location

**Security Considerations:**
- Set secure secret key for Flask sessions
- Configure CORS if needed for cross-origin requests
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Validate and sanitize all user inputs

### Monitoring

**Logging:**
- Log all formatting requests with timestamps
- Log errors with full stack traces
- Log file cleanup operations

**Metrics:**
- Track request count and response times
- Monitor temporary file storage usage
- Track success vs error rates

## Future Enhancements (Post-MVP)

1. **Batch Processing** - Upload and format multiple files at once
2. **Syntax Highlighting** - Display formatted code with syntax highlighting
3. **Diff View** - Show before/after comparison
4. **API Authentication** - Add API keys for programmatic access
5. **File History** - Store recent formatting operations
6. **Real-time Preview** - Show formatting preview before download
7. **Custom Options** - Allow users to configure indentation size, line length, etc.
8. **WebSocket Support** - Real-time progress updates for large files
