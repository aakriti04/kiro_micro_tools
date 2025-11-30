/**
 * TCL Formatter Web Interface - Client-side Logic
 * 
 * Handles file selection, form submission, and status display for the web interface.
 */

// DOM Elements
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const formatBtn = document.getElementById('formatBtn');
const statusDisplay = document.getElementById('status');
const alignSetCheckbox = document.getElementById('alignSet');
const expandListsCheckbox = document.getElementById('expandLists');
const strictIndentCheckbox = document.getElementById('strictIndent');

// File selection handling
fileInput.addEventListener('change', handleFileSelection);

/**
 * Handle file selection and validation.
 * Validates file extension and enables/disables format button.
 */
function handleFileSelection(event) {
    try {
        const file = event.target.files[0];
        
        if (!file) {
            fileName.textContent = 'No file selected';
            formatBtn.disabled = true;
            clearStatus();
            return;
        }
        
        // Validate file extension
        const fileExtension = file.name.split('.').pop().toLowerCase();
        
        if (fileExtension !== 'tcl') {
            fileName.textContent = file.name;
            formatBtn.disabled = true;
            updateStatus('Invalid file extension. Please select a .tcl file.', true);
            return;
        }
        
        // Valid file selected
        fileName.textContent = file.name;
        formatBtn.disabled = false;
        clearStatus();
    } catch (error) {
        updateStatus(`Error selecting file: ${error.message}`, true);
        formatBtn.disabled = true;
    }
}

// Format button click handler
formatBtn.addEventListener('click', formatFile);

/**
 * Handle form submission and file formatting.
 * Builds FormData, sends POST request, and handles response.
 */
async function formatFile() {
    try {
        const file = fileInput.files[0];
        
        if (!file) {
            updateStatus('Please select a file first.', true);
            return;
        }
        
        // Build FormData with file and options
        const formData = new FormData();
        formData.append('file', file);
        formData.append('align_set', alignSetCheckbox.checked ? 'true' : 'false');
        formData.append('expand_lists', expandListsCheckbox.checked ? 'true' : 'false');
        formData.append('strict_indent', strictIndentCheckbox.checked ? 'true' : 'false');
        
        // Show processing indicator
        updateStatus('Processing file...', false, true);
        formatBtn.disabled = true;
        
        try {
            // Send POST request to /format endpoint with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
            
            const response = await fetch('/format', {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            // Handle response
            if (response.ok) {
                await handleSuccessResponse(response);
            } else {
                await handleErrorResponse(response);
            }
        } catch (error) {
            // Handle network errors
            if (error.name === 'AbortError') {
                updateStatus('Request timed out. Please try again.', true);
            } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                updateStatus('Unable to connect to server. Please check your connection.', true);
            } else {
                updateStatus(`Network error: ${error.message}`, true);
            }
        } finally {
            // Re-enable format button
            formatBtn.disabled = false;
        }
    } catch (error) {
        // Catch any unexpected errors in the outer scope
        updateStatus(`Unexpected error: ${error.message}`, true);
        formatBtn.disabled = false;
    }
}

/**
 * Handle successful response with file download.
 * Creates blob from response and triggers download.
 * 
 * @param {Response} response - Fetch API response object
 */
async function handleSuccessResponse(response) {
    try {
        // Get filename from Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'formatted_file.tcl';
        
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1];
            }
        }
        
        // Create blob from response
        const blob = await response.blob();
        
        // Trigger download
        downloadFile(blob, filename);
        
        // Update status based on filename
        if (filename === 'errors.log') {
            // Count errors in the log
            const text = await blob.text();
            const errorCount = (text.match(/Line \d+:/g) || []).length;
            updateStatus(`Syntax errors detected (${errorCount} error${errorCount !== 1 ? 's' : ''}). Error log downloaded.`, true);
        } else {
            updateStatus('File formatted successfully! Download started.', false);
        }
    } catch (error) {
        updateStatus(`Error processing response: ${error.message}`, true);
    }
}

/**
 * Handle error response from server.
 * Parses JSON error message and displays it.
 * 
 * @param {Response} response - Fetch API response object
 */
async function handleErrorResponse(response) {
    try {
        const errorData = await response.json();
        const errorMessage = errorData.error || 'An unknown error occurred';
        updateStatus(errorMessage, true);
    } catch (error) {
        // If JSON parsing fails, show generic error
        updateStatus(`Server error (${response.status}): ${response.statusText}`, true);
    }
}

/**
 * Trigger file download in browser.
 * Creates temporary anchor element and clicks it.
 * 
 * @param {Blob} blob - File content as blob
 * @param {string} filename - Name for downloaded file
 */
function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

/**
 * Update status display with message and styling.
 * 
 * @param {string} message - Status message to display
 * @param {boolean} isError - Whether this is an error message
 * @param {boolean} isProcessing - Whether this is a processing indicator
 */
function updateStatus(message, isError = false, isProcessing = false) {
    statusDisplay.textContent = message;
    statusDisplay.className = 'status-display';
    
    if (isProcessing) {
        statusDisplay.classList.add('processing');
    } else if (isError) {
        statusDisplay.classList.add('error');
    } else {
        statusDisplay.classList.add('success');
    }
}

/**
 * Clear status display.
 */
function clearStatus() {
    statusDisplay.textContent = '';
    statusDisplay.className = 'status-display';
}
