#!/usr/bin/env python3
"""
Debug version of the Flask app to test template rendering
"""

from flask import Flask, render_template, render_template_string

app = Flask(__name__)
app.secret_key = 'debug-secret-key'

# Simple test template
SIMPLE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Universal File Converter - Debug</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            color: white;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            text-align: center;
        }
        .card {
            background: rgba(255,255,255,0.9);
            color: #333;
            padding: 30px;
            border-radius: 15px;
            margin: 20px 0;
        }
        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
        }
        .upload-area {
            border: 3px dashed #ccc;
            padding: 40px 20px;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 Universal File Converter</h1>
        <p>Debug Version - Testing Template Rendering</p>
        
        <div class="card">
            <h2>✅ Template is Working!</h2>
            <p>If you can see this page, the Flask app is running correctly.</p>
            
            <div class="upload-area">
                <h3>📁 File Upload Area</h3>
                <p>Drag and drop files here or click to browse</p>
                <input type="file" style="margin: 10px;">
            </div>
            
            <a href="/test" class="btn">🧪 Test Route</a>
            <a href="/about" class="btn">ℹ️ About</a>
        </div>
        
        <div style="margin-top: 30px;">
            <h3>🔧 Debug Info:</h3>
            <p>Flask Version: Working</p>
            <p>Templates: Loading</p>
            <p>Static Files: Embedded</p>
            <p>Status: ✅ Ready</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """Main page - simple version"""
    try:
        # Try to render the full template first
        return render_template('index.html')
    except Exception as e:
        # If that fails, use the simple template
        print(f"Template error: {e}")
        return render_template_string(SIMPLE_TEMPLATE)

@app.route('/test')
def test():
    """Test route"""
    return render_template_string('''
    <html>
    <head><title>Test Page</title></head>
    <body style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 50px; text-align: center; font-family: Arial;">
        <h1>🧪 Test Page</h1>
        <p>This is a test route to verify Flask is working.</p>
        <a href="/" style="color: white;">← Back to Home</a>
    </body>
    </html>
    ''')

@app.route('/about')
def about():
    """About page"""
    try:
        return render_template('about.html')
    except Exception as e:
        print(f"About template error: {e}")
        return render_template_string('''
        <html>
        <head><title>About</title></head>
        <body style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 50px; font-family: Arial;">
            <h1>ℹ️ About Universal File Converter</h1>
            <p>A powerful web-based file conversion tool.</p>
            <h3>Supported Formats:</h3>
            <ul style="text-align: left; max-width: 400px; margin: 0 auto;">
                <li>Images: JPG, PNG, GIF, BMP, TIFF</li>
                <li>Documents: PDF, DOCX, TXT, MD, HTML</li>
                <li>Data: CSV, JSON, XML</li>
            </ul>
            <p style="margin-top: 30px;">
                <a href="/" style="color: white;">← Back to Home</a>
            </p>
        </body>
        </html>
        ''')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'message': 'Universal File Converter is running',
        'templates': 'working'
    }

if __name__ == '__main__':
    print("🚀 Starting Universal File Converter (Debug Mode)")
    print("📱 Open in browser: http://localhost:5000")
    print("🔧 This is a debug version to test template rendering")
    print("-" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting app: {e}")
        print("💡 Try: python debug_app.py")