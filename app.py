#!/usr/bin/env python3
"""
DazzloDocs Converter - Professional File Conversion Service
A modern, robust web application for converting files between various formats.
Enhanced for maximum compatibility and features.
"""

import os
import uuid
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Import our custom modules
from config import Config
from utils.file_handler import FileHandler
from utils.converter import FileConverter
from utils.validators import FileValidator
from utils.cleanup import CleanupManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

# Initialize components
file_handler = FileHandler()
converter = FileConverter()
validator = FileValidator()
cleanup_manager = CleanupManager()

# Start cleanup thread
cleanup_manager.start_cleanup_thread()

@app.route('/')
def index():
    """Main page with enhanced UI"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Enhanced API endpoint for file upload and conversion"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        target_format = request.form.get('target_format', '').lower()
        
        # Get advanced options
        image_quality = request.form.get('image_quality', '85')
        pdf_resolution = request.form.get('pdf_resolution', '300')
        
        # Validate input
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not target_format:
            return jsonify({
                'success': False,
                'error': 'Target format not specified'
            }), 400
        
        # Debug logging
        logger.info(f"Received file: {file.filename}")
        logger.info(f"Target format: {target_format}")
        logger.info(f"Form data: {dict(request.form)}")
        
        # Validate file
        if not validator.is_allowed_file(file.filename):
            supported_formats = validator.get_supported_formats()
            format_list = []
            for category, formats in supported_formats.items():
                format_list.extend(formats)
            logger.error(f"File type not supported: {file.filename}")
            return jsonify({
                'success': False,
                'error': f'File type not supported. Allowed types: {", ".join(sorted(set(format_list)))}'
            }), 400
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        input_filename = f"{unique_id}_{original_filename}"
        
        # Save uploaded file
        input_path = file_handler.save_uploaded_file(file, input_filename)
        
        # Enhanced file validation
        logger.info(f"Validating file: {input_path}")
        validation_result = validator.validate_file(input_path, original_filename)
        logger.info(f"Validation result: {validation_result}")
        if not validation_result['valid']:
            # Clean up invalid file
            file_handler.delete_file(input_path)
            logger.error(f"File validation failed: {validation_result['error']}")
            return jsonify({
                'success': False,
                'error': validation_result['error']
            }), 400
        
        # Generate output filename
        output_filename = f"{unique_id}_converted_{Path(original_filename).stem}.{target_format}"
        output_path = os.path.join(Config.CONVERTED_FOLDER, output_filename)
        
        # Update converter settings with advanced options
        if image_quality.isdigit():
            converter.image_quality = int(image_quality)
        if pdf_resolution.isdigit():
            converter.pdf_resolution = int(pdf_resolution)
        
        # Perform conversion
        logger.info(f"Starting conversion: {original_filename} -> {target_format}")
        logger.info(f"Input path: {input_path}")
        logger.info(f"Output path: {output_path}")
        logger.info(f"Input file exists: {os.path.exists(input_path)}")
        logger.info(f"Input file size: {os.path.getsize(input_path) if os.path.exists(input_path) else 'N/A'}")
        conversion_result = converter.convert_file(input_path, output_path, target_format)
        logger.info(f"Conversion result: {conversion_result}")
        
        if conversion_result['success']:
            # Clean up input file
            file_handler.delete_file(input_path)
            
            # Schedule cleanup of output file
            cleanup_manager.schedule_cleanup(output_path)
            
            download_url = url_for('download_file', filename=output_filename)
            
            logger.info(f"Conversion successful: {output_filename}")
            return jsonify({
                'success': True,
                'download_url': download_url,
                'filename': output_filename,
                'original_filename': original_filename,
                'target_format': target_format,
                'file_size': validation_result.get('file_size', 0)
            })
        else:
            # Clean up input file on conversion failure
            file_handler.delete_file(input_path)
            return jsonify({
                'success': False,
                'error': conversion_result.get('error', 'Conversion failed')
            }), 500
            
    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'error': 'File too large. Maximum file size is 100MB.'
        }), 413
    except Exception as e:
        logger.error(f"API upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Enhanced form-based file upload endpoint"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        target_format = request.form.get('target_format', '').lower()
        
        # Get advanced options
        image_quality = request.form.get('image_quality', '85')
        pdf_resolution = request.form.get('pdf_resolution', '300')
        
        # Validate input
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if not target_format:
            flash('Please select a target format', 'error')
            return redirect(request.url)
        
        # Validate file
        if not validator.is_allowed_file(file.filename):
            supported_formats = validator.get_supported_formats()
            format_list = []
            for category, formats in supported_formats.items():
                format_list.extend(formats)
            flash(f'File type not supported. Allowed types: {", ".join(sorted(set(format_list)))}', 'error')
            return redirect(request.url)
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        input_filename = f"{unique_id}_{original_filename}"
        
        # Save uploaded file
        input_path = file_handler.save_uploaded_file(file, input_filename)
        
        # Enhanced file validation
        validation_result = validator.validate_file(input_path, original_filename)
        if not validation_result['valid']:
            # Clean up invalid file
            file_handler.delete_file(input_path)
            flash(validation_result['error'], 'error')
            return redirect(request.url)
        
        # Generate output filename
        output_filename = f"{unique_id}_converted_{Path(original_filename).stem}.{target_format}"
        output_path = os.path.join(Config.CONVERTED_FOLDER, output_filename)
        
        # Update converter settings with advanced options
        if image_quality.isdigit():
            converter.image_quality = int(image_quality)
        if pdf_resolution.isdigit():
            converter.pdf_resolution = int(pdf_resolution)
        
        # Perform conversion
        logger.info(f"Starting conversion: {original_filename} -> {target_format}")
        conversion_result = converter.convert_file(input_path, output_path, target_format)
        
        if conversion_result['success']:
            # Clean up input file
            file_handler.delete_file(input_path)
            
            # Schedule cleanup of output file
            cleanup_manager.schedule_cleanup(output_path)
            
            # Redirect to success page
            flash(f'File converted successfully! Original: {original_filename} -> {target_format.upper()}', 'success')
            return redirect(url_for('success', filename=output_filename))
        else:
            # Clean up input file on conversion failure
            file_handler.delete_file(input_path)
            flash(f'Conversion failed: {conversion_result.get("error", "Unknown error")}', 'error')
            return redirect(request.url)
            
    except RequestEntityTooLarge:
        flash('File too large. Maximum file size is 100MB.', 'error')
        return redirect(request.url)
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        flash(f'Server error: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/download/<filename>')
def download_file(filename):
    """Download converted file"""
    try:
        file_path = os.path.join(Config.CONVERTED_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return "File not found", 404
        
        # Get original filename for download
        original_name = filename.split('_converted_', 1)[-1] if '_converted_' in filename else filename
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=original_name,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return "Download error", 500

@app.route('/success/<filename>')
def success(filename):
    """Success page after conversion"""
    try:
        file_path = os.path.join(Config.CONVERTED_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return "File not found", 404
        
        # Get file info
        file_size = os.path.getsize(file_path)
        original_name = filename.split('_converted_', 1)[-1] if '_converted_' in filename else filename
        
        return render_template('success.html', 
                             filename=filename,
                             original_name=original_name,
                             file_size=file_size,
                             download_url=url_for('download_file', filename=filename))
        
    except Exception as e:
        logger.error(f"Success page error: {str(e)}")
        return "Error", 500

@app.route('/api/formats')
def get_formats():
    """API endpoint to get supported formats"""
    try:
        supported_formats = validator.get_supported_formats()
        return jsonify({
            'success': True,
            'formats': supported_formats
        })
    except Exception as e:
        logger.error(f"Formats API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/format-info/<extension>')
def get_format_info(extension):
    """API endpoint to get format information"""
    try:
        format_info = validator.get_format_info(extension)
        return jsonify({
            'success': True,
            'format_info': format_info
        })
    except Exception as e:
        logger.error(f"Format info API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversion-options/<input_format>')
def get_conversion_options(input_format):
    """API endpoint to get conversion options for a format"""
    try:
        options = converter.get_conversion_options(input_format)
        return jsonify({
            'success': True,
            'options': options
        })
    except Exception as e:
        logger.error(f"Conversion options API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Enhanced health check endpoint"""
    try:
        # Check if all components are working
        components_status = {
            'file_handler': True,
            'converter': True,
            'validator': True,
            'cleanup_manager': True
        }
        
        # Check if directories exist
        directories_status = {
            'uploads': os.path.exists(Config.UPLOAD_FOLDER),
            'converted': os.path.exists(Config.CONVERTED_FOLDER)
        }
        
        # Check converter capabilities (only the ones that exist in our simplified converter)
        converter_capabilities = {
            'pil_available': converter.pil_available,
            'pymupdf_available': converter.pymupdf_available,
            'reportlab_available': converter.reportlab_available,
            'docx_available': converter.docx_available
        }
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': components_status,
            'directories': directories_status,
            'converter_capabilities': converter_capabilities,
            'supported_formats': validator.get_supported_formats()
        })
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health')
def health():
    """Simple health check for load balancers"""
    return "OK", 200

@app.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """500 error handler"""
    return render_template('500.html'), 500

@app.errorhandler(413)
def too_large(e):
    """413 error handler for large files"""
    return render_template('413.html'), 413

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)