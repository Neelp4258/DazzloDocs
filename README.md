# 🎉 DazzloDocs Converter

A modern, professional file conversion service built with Flask. Convert files between various formats with ease, security, and speed.

![DazzloDocs Converter](https://img.shields.io/badge/Flask-2.3.3-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **🖼️ Image Conversion**: JPG, PNG, GIF, BMP, TIFF, WebP, ICO
- **📄 Document Processing**: PDF, DOCX, DOC, TXT, MD, HTML, RTF
- **📊 Data Files**: CSV, JSON, XML
- **🚀 Lightning Fast**: Optimized processing engine
- **🔒 Secure & Private**: Automatic file cleanup after 1 hour
- **📱 Mobile Friendly**: Responsive design for all devices
- **🎨 Modern UI**: Beautiful, professional interface
- **⚡ Real-time Progress**: Live conversion status updates

## 🏗️ Architecture

```
DazzloDocs Converter/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── utils/                # Utility modules
│   ├── __init__.py
│   ├── converter.py      # File conversion logic
│   ├── file_handler.py   # File operations
│   ├── validators.py     # File validation
│   └── cleanup.py        # Automatic cleanup
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Main page
│   ├── success.html      # Success page
│   ├── about.html        # About page
│   ├── 404.html          # Error pages
│   ├── 500.html
│   └── 413.html
├── uploads/              # Upload directory
├── converted/            # Converted files
├── requirements.txt      # Python dependencies
├── run.py               # Quick start script
├── Dockerfile           # Container configuration
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DazzloDocs-Converter
   ```

2. **Run the quick start script**
   ```bash
   python run.py
   ```

   This script will:
   - Check Python version
   - Install dependencies
   - Create necessary directories
   - Start the application

3. **Access the application**
   - Open your browser and go to: `http://localhost:5000`
   - Start converting files!

### Manual Installation

If you prefer manual installation:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create directories**
   ```bash
   mkdir uploads converted templates
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

## 🛠️ System Dependencies

For full functionality, install these system dependencies:

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install libreoffice pandoc
```

### macOS
```bash
brew install --cask libreoffice
brew install pandoc
```

### Windows
- Download [LibreOffice](https://www.libreoffice.org/download/)
- Download [Pandoc](https://pandoc.org/installing.html)

## 📦 Docker Deployment

### Using Docker Compose

1. **Build and run**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Open: `http://localhost:5000`

### Using Docker directly

1. **Build the image**
   ```bash
   docker build -t dazzlodocs-converter .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 dazzlodocs-converter
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
MAX_CONTENT_LENGTH=52428800
UPLOAD_FOLDER=uploads
CONVERTED_FOLDER=converted
LOG_LEVEL=INFO
```

### Configuration Options

- `MAX_CONTENT_LENGTH`: Maximum file size (default: 50MB)
- `FILE_RETENTION_TIME`: How long to keep files (default: 1 hour)
- `CLEANUP_INTERVAL`: Cleanup frequency (default: 1 hour)
- `IMAGE_QUALITY`: Image conversion quality (default: 95)
- `IMAGE_MAX_DIMENSION`: Max image dimension (default: 2000px)

## 📁 Supported Formats

### Input → Output Conversions

| Input Format | Supported Output Formats |
|--------------|-------------------------|
| JPG/JPEG     | PNG, GIF, BMP, TIFF, WebP, ICO, PDF |
| PNG          | JPG, JPEG, GIF, BMP, TIFF, WebP, ICO, PDF |
| GIF          | JPG, JPEG, PNG, BMP, TIFF, WebP, ICO, PDF |
| BMP          | JPG, JPEG, PNG, GIF, TIFF, WebP, ICO, PDF |
| TIFF         | JPG, JPEG, PNG, GIF, BMP, WebP, ICO, PDF |
| WebP         | JPG, JPEG, PNG, GIF, BMP, TIFF, ICO, PDF |
| ICO          | JPG, JPEG, PNG, GIF, BMP, TIFF, WebP, PDF |
| PDF          | JPG, JPEG, PNG, GIF, BMP, TIFF, WebP, ICO, TXT |
| DOCX         | PDF, DOC, RTF, TXT, HTML |
| DOC          | PDF, DOCX, RTF, TXT, HTML |
| TXT          | PDF, DOCX, DOC, RTF, HTML |
| MD           | PDF, HTML, TXT |
| HTML         | PDF, TXT, MD |
| RTF          | PDF, DOCX, DOC, TXT, HTML |
| CSV          | PDF, TXT, JSON, XML |
| JSON         | PDF, TXT, CSV, XML |
| XML          | PDF, TXT, CSV, JSON |

## 🔒 Security Features

- **File Validation**: Strict file type checking
- **Size Limits**: Configurable file size restrictions
- **Auto Cleanup**: Files automatically deleted after 1 hour
- **Secure Filenames**: UUID-based naming prevents conflicts
- **Input Sanitization**: All inputs are properly validated
- **HTTPS Ready**: Configured for secure connections

## 🎨 UI/UX Features

- **Modern Design**: Clean, professional interface
- **Responsive Layout**: Works on all device sizes
- **Drag & Drop**: Easy file upload interface
- **Real-time Feedback**: Progress indicators and status updates
- **Error Handling**: User-friendly error messages
- **Loading States**: Smooth loading animations
- **Accessibility**: WCAG compliant design

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

### Manual Testing
1. Test file upload with different formats
2. Verify conversion quality
3. Check error handling with invalid files
4. Test mobile responsiveness
5. Verify cleanup functionality

## 📊 Performance

- **Fast Processing**: Optimized conversion algorithms
- **Memory Efficient**: Stream-based file handling
- **Concurrent Support**: Handles multiple users
- **Caching**: Intelligent result caching
- **Background Processing**: Non-blocking operations

## 🚀 Deployment

### Production Deployment

1. **Set environment variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secure-secret-key
   ```

2. **Use Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Configure reverse proxy (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Cloud Deployment

#### Heroku
```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

#### Railway
```bash
# Railway will auto-detect and deploy
railway up
```

#### Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

## 🐛 Troubleshooting

### Common Issues

1. **Conversion fails**
   - Check if LibreOffice is installed
   - Verify file format is supported
   - Check file size limits

2. **Files not opening after conversion**
   - Ensure proper file permissions
   - Check if target format is supported
   - Verify file integrity

3. **Performance issues**
   - Increase server resources
   - Check disk space
   - Monitor memory usage

### Logs

Check application logs:
```bash
tail -f app.log
```

### Debug Mode

Enable debug mode for development:
```bash
export FLASK_ENV=development
python app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask community for the excellent framework
- Pillow team for image processing capabilities
- PyMuPDF developers for PDF handling
- Bootstrap team for the UI framework

## 📞 Support

- **Email**: support@dazzlodocs.com
- **Website**: www.dazzlodocs.com
- **Issues**: GitHub Issues page

---

Made with ❤️ by the DazzloDocs Team