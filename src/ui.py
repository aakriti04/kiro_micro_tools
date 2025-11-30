"""
UI module for TCL Formatter & Syntax Debugger.

This module contains the TCLFormatterUI class which provides the graphical
user interface for the TCL formatter application using PyQt6.
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QTextEdit,
    QLabel,
    QFileDialog,
    QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from src.formatter import TCLFormatter, FormattingResult


class FormatterWorker(QThread):
    """
    Worker thread for running the formatter in the background.
    
    This thread prevents the UI from freezing during formatting operations
    by running the formatter in a separate thread.
    """
    
    # Signal emitted when formatting is complete
    finished = pyqtSignal(object)  # Emits FormattingResult
    
    def __init__(self, file_path: str, options: dict):
        """
        Initialize the worker thread.
        
        Args:
            file_path: Path to the TCL file to format
            options: Dictionary with formatting options (align_set, expand_lists, strict_indent)
        """
        super().__init__()
        self.file_path = file_path
        self.options = options
    
    def run(self):
        """
        Run the formatting operation in the background thread.
        
        This method is called when the thread starts. It creates a formatter
        with the specified options, formats the file, and emits the result.
        """
        # Create formatter with selected options
        formatter = TCLFormatter(
            align_set=self.options.get('align_set', False),
            expand_lists=self.options.get('expand_lists', False),
            strict_indent=self.options.get('strict_indent', False)
        )
        
        # Format the file
        result = formatter.format_file(self.file_path)
        
        # Emit the result
        self.finished.emit(result)


class TCLFormatterUI(QMainWindow):
    """
    Main window for the TCL Formatter & Syntax Debugger application.
    
    This class manages the user interface components including file selection,
    formatting options, and status display.
    """
    
    def __init__(self):
        """Initialize the main window and all UI components."""
        super().__init__()
        self.selected_file_path = None
        
        # Initialize formatting options state (session-based persistence)
        self.formatting_options = {
            'align_set': False,
            'expand_lists': False,
            'strict_indent': False
        }
        
        # Operation flag to prevent concurrent operations
        self.operation_in_progress = False
        
        # Worker thread reference
        self.worker = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create and layout all UI widgets."""
        # Set window properties
        self.setWindowTitle("TCL Formatter & Syntax Debugger")
        self.setMinimumSize(700, 500)
        self.resize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # File selection section
        file_section = self._create_file_section()
        main_layout.addWidget(file_section)
        
        # Formatting options section
        options_section = self._create_options_section()
        main_layout.addWidget(options_section)
        
        # Format button
        self.format_button = QPushButton("Format File")
        self.format_button.setEnabled(False)
        self.format_button.setMinimumHeight(40)
        self.format_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        main_layout.addWidget(self.format_button)
        
        # Status output section
        status_section = self._create_status_section()
        main_layout.addWidget(status_section)
        
        # Connect signals
        self.browse_button.clicked.connect(self.browse_file)
        self.format_button.clicked.connect(self.format_file)
        
        # Connect checkbox signals to state tracking
        self.align_set_checkbox.stateChanged.connect(self._on_align_set_changed)
        self.expand_lists_checkbox.stateChanged.connect(self._on_expand_lists_changed)
        self.strict_indent_checkbox.stateChanged.connect(self._on_strict_indent_changed)
        
        # Apply overall styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
    
    def _create_file_section(self):
        """Create the file selection section with path display and browse button."""
        group_box = QGroupBox("File Selection")
        layout = QVBoxLayout()
        
        # File path display
        path_layout = QHBoxLayout()
        path_label = QLabel("Selected File:")
        path_label.setMinimumWidth(100)
        
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        self.file_path_display.setPlaceholderText("No file selected...")
        self.file_path_display.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.file_path_display)
        
        # Browse button
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setMinimumWidth(100)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        path_layout.addWidget(self.browse_button)
        
        layout.addLayout(path_layout)
        group_box.setLayout(layout)
        
        return group_box
    
    def _create_options_section(self):
        """Create the formatting options section with checkboxes."""
        group_box = QGroupBox("Formatting Options")
        layout = QVBoxLayout()
        
        # Create three checkboxes for formatting options
        self.align_set_checkbox = QCheckBox("Align set commands")
        self.align_set_checkbox.setToolTip(
            "Align assignment values in consecutive set commands"
        )
        
        self.expand_lists_checkbox = QCheckBox("Expand long lists to multiline formatting")
        self.expand_lists_checkbox.setToolTip(
            "Expand lists exceeding 80 characters to multiple lines"
        )
        
        self.strict_indent_checkbox = QCheckBox("Strict indentation mode")
        self.strict_indent_checkbox.setToolTip(
            "Enforce consistent indentation for continuation lines"
        )
        
        # Apply checkbox styling
        checkbox_style = """
            QCheckBox {
                spacing: 8px;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """
        self.align_set_checkbox.setStyleSheet(checkbox_style)
        self.expand_lists_checkbox.setStyleSheet(checkbox_style)
        self.strict_indent_checkbox.setStyleSheet(checkbox_style)
        
        layout.addWidget(self.align_set_checkbox)
        layout.addWidget(self.expand_lists_checkbox)
        layout.addWidget(self.strict_indent_checkbox)
        
        group_box.setLayout(layout)
        
        return group_box
    
    def _create_status_section(self):
        """Create the status output section."""
        group_box = QGroupBox("Status")
        layout = QVBoxLayout()
        
        self.status_output = QTextEdit()
        self.status_output.setReadOnly(True)
        self.status_output.setPlaceholderText("Ready to format TCL files...")
        self.status_output.setMinimumHeight(150)
        self.status_output.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        
        layout.addWidget(self.status_output)
        group_box.setLayout(layout)
        
        return group_box
    
    def browse_file(self):
        """
        Open file dialog and select TCL file.
        
        Opens a QFileDialog filtered to show only .tcl files. Validates the
        selected file has a .tcl extension, updates the file path display,
        and enables the format button if a valid file is selected.
        """
        # Open file dialog with .tcl filter
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select TCL File",
            "",
            "TCL Files (*.tcl);;All Files (*)"
        )
        
        # Check if user selected a file (not cancelled)
        if file_path:
            # Validate file has .tcl extension
            if file_path.lower().endswith('.tcl'):
                # Store the selected file path
                self.selected_file_path = file_path
                
                # Update file path display with selected file
                self.file_path_display.setText(file_path)
                
                # Enable format button when valid file is selected
                self.format_button.setEnabled(True)
                
                # Clear any previous error messages
                self.status_output.clear()
                self.update_status("File selected successfully. Ready to format.", is_error=False)
            else:
                # Display error message for invalid file selection
                self.selected_file_path = None
                self.file_path_display.clear()
                self.format_button.setEnabled(False)
                self.update_status(
                    f"Error: Invalid file selection. Please select a file with .tcl extension.\n"
                    f"Selected file: {file_path}",
                    is_error=True
                )
    
    def _on_align_set_changed(self, state):
        """
        Handle align set commands checkbox state change.
        
        Args:
            state: Qt.CheckState value (Checked or Unchecked)
        """
        self.formatting_options['align_set'] = (state == Qt.CheckState.Checked.value)
    
    def _on_expand_lists_changed(self, state):
        """
        Handle expand lists checkbox state change.
        
        Args:
            state: Qt.CheckState value (Checked or Unchecked)
        """
        self.formatting_options['expand_lists'] = (state == Qt.CheckState.Checked.value)
    
    def _on_strict_indent_changed(self, state):
        """
        Handle strict indentation checkbox state change.
        
        Args:
            state: Qt.CheckState value (Checked or Unchecked)
        """
        self.formatting_options['strict_indent'] = (state == Qt.CheckState.Checked.value)
    
    def get_formatting_options(self):
        """
        Get the current formatting options state.
        
        Returns:
            Dictionary with 'align_set', 'expand_lists', and 'strict_indent' keys
        """
        return self.formatting_options.copy()
    
    def format_file(self):
        """
        Invoke formatter with selected options and display results.
        
        This method:
        1. Checks if an operation is already in progress (prevents concurrent operations)
        2. Disables the format button and shows processing indicator
        3. Creates a QThread worker for background formatting
        4. Connects the worker's finished signal to handle results
        5. Starts the worker thread
        """
        # Prevent concurrent operations
        if self.operation_in_progress:
            return
        
        # Check if a file is selected
        if not self.selected_file_path:
            self.update_status("Error: No file selected.", is_error=True)
            return
        
        # Set operation flag
        self.operation_in_progress = True
        
        # Disable format button during operation
        self.format_button.setEnabled(False)
        
        # Show processing indicator
        self.update_status("Processing...", is_error=False)
        
        # Create worker thread with selected file and options
        self.worker = FormatterWorker(
            file_path=self.selected_file_path,
            options=self.get_formatting_options()
        )
        
        # Connect worker's finished signal to result handler
        self.worker.finished.connect(self._on_formatting_complete)
        
        # Start the worker thread
        self.worker.start()
    
    def _on_formatting_complete(self, result: FormattingResult):
        """
        Handle formatting operation completion.
        
        This method is called when the worker thread finishes. It:
        1. Processes the formatting result (success or error)
        2. Updates the status display with appropriate message
        3. Re-enables the format button
        4. Clears the operation flag
        
        Args:
            result: FormattingResult object from the formatter
        """
        # Handle the result based on success status
        if result.success:
            # Success - display output file path
            message = f"✓ Formatting completed successfully!\n\n"
            message += f"Output file: {result.output_path}"
            self.update_status(message, is_error=False)
        else:
            # Check if this is a syntax error or file access error
            if result.errors:
                # Syntax errors detected
                error_count = len(result.errors)
                message = f"✗ Syntax validation failed!\n\n"
                message += f"Found {error_count} error(s).\n"
                message += f"Error log: {result.error_path}\n\n"
                message += "Errors:\n"
                # Show first few errors in the status display
                for i, error in enumerate(result.errors[:5]):
                    message += f"  Line {error.line_number}: {error.message}\n"
                if error_count > 5:
                    message += f"  ... and {error_count - 5} more error(s)\n"
                self.update_status(message, is_error=True)
            else:
                # File access or other error
                message = f"✗ Formatting failed!\n\n"
                message += result.message
                self.update_status(message, is_error=True)
        
        # Re-enable format button after completion
        self.format_button.setEnabled(True)
        
        # Clear operation flag
        self.operation_in_progress = False
        
        # Clean up worker reference
        self.worker = None
    
    def update_status(self, message: str, is_error: bool = False):
        """
        Update status display with message.
        
        Args:
            message: The status message to display
            is_error: Whether this is an error message (affects styling)
        """
        # Set text color based on error status
        if is_error:
            color = "#d32f2f"  # Red for errors
        else:
            color = "#2e7d32"  # Green for success
        
        # Update status output with colored message
        self.status_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                color: {color};
            }}
        """)
        self.status_output.setText(message)
