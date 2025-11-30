"""
Flask backend for TCL Formatter web interface.

This module provides a REST API for formatting TCL files through a web interface.
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
import tempfile
from io import BytesIO
from werkzeug.utils import secure_filename
from src.formatter import TCLFormatter, FormattingResult

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
ALLOWED_EXTENSIONS = {'tcl'}


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/format', methods=['POST'])
def format_tcl_file():
    """
    Handle file upload and formatting request.
    
    Expects multipart/form-data with:
    - file: TCL file to format
    - align_set: boolean (optional)
    - expand_lists: boolean (optional)
    - strict_indent: boolean (optional)
    
    Returns formatted file or error log on success, JSON error on failure.
    """
    # Validate file upload
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file extension. Only .tcl files are allowed'}), 400
    
    # Parse formatting options
    align_set = request.form.get('align_set', 'false').lower() == 'true'
    expand_lists = request.form.get('expand_lists', 'false').lower() == 'true'
    strict_indent = request.form.get('strict_indent', 'false').lower() == 'true'
    
    # Create temporary files for processing
    input_temp = None
    output_file = None
    error_file = None
    
    try:
        # Save uploaded file to temporary location
        input_temp = tempfile.NamedTemporaryFile(mode='w+b', suffix='.tcl', delete=False)
        file.save(input_temp.name)
        input_temp.close()
        
        # Create formatter and process file
        formatter = TCLFormatter(
            align_set=align_set,
            expand_lists=expand_lists,
            strict_indent=strict_indent
        )
        
        result = formatter.format_file(input_temp.name)
        
        # Handle formatting result
        if result.success:
            # Return formatted file
            output_file = result.output_path
            if not output_file or not os.path.exists(output_file):
                return jsonify({'error': 'Formatted file not found'}), 500
            
            # Generate output filename
            original_name = secure_filename(file.filename)
            base_name = original_name.rsplit('.', 1)[0]
            output_filename = f"{base_name}_formatted.tcl"
            
            # Read file content before cleanup
            with open(output_file, 'rb') as f:
                file_content = f.read()
            
            # Clean up before sending response
            try:
                os.unlink(output_file)
            except Exception:
                pass
            
            # Send file from memory
            return send_file(
                BytesIO(file_content),
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/octet-stream'
            )
        else:
            # Return error log
            error_file = result.error_path
            if not error_file or not os.path.exists(error_file):
                return jsonify({'error': 'Error log not found'}), 500
            
            # Read file content before cleanup
            with open(error_file, 'rb') as f:
                file_content = f.read()
            
            # Clean up before sending response
            try:
                os.unlink(error_file)
            except Exception:
                pass
            
            # Send file from memory
            return send_file(
                BytesIO(file_content),
                as_attachment=True,
                download_name='errors.log',
                mimetype='application/octet-stream'
            )
    
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500
    
    finally:
        # Clean up temporary files
        try:
            if input_temp and os.path.exists(input_temp.name):
                os.unlink(input_temp.name)
        except Exception:
            pass


@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({'error': 'Bad request'}), 400


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({'error': 'File size exceeds 10MB limit'}), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
