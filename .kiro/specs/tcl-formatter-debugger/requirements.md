# Requirements Document

## Introduction

The TCL Formatter & Syntax Debugger is a desktop application that provides automated formatting and syntax validation for TCL (Tool Command Language) script files. The application enables users to select TCL files, apply configurable formatting rules, and receive either a properly formatted output file or a detailed error report identifying syntax issues. The system is built using PyQt6 for the graphical user interface and implements a custom parsing and formatting engine in Python.

## Glossary

- **TCL File**: A text file with .tcl extension containing Tool Command Language script code
- **Formatter Engine**: The Python module responsible for parsing, validating, and reformatting TCL code
- **UI Component**: The PyQt6-based graphical user interface that handles user interactions
- **Syntax Validator**: The component that detects brace and quote mismatches using stack-based parsing
- **Formatting Options**: User-configurable settings that control code formatting behavior
- **Error Log**: A text file containing line-numbered syntax error descriptions
- **Formatted Output**: A TCL file with suffix _formatted.tcl containing properly indented and formatted code

## Requirements

### Requirement 1

**User Story:** As a TCL developer, I want to select a TCL file through a graphical interface, so that I can easily specify which file to format without using command-line arguments.

#### Acceptance Criteria

1. WHEN the application starts THEN the UI Component SHALL display a file browser button
2. WHEN the user clicks the browse button THEN the UI Component SHALL open a file selection dialog filtered to show .tcl files
3. WHEN the user selects a valid TCL File THEN the UI Component SHALL display the complete file path in a read-only text field
4. WHEN the user selects a non-tcl file THEN the UI Component SHALL reject the selection and display an error message
5. WHEN no file is selected THEN the UI Component SHALL disable the format button

### Requirement 2

**User Story:** As a TCL developer, I want to configure formatting options before processing, so that I can customize the output to match my coding standards.

#### Acceptance Criteria

1. WHEN the UI Component displays formatting options THEN the UI Component SHALL provide a checkbox for "Align set commands"
2. WHEN the UI Component displays formatting options THEN the UI Component SHALL provide a checkbox for "Expand long lists to multiline formatting"
3. WHEN the UI Component displays formatting options THEN the UI Component SHALL provide a checkbox for "Strict indentation mode"
4. WHEN the user toggles any Formatting Options THEN the UI Component SHALL persist the selection state for the current session
5. WHEN the format operation executes THEN the Formatter Engine SHALL apply only the selected Formatting Options

### Requirement 3

**User Story:** As a TCL developer, I want to initiate the formatting process with a single button click, so that I can quickly process my selected file.

#### Acceptance Criteria

1. WHEN a valid TCL File is selected THEN the UI Component SHALL enable the format button
2. WHEN the user clicks the format button THEN the UI Component SHALL disable the button and display a processing indicator
3. WHEN the formatting operation completes THEN the UI Component SHALL re-enable the format button
4. WHEN the formatting operation is in progress THEN the UI Component SHALL prevent multiple simultaneous format operations

### Requirement 4

**User Story:** As a TCL developer, I want to see the status and results of the formatting operation, so that I know whether the operation succeeded or failed.

#### Acceptance Criteria

1. WHEN the formatting operation starts THEN the UI Component SHALL display "Processing..." in the status output area
2. WHEN the formatting operation succeeds THEN the UI Component SHALL display the Formatted Output file path and success message
3. WHEN syntax errors are detected THEN the UI Component SHALL display the Error Log file path and error count
4. WHEN the formatting operation fails due to file access issues THEN the UI Component SHALL display a descriptive error message with the failure reason

### Requirement 5

**User Story:** As a TCL developer, I want the formatter to produce a new file with formatted code, so that my original file remains unchanged and I can review the changes before replacing it.

#### Acceptance Criteria

1. WHEN the Formatter Engine completes successfully THEN the Formatter Engine SHALL create a Formatted Output file in the same directory as the input file
2. WHEN creating the Formatted Output THEN the Formatter Engine SHALL append "_formatted" before the .tcl extension
3. WHEN the Formatted Output file already exists THEN the Formatter Engine SHALL overwrite the existing file
4. WHEN the Formatter Engine cannot write to the output directory THEN the Formatter Engine SHALL raise an exception with a descriptive error message

### Requirement 6

**User Story:** As a TCL developer, I want syntax errors to be detected and reported with line numbers, so that I can quickly locate and fix issues in my code.

#### Acceptance Criteria

1. WHEN the Syntax Validator detects unmatched opening braces THEN the Syntax Validator SHALL record the error with the line number where the brace was opened
2. WHEN the Syntax Validator detects unmatched closing braces THEN the Syntax Validator SHALL record the error with the line number where the excess brace appears
3. WHEN the Syntax Validator detects unmatched quotes THEN the Syntax Validator SHALL record the error with the line number where the quote mismatch occurs
4. WHEN syntax errors exist THEN the Formatter Engine SHALL generate an Error Log file named "errors.log" in the same directory as the input file
5. WHEN the Error Log is created THEN the Error Log SHALL contain each error on a separate line with format "Line X: [error description]"

### Requirement 7

**User Story:** As a TCL developer, I want the formatter to apply consistent indentation based on TCL block structures, so that my code is readable and follows standard conventions.

#### Acceptance Criteria

1. WHEN the Formatter Engine processes a line ending with an opening brace THEN the Formatter Engine SHALL increase indentation level by one for subsequent lines
2. WHEN the Formatter Engine processes a line starting with a closing brace THEN the Formatter Engine SHALL decrease indentation level by one for that line
3. WHEN the Formatter Engine applies indentation THEN the Formatter Engine SHALL use exactly 2 spaces per indentation level
4. WHEN the Formatter Engine encounters block keywords (if, else, foreach, while, switch, proc, namespace) THEN the Formatter Engine SHALL maintain proper indentation context for the block
5. WHEN strict indentation mode is enabled THEN the Formatter Engine SHALL enforce consistent indentation even for continuation lines

### Requirement 8

**User Story:** As a TCL developer, I want set commands to be optionally aligned, so that variable assignments are visually organized and easier to read.

#### Acceptance Criteria

1. WHEN "Align set commands" option is enabled THEN the Formatter Engine SHALL detect all set command statements in the current block
2. WHEN aligning set commands THEN the Formatter Engine SHALL calculate the maximum length of variable names in the block
3. WHEN aligning set commands THEN the Formatter Engine SHALL add whitespace after the variable name to align all assignment values
4. WHEN "Align set commands" option is disabled THEN the Formatter Engine SHALL preserve single-space separation between variable names and values

### Requirement 9

**User Story:** As a TCL developer, I want long lists to be optionally expanded to multiple lines, so that complex data structures are more readable.

#### Acceptance Criteria

1. WHEN "Expand long lists to multiline formatting" option is enabled THEN the Formatter Engine SHALL detect list structures exceeding 80 characters
2. WHEN expanding a list THEN the Formatter Engine SHALL place each list element on a separate line with increased indentation
3. WHEN expanding a list THEN the Formatter Engine SHALL place the closing brace on a new line at the original indentation level
4. WHEN "Expand long lists to multiline formatting" option is disabled THEN the Formatter Engine SHALL preserve the original list formatting

### Requirement 10

**User Story:** As a TCL developer, I want the syntax validator to use a stack-based approach for brace and quote matching, so that nested structures are correctly validated.

#### Acceptance Criteria

1. WHEN the Syntax Validator encounters an opening brace or quote THEN the Syntax Validator SHALL push the character and line number onto a validation stack
2. WHEN the Syntax Validator encounters a closing brace or quote THEN the Syntax Validator SHALL pop from the stack and verify matching pairs
3. WHEN the validation stack has unmatched items after processing all lines THEN the Syntax Validator SHALL report errors for each unmatched opening character
4. WHEN a closing character has no matching opening character THEN the Syntax Validator SHALL report an error for the unexpected closing character
5. WHEN all braces and quotes are properly matched THEN the Syntax Validator SHALL return a success status with no errors

### Requirement 11

**User Story:** As a system administrator, I want clear installation and execution instructions, so that I can deploy the application without technical difficulties.

#### Acceptance Criteria

1. WHEN the application is distributed THEN the application SHALL include a requirements.txt file listing all Python dependencies
2. WHEN the application is distributed THEN the application SHALL include a README file with installation commands
3. WHEN the README provides installation instructions THEN the README SHALL specify the pip install command for PyQt6
4. WHEN the README provides execution instructions THEN the README SHALL specify the command to launch the application
5. WHEN the application is distributed THEN the application SHALL include an example TCL File demonstrating formatting capabilities

### Requirement 12

**User Story:** As a developer maintaining this application, I want the code organized into logical modules, so that the codebase is maintainable and extensible.

#### Acceptance Criteria

1. WHEN the application is structured THEN the application SHALL separate UI logic into a ui.py module
2. WHEN the application is structured THEN the application SHALL separate formatting logic into a formatter.py module
3. WHEN the application is structured THEN the application SHALL provide a main.py entry point that initializes the application
4. WHEN any module is opened THEN the module SHALL contain meaningful comments explaining complex logic
5. WHEN functions are defined THEN the functions SHALL include docstrings describing parameters and return values
