#!/usr/bin/env python3
"""
Quick Start Script for Universal File Converter
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
    directories = ['uploads', 'converted', 'templates']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")

def check_template_files():
    """Check if template files exist."""
    print("\n📄 Checking template files...")
    required_templates = [
        'templates/base.html',
        'templates/index.html', 
        'templates/success.html',
        'templates/about.html',
        'templates/404.html',
        'templates/500.html'
    ]
    
    missing_templates = []
    for template in required_templates:
        if not Path(template).exists():
            missing_templates.append(template)
    
    if missing_templates:
        print("❌ Missing template files:")
        for template in missing_templates:
            print(f"   - {template}")
        print("\n💡 Make sure all template files are in the templates/ directory")
        return False
    
    print("✅ All template files found")
    return True

def set_environment():
    """Set environment variables."""
    print("\n🔧 Setting up environment...")
    
    # Set Flask environment variables
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    # Create .env file if it doesn't exist
    env_file = Path('.env')
    if not env_file.exists():
        env_content = """# Environment Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
MAX_CONTENT_LENGTH=52428800
UPLOAD_FOLDER=uploads
CONVERTED_FOLDER=converted
"""
        env_file.write_text(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file exists")

def run_application():
    """Run the Flask application."""
    print("\n🚀 Starting Universal File Converter...")
    print("🌐 Server will be available at: http://localhost:5000")
    print("📝 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run the app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError:
        print("❌ Could not import the Flask app")
        print("💡 Make sure app.py exists in the current directory")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main function to set up and run the application."""
    print("🔄 Universal File Converter - Quick Start")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check if we're in the right directory
    if not Path('app.py').exists():
        print("❌ app.py not found in current directory")
        print("💡 Make sure you're in the project root directory")
        sys.exit(1)
    
    # Install Python dependencies
    install_requirements()
    
    # Create directories
    create_directories()
    
    # Check template files
    if not check_template_files():
        sys.exit(1)
    
    # Set up environment
    set_environment()
    
    # Check system dependencies
    check_system_dependencies()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    
    # Ask user if they want to start the server
    try:
        start_server = input("\n🚀 Start the server now? (y/n): ").lower().strip()
        if start_server in ['y', 'yes', '']:
            run_application()
        else:
            print("\n💡 To start the server later, run: python app.py")
            print("🌐 Server will be available at: http://localhost:5000")
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")

if __name__ == '__main__':
    main()