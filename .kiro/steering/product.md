# Product Overview

TCL Formatter & Syntax Debugger is a desktop application for automated formatting and syntax validation of TCL (Tool Command Language) script files.

## Core Features

- **Syntax Validation**: Stack-based detection of unmatched braces and quotes with line-by-line error reporting
- **Automatic Formatting**: Consistent indentation based on TCL block structures (2 spaces per level)
- **Set Command Alignment**: Optional alignment of variable assignments for readability
- **List Expansion**: Expands lists exceeding 80 characters to multiple lines
- **Strict Indentation Mode**: Enforces consistent indentation for continuation lines
- **Error Reporting**: Generates `errors.log` with line numbers for syntax errors
- **User-Friendly GUI**: PyQt6-based interface for file selection and formatting options

## Output Behavior

- **Success**: Creates `filename_formatted.tcl` in the same directory as input
- **Failure**: Creates `errors.log` in the same directory with detailed error descriptions
- Files are overwritten if they already exist
