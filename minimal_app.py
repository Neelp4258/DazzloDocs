#!/usr/bin/env python3
from flask import Flask, render_template_string

app = Flask(__name__)
app.secret_key = 'test-secret'

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Universal File Converter</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
        }
        .card-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 20px 20px 0 0;
        }
        .upload-area {
            border: 3px dashed #ddd;
            border-radius: 15px;
            padding: 40px 20px;
            text-align: center;
            background: rgba(255,255,255,0.5);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .upload-area:hover {
            border-color: #667eea;
            background: rgba(102,126,234,0.1);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header text-center py-4">
                        <h1 class="mb-0">
                            <i class="fas fa-exchange-alt me-2"></i>
                            Universal File Converter
                        </h1>
                        <p class="mb-0 mt-2 opacity-90">Convert your files between different formats</p>
                    </div>
                    <div class="card-body p-4">
                        <form method="POST" action="/upload" enctype="multipart/form-data">
                            <div class="upload-area mb-4" onclick="document.getElementById('fileInput').click()">
                                <i class="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
                                <h4>Click here to select a file</h4>
                                <p class="text-muted">Or drag and drop your file</p>
                                <input type="file" id="fileInput" name="file" style="display: none;" 
                                       accept=".jpg,.jpeg,.png,.pdf,.docx,.txt,.md">
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Convert to:</label>
                                <select class="form-select" name="target_format" required>
                                    <option value="">Select format...</option>
                                    <option value="pdf">PDF</option>
                                    <option value="jpg">JPG</option>
                                    <option value="png">PNG</option>
                                    <option value="txt">TXT</option>
                                    <option value="docx">DOCX</option>
                                </select>
                            </div>
                            
                            <div class="text-center">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-magic me-2"></i>
                                    Convert File
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <!-- Features -->
                <div class="row mt-5">
                    <div class="col-md-4 text-center text-white mb-3">
                        <i class="fas fa-images fa-3x mb-3"></i>
                        <h5>Image Conversion</h5>
                        <p class="opacity-75">JPG, PNG, GIF, BMP</p>
                    </div>
                    <div class="col-md-4 text-center text-white mb-3">
                        <i class="fas fa-file-pdf fa-3x mb-3"></i>
                        <h5>Document Processing</h5>
                        <p class="opacity-75">PDF, DOCX, TXT, MD</p>
                    </div>
                    <div class="col-md-4 text-center text-white mb-3">
                        <i class="fas fa-bolt fa-3x mb-3"></i>
                        <h5>Fast & Secure</h5>
                        <p class="opacity-75">Quick & Safe Processing</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // File input handler
        document.getElementById('fileInput').addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                const fileName = e.target.files[0].name;
                document.querySelector('.upload-area h4').textContent = 'File selected: ' + fileName;
            }
        });
        
        // Drag and drop
        const uploadArea = document.querySelector('.upload-area');
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#667eea';
        });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            document.getElementById('fileInput').files = e.dataTransfer.files;
            if (e.dataTransfer.files.length > 0) {
                document.querySelector('.upload-area h4').textContent = 'File selected: ' + e.dataTransfer.files[0].name;
            }
        });
    </script>
</body>
</html>
    ''')

@app.route('/upload', methods=['POST'])
def upload():
    return render_template_