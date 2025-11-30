"""
Main entry point for the TCL Formatter & Syntax Debugger application.

This module initializes the PyQt6 application and launches the main window.
It includes proper error handling for application startup failures.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from src.ui import TCLFormatterUI


def main():
    """
    Initialize and run the TCL Formatter application.
    
    This function:
    1. Creates a QApplication instance
    2. Creates and shows the main window
    3. Executes the application event loop
    4. Handles any startup errors gracefully
    
    Returns:
        int: Application exit code (0 for success, non-zero for errors)
    """
    try:
        # Create QApplication instance
        # sys.argv is passed to support command-line arguments in the future
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName("TCL Formatter & Syntax Debugger")
        app.setOrganizationName("TCL Tools")
        app.setApplicationVersion("1.0.0")
        
        # Create and show main window
        main_window = TCLFormatterUI()
        main_window.show()
        
        # Execute application event loop
        # This blocks until the application exits
        return app.exec()
        
    except ImportError as e:
        # Handle missing dependencies
        error_msg = (
            f"Failed to import required modules:\n{str(e)}\n\n"
            "Please ensure all dependencies are installed:\n"
            "pip install -r requirements.txt"
        )
        print(f"ERROR: {error_msg}", file=sys.stderr)
        
        # Try to show a GUI error dialog if PyQt6 is available
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Import Error", error_msg)
        except:
            pass  # If PyQt6 isn't available, we already printed to stderr
        
        return 1
        
    except Exception as e:
        # Handle any other startup errors
        error_msg = (
            f"Application startup failed:\n{str(e)}\n\n"
            "Please check the error message above and try again."
        )
        print(f"ERROR: {error_msg}", file=sys.stderr)
        
        # Try to show a GUI error dialog
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Startup Error", error_msg)
        except:
            pass  # If we can't show GUI, we already printed to stderr
        
        return 1


if __name__ == "__main__":
    # Run the application and exit with the returned code
    sys.exit(main())
