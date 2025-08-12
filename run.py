#!/usr/bin/env python3
"""
DazzloDocs Converter - Quick Start Script
This script sets up and runs the application with proper configuration.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_requirements():
    """Install Python requirements."""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        print("💡 Try: pip install -r requirements.txt")
        sys.exit(1)

def check_system_dependencies():
    """Check and suggest system dependencies."""
    print("\n🔍 Checking system dependencies...")
    
    # Check for LibreOffice
    try:
        result = subprocess.run(['libreoffice', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ LibreOffice detected")
        else:
            print("⚠️  LibreOffice not found")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  LibreOffice not found")
        print_libreoffice_instructions()
    
    # Check for Pandoc
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Pandoc detected")
        else:
            print("⚠️  Pandoc not found")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Pandoc not found")
        print_pandoc_instructions()

def print_libreoffice_instructions():
    """Print LibreOffice installation instructions."""
    system = platform.system().lower()
    if system == "linux":
        print("💡 Install LibreOffice: sudo apt-get install libreoffice")
    elif system == "darwin":  # macOS
        print("💡 Install LibreOffice: brew install --cask libreoffice")
    elif system == "windows":
        print("💡 Download LibreOffice from: https://www.libreoffice.org/download/")

def print_pandoc_instructions():
    """Print Pandoc installation instructions."""
    system = platform.system().lower()
    if system == "linux":
        print("💡 Install Pandoc: sudo apt-get install pandoc")
    elif system == "darwin":  # macOS
        print("💡 Install Pandoc: brew install pandoc")
    elif system == "windows":
        print("💡 Download Pandoc from: https://pandoc.org/installing.html")

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    directories = ['uploads', 'converted', 'Templates']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")

def check_template_files():
    """Check if template files exist."""
    print("\n📄 Checking template files...")
    required_templates = [
        'Templates/base.html',
        'Templates/index.html', 
        'Templates/success.html',
        'Templates/about.html',
        'Templates/404.html',
        'Templates/500.html'
    ]
    
    missing_templates = []
    for template in required_templates:
        if not Path(template).exists():
            missing_templates.append(template)
    
    if missing_templates:
        print(f"⚠️  Missing templates: {', '.join(missing_templates)}")
        print("💡 Make sure all template files are present")
    else:
        print("✅ All template files found")

def set_environment():
    """Set environment variables."""
    print("\n⚙️  Setting environment variables...")
    
    # Set default environment variables
    env_vars = {
        'FLASK_ENV': 'development',
        'SECRET_KEY': 'dev-secret-key-change-this-in-production',
        'MAX_CONTENT_LENGTH': '52428800',  # 50MB
        'UPLOAD_FOLDER': 'uploads',
        'CONVERTED_FOLDER': 'converted'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"✅ Set {key}={value}")
    
    print("✅ Environment variables configured")

def run_application():
    """Run the Flask application."""
    print("\n🚀 Starting DazzloDocs Converter...")
    print("📍 Application will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Import and run the app
        from app import app
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=True
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

def main():
    """Main function."""
    print("🎉 Welcome to DazzloDocs Converter!")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    install_requirements()
    
    # Check system dependencies
    check_system_dependencies()
    
    # Create directories
    create_directories()
    
    # Check template files
    check_template_files()
    
    # Set environment
    set_environment()
    
    # Run application
    run_application()

if __name__ == "__main__":
    main()