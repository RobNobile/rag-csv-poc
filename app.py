#!/usr/bin/env python3
"""
Vehicle Mapping RAG - Flask Web Application

This Flask app provides a web interface for the vehicle mapping RAG system,
with CSV file upload and interactive chat functionality.
"""

import os
import atexit
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from vehicle_rag import VehicleRAG

# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Single global RAG instance
rag_instance = VehicleRAG()


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle CSV file upload and initialize RAG system.

    Returns:
        JSON response with success status and metadata
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']

        # Check if file was selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Please upload a CSV file.'
            }), 400

        # Save file securely
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Initialize RAG system
        result = rag_instance.initialize_from_csv(filepath)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Error processing upload: {str(e)}'
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Process a chat message through the RAG system.

    Expected JSON body:
        {
            "message": "user's question"
        }

    Returns:
        JSON response with AI answer
    """
    try:
        # Get message from request
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400

        message = data['message'].strip()

        if not message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400

        # Check if RAG is initialized
        if not rag_instance.initialized:
            return jsonify({
                'success': False,
                'error': 'RAG system not initialized',
                'response': 'Please upload a CSV file first to initialize the system.'
            }), 400

        # Process query
        result = rag_instance.query(message)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': f'Error processing message: {str(e)}'
        }), 500


@app.route('/api/status', methods=['GET'])
def status():
    """
    Get the current status of the RAG system.

    Returns:
        JSON response with system status and statistics
    """
    try:
        stats = rag_instance.get_stats()

        return jsonify({
            'success': True,
            'status': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/reset', methods=['POST'])
def reset():
    """
    Reset the RAG system.

    Returns:
        JSON response confirming reset
    """
    try:
        # Reset RAG instance
        rag_instance.reset()

        # Clean up uploaded files
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            import shutil
            for item in os.listdir(app.config['UPLOAD_FOLDER']):
                item_path = os.path.join(app.config['UPLOAD_FOLDER'], item)
                if os.path.isfile(item_path):
                    os.remove(item_path)

        return jsonify({
            'success': True,
            'message': 'RAG system reset successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Error resetting system: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint.

    Returns:
        JSON response indicating service health
    """
    try:
        # Check if Ollama is accessible (optional)
        return jsonify({
            'success': True,
            'status': 'healthy',
            'message': 'Vehicle Mapping RAG service is running'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size limit exceeded."""
    return jsonify({
        'success': False,
        'error': 'File size exceeds maximum limit (10MB)'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


def cleanup_on_shutdown():
    """Clean up uploaded files on shutdown."""
    if os.path.exists(UPLOAD_FOLDER):
        for item in os.listdir(UPLOAD_FOLDER):
            item_path = os.path.join(UPLOAD_FOLDER, item)
            if os.path.isfile(item_path):
                try:
                    os.remove(item_path)
                except Exception:
                    pass  # Silently ignore cleanup errors


# Register cleanup function to run on shutdown
atexit.register(cleanup_on_shutdown)


if __name__ == '__main__':
    print("=" * 50)
    print("🚗 Vehicle Mapping RAG Web Application")
    print("=" * 50)
    print("\n🌐 Starting server...")
    print("  • Open http://localhost:5001 in your browser")
    print("=" * 50)
    print()

    # Run Flask app
    app.run(debug=False, host='0.0.0.0', port=5001)
