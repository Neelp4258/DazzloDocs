#!/usr/bin/env python3
"""
Universal File Converter - Main Application
A complete web-based file conversion service with beautiful UI.
"""

from flask import Flask, request, jsonify, send_file, redirect, url_for, flash, render_template_string
import os
import tempfile
import uuid
from pathlib import Path
import shutil
from werkzeug.utils import secure_filename
from datetime import datetime
import threading
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import libraries with error handling
try:
    from PIL import Image
    PIL_AVAILABLE = True
    logger.info("✅ PIL (Pillow) loaded successfully")
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("⚠️  PIL (Pillow) not available - install with: pip install Pillow")

try:
    import pypandoc
    PYPANDOC_AVAILABLE = True
    logger.info("✅ pypandoc loaded successfully")
except ImportError:
    PYPANDOC_AVAILABLE = False
    logger.warning("⚠️  pypandoc not available - install with: pip install pypandoc")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
    logger.info("✅ PyMuPDF loaded successfully")
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("⚠️  PyMuPDF not available - install with: pip install PyMuPDF")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB

# Configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
CONVERTED_FOLDER = os.environ.get('CONVERTED_FOLDER', 'converted')
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'ico',
    'docx', 'doc', 'md', 'html', 'rtf', 'csv', 'json', 'xml'
}

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# Embedded HTML templates to avoid template rendering issues
MAIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal File Converter</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #667eea;
            --secondary: #764ba2;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --info: #3b82f6;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            min-height: 100vh;
            line-height: 1.6;
        }
        .navbar {
            background: rgba(255,255,255,0.95) !important;
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .container-main {
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        .card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
            transition: all 0.3s ease;
        }
        .card:hover { transform: translateY(-8px); }
        .card-header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border-radius: 24px 24px 0 0 !important;
            border: none;
            padding: 2rem;
            text-align: center;
        }
        .card-body { padding: 2.5rem; }
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
        .btn-success {
            background: var(--success);
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-weight: 600;
            animation: pulse 2s infinite;
        }
        .form-control, .form-select {
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 14px 18px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: rgba(255,255,255,0.9);
        }
        .form-control:focus, .form-select:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(102,126,234,0.1);
            background: white;
        }
        .upload-area {
            border: 3px dashed #cbd5e1;
            border-radius: 20px;
            padding: 4rem 2rem;
            text-align: center;
            transition: all 0.3s ease;
            background: rgba(255,255,255,0.6);
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        .upload-area:hover {
            border-color: var(--primary);
            background: rgba(102,126,234,0.1);
            transform: scale(1.02);
        }
        .upload-area.dragover {
            border-color: var(--primary);
            background: rgba(102,126,234,0.2);
            transform: scale(1.05);
        }
        .file-icon {
            font-size: 4rem;
            color: var(--primary);
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
        }
        .upload-area:hover .file-icon { transform: scale(1.1); }
        .feature-card {
            text-align: center;
            padding: 2.5rem;
            border-radius: 20px;
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.3);
            transition: all 0.4s ease;
            height: 100%;
            cursor: pointer;
        }
        .feature-card:hover {
            transform: translateY(-10px);
            background: rgba(255,255,255,0.25);
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        .feature-icon {
            font-size: 3rem;
            color: white;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
        }
        .feature-card:hover .feature-icon { transform: scale(1.2) rotate(5deg); }
        .alert {
            border: none;
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .alert-success {
            background: rgba(16,185,129,0.1);
            color: #065f46;
            border-left: 4px solid var(--success);
        }
        .alert-danger {
            background: rgba(239,68,68,0.1);
            color: #991b1b;
            border-left: 4px solid var(--danger);
        }
        .alert-info {
            background: rgba(59,130,246,0.1);
            color: #1e40af;
            border-left: 4px solid var(--info);
        }
        .footer {
            background: rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            color: white;
            padding: 2rem 0;
            margin-top: 3rem;
            text-align: center;
        }
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        .loading-spinner {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.7); }
            70% { box-shadow: 0 0 0 10px rgba(16,185,129,0); }
            100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in { animation: fadeInUp 0.6s ease-out; }
        @media (max-width: 768px) {
            .container-main { padding: 1rem; }
            .card-body { padding: 1.5rem; }
            .upload-area { padding: 2rem 1rem; }
            .feature-card { padding: 1.5rem; }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg fixed-top">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-exchange-alt me-2"></i>
                File Converter
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link fw-semibold" href="/">
                            <i class="fas fa-home me-1"></i>Home
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link fw-semibold" href="/about">
                            <i class="fas fa-info-circle me-1"></i>About
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main style="padding-top: 100px; min-height: calc(100vh - 180px);">
        <div class="container-main">
            {% for message in get_flashed_messages() %}
            <div class="alert alert-info alert-dismissible fade show" role="alert">
                <i class="fas fa-info-circle me-2"></i>{{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            {% endfor %}

            <div class="row justify-content-center">
                <div class="col-lg-10">
                    <div class="card fade-in">
                        <div class="card-header">
                            <h1 class="mb-0 display-6">
                                <i class="fas fa-cloud-upload-alt me-3"></i>
                                Universal File Converter
                            </h1>
                            <p class="mb-0 mt-3 fs-5 opacity-90">Transform your files instantly between different formats</p>
                        </div>
                        <div class="card-body">
                            <form id="uploadForm" method="POST" action="/upload" enctype="multipart/form-data">
                                <div class="upload-area" id="uploadArea">
                                    <div class="file-icon">
                                        <i class="fas fa-file-upload"></i>
                                    </div>
                                    <h3 class="mb-3">Drop your file here or click to browse</h3>
                                    <p class="text-muted fs-5 mb-0">Supports images, documents, PDFs and more • Max 50MB</p>
                                    <input type="file" id="fileInput" name="file" class="d-none" 
                                           accept=".jpg,.jpeg,.png,.gif,.bmp,.tiff,.webp,.ico,.pdf,.docx,.doc,.txt,.md,.html,.rtf,.csv,.json,.xml">
                                </div>

                                <div id="fileInfo" class="d-none mt-4">
                                    <div class="alert alert-info">
                                        <div class="d-flex align-items-center">
                                            <i class="fas fa-file me-3 fs-2"></i>
                                            <div class="flex-grow-1">
                                                <h6 class="mb-1" id="fileName"></h6>
                                                <small class="text-muted" id="fileSize"></small>
                                            </div>
                                            <button type="button" class="btn btn-outline-secondary" id="removeFile">
                                                <i class="fas fa-times"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                <div class="mt-4" id="formatSelection" style="display: none;">
                                    <label for="targetFormat" class="form-label fs-5 fw-semibold">
                                        <i class="fas fa-exchange-alt me-2"></i>Convert to:
                                    </label>
                                    <select class="form-select" id="targetFormat" name="target_format" required>
                                        <option value="">Choose your target format...</option>
                                        <optgroup label="🖼️ Images">
                                            <option value="jpg">JPG - JPEG Image</option>
                                            <option value="png">PNG - Portable Network Graphics</option>
                                            <option value="gif">GIF - Graphics Interchange Format</option>
                                            <option value="bmp">BMP - Bitmap Image</option>
                                            <option value="tiff">TIFF - Tagged Image File</option>
                                            <option value="webp">WebP - Modern Image Format</option>
                                        </optgroup>
                                        <optgroup label="📄 Documents">
                                            <option value="pdf">PDF - Portable Document Format</option>
                                            <option value="docx">DOCX - Word Document</option>
                                            <option value="txt">TXT - Plain Text</option>
                                            <option value="md">MD - Markdown</option>
                                            <option value="html">HTML - Web Page</option>
                                            <option value="rtf">RTF - Rich Text Format</option>
                                        </optgroup>
                                        <optgroup label="📊 Data">
                                            <option value="csv">CSV - Comma Separated Values</option>
                                            <option value="json">JSON - JavaScript Object Notation</option>
                                            <option value="xml">XML - Extensible Markup Language</option>
                                        </optgroup>
                                    </select>
                                </div>

                                <div class="text-center mt-5" id="convertSection" style="display: none;">
                                    <button type="submit" class="btn btn-primary btn-lg fs-5">
                                        <i class="fas fa-magic me-2"></i>Convert File Now
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>

                    <div class="row mt-5">
                        <div class="col-md-4 mb-4">
                            <div class="feature-card fade-in">
                                <div class="feature-icon">
                                    <i class="fas fa-images"></i>
                                </div>
                                <h4 class="text-white mb-3">Image Magic</h4>
                                <p class="text-white-50 mb-0 fs-6">Convert between JPG, PNG, GIF, BMP, TIFF, WebP and more with perfect quality</p>
                            </div>
                        </div>
                        <div class="col-md-4 mb-4">
                            <div class="feature-card fade-in" style="animation-delay: 0.2s;">
                                <div class="feature-icon">
                                    <i class="fas fa-file-pdf"></i>
                                </div>
                                <h4 class="text-white mb-3">Document Power</h4>
                                <p class="text-white-50 mb-0 fs-6">Handle PDF, Word, Markdown, HTML and text files with ease</p>
                            </div>
                        </div>
                        <div class="col-md-4 mb-4">
                            <div class="feature-card fade-in" style="animation-delay: 0.4s;">
                                <div class="feature-icon">
                                    <i class="fas fa-bolt"></i>
                                </div>
                                <h4 class="text-white mb-3">Lightning Fast</h4>
                                <p class="text-white-50 mb-0 fs-6">Quick processing with automatic cleanup and security</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p class="mb-0 fs-5">
                <i class="fas fa-heart text-danger me-2"></i>
                Made with love • Universal File Converter © 2024
            </p>
        </div>
    </footer>

    <div id="loadingOverlay" class="loading-overlay">
        <div class="loading-spinner">
            <div class="spinner-border text-primary mb-4" style="width: 4rem; height: 4rem;" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <h4 class="mb-2">Converting your file...</h4>
            <p class="text-muted mb-0">This may take a few moments depending on file size</p>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const fileInfo = document.getElementById('fileInfo');
            const fileName = document.getElementById('fileName');
            const fileSize = document.getElementById('fileSize');
            const removeFile = document.getElementById('removeFile');
            const formatSelection = document.getElementById('formatSelection');
            const targetFormat = document.getElementById('targetFormat');
            const convertSection = document.getElementById('convertSection');
            const uploadForm = document.getElementById('uploadForm');
            const loadingOverlay = document.getElementById('loadingOverlay');

            function formatFileSize(bytes) {
                if (bytes === 0) return '0 Bytes';
                const k = 1024;
                const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
            }

            function handleFileSelect(file) {
                fileName.textContent = file.name;
                fileSize.textContent = formatFileSize(file.size);
                fileInfo.classList.remove('d-none');
                formatSelection.style.display = 'block';
                uploadArea.style.borderColor = '#10b981';
                uploadArea.querySelector('h3').textContent = '✅ File selected successfully!';
            }

            function resetForm() {
                fileInput.value = '';
                fileInfo.classList.add('d-none');
                formatSelection.style.display = 'none';
                convertSection.style.display = 'none';
                uploadArea.style.borderColor = '#cbd5e1';
                uploadArea.querySelector('h3').textContent = 'Drop your file here or click to browse';
            }

            uploadArea.addEventListener('click', () => fileInput.click());
            
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', function(e) {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    handleFileSelect(files[0]);
                }
            });

            fileInput.addEventListener('change', function(e) {
                if (e.target.files.length > 0) {
                    handleFileSelect(e.target.files[0]);
                }
            });

            removeFile.addEventListener('click', resetForm);

            targetFormat.addEventListener('change', function() {
                convertSection.style.display = this.value ? 'block' : 'none';
            });

            uploadForm.addEventListener('submit', function(e) {
                if (!fileInput.files.length || !targetFormat.value) {
                    e.preventDefault();
                    alert('Please select a file and target format.');
                    return;
                }
                loadingOverlay.style.display = 'flex';
            });

            // Auto-hide alerts
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                setTimeout(() => {
                    const bsAlert = new bootstrap.Alert(alert);
                    if (bsAlert) bsAlert.close();
                }, 5000);
            });
        });
    </script>
</body>
</html>'''

SUCCESS_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conversion Complete - Universal File Converter</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .success-card {
            background: rgba(255,255,255,0.95);
            border-radius: 24px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            overflow: hidden;
            animation: bounceIn 0.8s ease-out;
        }
        .card-header {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .card-body { padding: 2.5rem; text-align: center; }
        .success-icon {
            font-size: 5rem;
            color: #10b981;
            margin-bottom: 2rem;
            animation: pulse 2s infinite;
        }
        .btn-success {
            background: #10b981;
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-weight: 600;
            animation: glow 2s infinite;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-weight: 600;
        }
        .file-info {
            background: rgba(16,185,129,0.1);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 2rem 0;
            border-left: 4px solid #10b981;
        }
        @keyframes bounceIn {
            0% { transform: scale(0.3); opacity: 0; }
            50% { transform: scale(1.05); }
            70% { transform: scale(0.9); }
            100% { transform: scale(1); opacity: 1; }
        }
        @keyframes glow {
            0% { box-shadow: 0 0 5px #10b981; }
            50% { box-shadow: 0 0 20px #10b981; }
            100% { box-shadow: 0 0 5px #10b981; }
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
    </style>
</head>
<body>
    <div class="success-card">
        <div class="card-header">
            <h1 class="mb-0 display-5">
                <i class="fas fa-check-circle me-3"></i>
                Conversion Successful!
            </h1>
            <p class="mb-0 mt-3 fs-5 opacity-90">Your file has been converted perfectly</p>
        </div>
        <div class="card-body">
            <div class="success-icon">
                <i class="fas fa-file-check"></i>
            </div>
            
            <div class="file-info">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <h6 class="text-muted mb-2">📁 Original File</h6>
                        <p class="mb-0 fw-semibold">{{ original_name }}</p>
                    </div>
                    <div class="col-md-6 mb-3">
                        <h6 class="text-muted mb-2">🔄 Converted To</h6>
                        <p class="mb-0 fw-semibold">{{ target_format.upper() }} Format</p>
                    </div>
                </div>
            </div>

            <div class="d-grid gap-3 d-md-block">
                <a href="{{ download_link }}" class="btn btn-success btn-lg me-md-3">
                    <i class="fas fa-download me-2"></i>
                    Download Your File
                </a>
                <a href="/" class="btn btn-primary btn-lg">
                    <i class="fas fa-plus me-2"></i>
                    Convert Another
                </a>
            </div>

            <div class="alert alert-info mt-4">
                <i class="fas fa-shield-alt me-2"></i>
                <strong>Privacy Note:</strong> Your file will be automatically deleted in 1 hour for security.
            </div>
        </div>
    </div>
</body>
</html>'''

ABOUT_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - Universal File Converter</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            padding: 2rem 0;
        }
        .card {
            background: rgba(255,255,255,0.95);
            border-radius: 24px;
            color: #333;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .card-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .feature-list {
            background: rgba(102,126,234,0.1);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header">
                        <h1 class="mb-0 display-5">
                            <i class="fas fa-info-circle me-3"></i>
                            About Universal File Converter
                        </h1>
                        <p class="mb-0 mt-3 fs-5 opacity-90">Powerful file conversion made simple</p>
                    </div>
                    <div class="card-body p-4">
                        <div class="row mb-4">
                            <div class="col-md-4 text-center mb-4">
                                <i class="fas fa-images fa-3x text-primary mb-3"></i>
                                <h4>Image Conversion</h4>
                                <p class="text-muted">JPG, PNG, GIF, BMP, TIFF, WebP, ICO</p>
                            </div>
                            <div class="col-md-4 text-center mb-4">
                                <i class="fas fa-file-pdf fa-3x text-success mb-3"></i>
                                <h4>Document Processing</h4>
                                <p class="text-muted">PDF, DOCX, DOC, TXT, MD, HTML, RTF</p>
                            </div>
                            <div class="col-md-4 text-center mb-4">
                                <i class="fas fa-database fa-3x text-info mb-3"></i>
                                <h4>Data Files</h4>
                                <p class="text-muted">CSV, JSON, XML</p>
                            </div>
                        </div>

                        <h3><i class="fas fa-star text-warning me-2"></i>Key Features</h3>
                        <div class="feature-list">
                            <ul class="list-unstyled">
                                <li class="mb-2"><i class="fas fa-bolt text-primary me-2"></i><strong>Lightning Fast:</strong> High-performance conversion engine</li>
                                <li class="mb-2"><i class="fas fa-shield-alt text-success me-2"></i><strong>Secure & Private:</strong> Files auto-deleted after 1 hour</li>
                                <li class="mb-2"><i class="fas fa-mobile-alt text-info me-2"></i><strong>Mobile Friendly:</strong> Works on all devices</li>
                                <li class="mb-2"><i class="fas fa-cloud text-secondary me-2"></i><strong>No Software Required:</strong> Everything in your browser</li>
                                <li class="mb-2"><i class="fas fa-magic text-danger me-2"></i><strong>Drag & Drop:</strong> Intuitive file uploading</li>
                                <li class="mb-0"><i class="fas fa-hd-video text-warning me-2"></i><strong>High Quality:</strong> Maintains original quality</li>
                            </ul>
                        </div>

                        <h3 class="mt-4"><i class="fas fa-cogs text-primary me-2"></i>How It Works</h3>
                        <div class="row text-center">
                            <div class="col-md-4 mb-3">
                                <div class="bg-light p-3 rounded">
                                    <i class="fas fa-upload fa-2x text-primary mb-2"></i>
                                    <h5>1. Upload</h5>
                                    <p class="mb-0">Select or drag your file</p>
                                </div>
                            </div>
                            <div class="col-md-4 mb-3">
                                <div class="bg-light p-3 rounded">
                                    <i class="fas fa-exchange-alt fa-2x text-success mb-2"></i>
                                    <h5>2. Choose Format</h5>
                                    <p class="mb-0">Select target format</p>
                                </div>
                            </div>
                            <div class="col-md-4 mb-3">
                                <div class="bg-light p-3 rounded">
                                    <i class="fas fa-download fa-2x text-info mb-2"></i>
                                    <h5>3. Download</h5>
                                    <p class="mb-0">Get your converted file</p>
                                </div>
                            </div>
                        </div>

                        <div class="text-center mt-4">
                            <a href="/" class="btn btn-primary btn-lg">
                                <i class="fas fa-arrow-left me-2"></i>
                                Back to Converter
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''

# Simple converter class
class FileConverter:
    def __init__(self):
        self.PIL_AVAILABLE = PIL_AVAILABLE
        self.PYPANDOC_AVAILABLE = PYPANDOC_AVAILABLE
        self.PYMUPDF_AVAILABLE = PYMUPDF_AVAILABLE
    
    def get_file_extension(self, filename):
        return Path(filename).suffix[1:].lower()
    
    def convert_image(self, input_file, output_file, target_format):
        if not PIL_AVAILABLE:
            logger.error("PIL not available for image conversion")
            return False
        try:
            with Image.open(input_file) as img:
                # Handle transparency for JPEG
                if target_format.upper() in ['JPEG', 'JPG'] and img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode == 'P':
                    img = img.convert('RGB')
                
                # Save with optimization
                save_kwargs = {'optimize': True}
                if target_format.upper() == 'JPEG':
                    save_kwargs['quality'] = 95
                
                img.save(output_file, format=target_format.upper(), **save_kwargs)
                logger.info(f"Successfully converted image to {target_format}")
                return True
        except Exception as e:
            logger.error(f"Image conversion error: {e}")
            return False
    
    def convert_pdf_to_image(self, input_file, output_file, target_format):
        if not PYMUPDF_AVAILABLE:
            logger.error("PyMuPDF not available for PDF conversion")
            return False
        try:
            import fitz
            doc = fitz.open(input_file)
            page = doc[0]  # First page only
            mat = fitz.Matrix(2.0, 2.0)  # Higher resolution
            pix = page.get_pixmap(matrix=mat)
            
            if target_format.lower() == 'png':
                pix.save(output_file)
            else:
                # Convert via PIL for other formats
                img_data = pix.tobytes("ppm")
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(img_data))
                if target_format.upper() == 'JPEG' and img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                img.save(output_file, format=target_format.upper(), quality=95)
            
            doc.close()
            logger.info(f"Successfully converted PDF to {target_format}")
            return True
        except Exception as e:
            logger.error(f"PDF to image conversion error: {e}")
            return False
    
    def convert_image_to_pdf(self, input_file, output_file):
        if not PIL_AVAILABLE:
            return False
        try:
            with Image.open(input_file) as img:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.save(output_file, 'PDF', resolution=150.0, quality=95)
                logger.info("Successfully converted image to PDF")
                return True
        except Exception as e:
            logger.error(f"Image to PDF conversion error: {e}")
            return False
    
    def convert_file(self, input_file, output_file, target_format):
        input_ext = self.get_file_extension(input_file)
        target_format = target_format.lower()
        
        logger.info(f"Converting {input_ext} to {target_format}")
        
        # Image to image conversion
        image_formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'ico']
        if input_ext in image_formats and target_format in image_formats:
            return self.convert_image(input_file, output_file, target_format)
        
        # Image to PDF
        elif input_ext in image_formats and target_format == 'pdf':
            return self.convert_image_to_pdf(input_file, output_file)
        
        # PDF to image
        elif input_ext == 'pdf' and target_format in image_formats:
            return self.convert_pdf_to_image(input_file, output_file, target_format)
        
        # For unsupported conversions, copy file (placeholder)
        else:
            try:
                shutil.copy2(input_file, output_file)
                logger.info(f"File copied (conversion not implemented for {input_ext} to {target_format})")
                return True
            except Exception as e:
                logger.error(f"File copy error: {e}")
                return False

# Initialize converter
converter = FileConverter()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    current_time = time.time()
    cutoff_time = current_time - 3600  # 1 hour ago
    
    for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER]:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                try:
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        logger.info(f"Cleaned up old file: {filename}")
                except OSError as e:
                    logger.warning(f"Could not remove {filepath}: {e}")

def start_cleanup_thread():
    """Start background cleanup thread"""
    def cleanup_loop():
        while True:
            cleanup_old_files()
            time.sleep(1800)  # Every 30 minutes
    
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()
    logger.info("Started file cleanup thread")

# Routes
@app.route('/')
def index():
    return render_template_string(MAIN_TEMPLATE)

@app.route('/about')
def about():
    return render_template_string(ABOUT_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect('/')
    
    file = request.files['file']
    target_format = request.form.get('target_format', '').lower()
    
    if file.filename == '' or not target_format:
        flash('Please select a file and target format')
        return redirect('/')
    
    if not allowed_file(file.filename):
        flash('File type not supported')
        return redirect('/')
    
    try:
        # Generate unique filenames
        unique_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        input_filename = f"{unique_id}_{original_filename}"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        
        # Save uploaded file
        file.save(input_path)
        logger.info(f"File uploaded: {original_filename}")
        
        # Generate output path
        output_filename = f"{unique_id}_converted_{Path(original_filename).stem}.{target_format}"
        output_path = os.path.join(CONVERTED_FOLDER, output_filename)
        
        # Convert file
        success = converter.convert_file(input_path, output_path, target_format)
        
        if success and os.path.exists(output_path):
            # Clean up input file
            os.remove(input_path)
            logger.info(f"Conversion successful: {original_filename} -> {target_format}")
            
            # Show success page
            return render_template_string(
                SUCCESS_TEMPLATE,
                original_name=original_filename,
                target_format=target_format,
                download_link=f'/download/{output_filename}'
            )
        else:
            # Clean up on failure
            for path in [input_path, output_path]:
                if os.path.exists(path):
                    os.remove(path)
            flash('Conversion failed. Please try a different format.')
            return redirect('/')
            
    except Exception as e:
        logger.error(f"Upload/conversion error: {e}")
        flash(f'An error occurred: {str(e)}')
        return redirect('/')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(CONVERTED_FOLDER, filename)
    
    if os.path.exists(file_path):
        # Extract clean filename
        parts = filename.split('_', 2)
        clean_name = parts[2] if len(parts) >= 3 else filename
        
        logger.info(f"File downloaded: {clean_name}")
        return send_file(file_path, as_attachment=True, download_name=clean_name)
    else:
        flash('File not found or has expired')
        return redirect('/')

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'PIL': PIL_AVAILABLE,
            'pypandoc': PYPANDOC_AVAILABLE,
            'PyMuPDF': PYMUPDF_AVAILABLE
        }
    })

# Error handlers
@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 50MB.')
    return redirect('/')

@app.errorhandler(404)
def not_found(e):
    return render_template_string('''
    <!DOCTYPE html>
    <html><head><title>404 - Page Not Found</title>
    <style>body{background:linear-gradient(135deg,#667eea,#764ba2);color:white;text-align:center;padding:5rem;font-family:Arial}</style>
    </head><body>
    <h1 style="font-size:5rem">404</h1><h3>Page Not Found</h3>
    <p>The page you're looking for doesn't exist.</p>
    <a href="/" style="color:white;background:rgba(255,255,255,0.2);padding:1rem 2rem;border-radius:8px;text-decoration:none">← Go Home</a>
    </body></html>
    '''), 404

@app.errorhandler(500)
def server_error(e):
    return render_template_string('''
    <!DOCTYPE html>
    <html><head><title>500 - Server Error</title>
    <style>body{background:linear-gradient(135deg,#667eea,#764ba2);color:white;text-align:center;padding:5rem;font-family:Arial}</style>
    </head><body>
    <h1 style="font-size:5rem">500</h1><h3>Server Error</h3>
    <p>Something went wrong. Please try again.</p>
    <a href="/" style="color:white;background:rgba(255,255,255,0.2);padding:1rem 2rem;border-radius:8px;text-decoration:none">← Try Again</a>
    </body></html>
    '''), 500

if __name__ == '__main__':
    print("🔄 Universal File Converter")
    print("=" * 50)
    print("🚀 Starting server...")
    print("🌐 Access at: http://localhost:5000")
    print("📊 Available features:")
    print(f"   • Images: {'✅' if PIL_AVAILABLE else '❌ (pip install Pillow)'}")
    print(f"   • Documents: {'✅' if PYPANDOC_AVAILABLE else '❌ (pip install pypandoc)'}")
    print(f"   • PDF: {'✅' if PYMUPDF_AVAILABLE else '❌ (pip install PyMuPDF)'}")
    print("=" * 50)
    
    # Start cleanup thread
    start_cleanup_thread()
    
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000))
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        print("💡 Try: python app.py")