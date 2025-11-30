"""
Unit tests for Flask web API endpoints.

Tests the /format endpoint with various scenarios including:
- Valid TCL file formatting
- Invalid file extensions
- Syntax error handling
- File size validation
"""

import pytest
import os
import tempfile
from pathlib import Path
from io import BytesIO
import sys

# Add parent directory to path to import web app
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_format_endpoint_valid_file(client):
    """Test formatting a valid TCL file."""
    # Create a simple valid TCL file content
    tcl_content = b"""set x 10
set y 20
if {$x > 5} {
puts "x is greater than 5"
}"""
    
    # Send POST request with file
    data = {
        'file': (BytesIO(tcl_content), 'test.tcl'),
        'align_set': 'false',
        'expand_lists': 'false',
        'strict_indent': 'false'
    }
    
    response = client.post('/format', data=data, content_type='multipart/form-data')
    
    # Check response
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/octet-stream'
    assert 'test_formatted.tcl' in response.headers.get('Content-Disposition', '')


def test_format_endpoint_invalid_extension(client):
    """Test that invalid file extensions are rejected."""
    # Create a file with invalid extension
    content = b"some content"
    
    data = {
        'file': (BytesIO(content), 'test.txt'),
    }
    
    response = client.post('/format', data=data, content_type='multipart/form-data')
    
    # Check response
    assert response.status_code == 400
    assert response.json['error'] == 'Invalid file extension. Only .tcl files are allowed'


def test_format_endpoint_no_file(client):
    """Test that missing file is handled."""
    response = client.post('/format', data={}, content_type='multipart/form-data')
    
    # Check response
    assert response.status_code == 400
    assert response.json['error'] == 'No file provided'


def test_format_endpoint_syntax_error(client):
    """Test handling of TCL files with syntax errors."""
    # Create TCL content with unmatched brace
    tcl_content = b"""set x 10
if {$x > 5} {
puts "missing closing brace"
"""
    
    data = {
        'file': (BytesIO(tcl_content), 'test.tcl'),
        'align_set': 'false',
        'expand_lists': 'false',
        'strict_indent': 'false'
    }
    
    response = client.post('/format', data=data, content_type='multipart/form-data')
    
    # Check response - should return error log
    assert response.status_code == 200
    assert 'errors.log' in response.headers.get('Content-Disposition', '')


def test_format_endpoint_with_options(client):
    """Test formatting with various options enabled."""
    tcl_content = b"""set x 10
set variable_name 20"""
    
    data = {
        'file': (BytesIO(tcl_content), 'test.tcl'),
        'align_set': 'true',
        'expand_lists': 'false',
        'strict_indent': 'false'
    }
    
    response = client.post('/format', data=data, content_type='multipart/form-data')
    
    # Check response
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/octet-stream'


def test_index_route(client):
    """Test that the index route serves HTML."""
    response = client.get('/')
    
    # Check response
    assert response.status_code == 200
    # Note: This will fail until we create the HTML template


def test_error_handler_413(client):
    """Test that file size limit error handler works."""
    # Create a file larger than 10MB
    large_content = b'x' * (11 * 1024 * 1024)  # 11MB
    
    data = {
        'file': (BytesIO(large_content), 'large.tcl'),
    }
    
    response = client.post('/format', data=data, content_type='multipart/form-data')
    
    # Check response
    assert response.status_code == 413
    assert 'error' in response.json
    assert 'File size exceeds 10MB limit' in response.json['error']


def test_error_handler_400(client):
    """Test that bad request error handler works."""
    # Test is already covered by test_format_endpoint_no_file and test_format_endpoint_invalid_extension
    # This is just to ensure the 400 handler is registered
    response = client.post('/format', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert 'error' in response.json
