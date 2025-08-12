# DazzloDocs Converter - Deployment Guide

## Issues Fixed ✅

### 1. Gunicorn Command Not Found
The "gunicorn: command not found" error has been resolved by:

1. **Added gunicorn to requirements.txt**: Added `gunicorn==21.2.0` to the dependencies
2. **Updated Dockerfile**: Changed from `python app.py` to `gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app`
3. **Created gunicorn.conf.py**: Added proper production configuration
4. **Updated Procfile**: Now uses `gunicorn -c gunicorn.conf.py app:app`
5. **Updated docker-compose.yml**: Fixed Railway deployment command

### 2. Template Rendering Error (502 Error)
The template rendering error has been resolved by:

1. **Fixed Flask template folder configuration**: Updated Flask app to use `template_folder='Templates'`
2. **Updated directory creation**: Fixed Dockerfile and run.py to create the correct `Templates` directory
3. **Consistent naming**: Ensured all references use the capitalized `Templates` directory

## Deployment Options

### 1. Render.com
- Connect your GitHub repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `gunicorn -c gunicorn.conf.py app:app`
- Environment variables:
  - `PORT`: Auto-set by Render
  - `SECRET_KEY`: Your secret key
  - `FLASK_ENV`: `production`

### 2. Railway
- Connect your GitHub repository
- Railway will automatically detect the Dockerfile
- Environment variables:
  - `PORT`: Auto-set by Railway
  - `SECRET_KEY`: Your secret key

### 3. Heroku
- Connect your GitHub repository
- Heroku will use the Procfile automatically
- Environment variables:
  - `PORT`: Auto-set by Heroku
  - `SECRET_KEY`: Your secret key

### 4. Docker Deployment
```bash
# Build the image
docker build -t dazzlodocs-converter .

# Run the container
docker run -p 5000:5000 -e SECRET_KEY=your-secret-key dazzlodocs-converter
```

### 5. Docker Compose
```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f
```

## Environment Variables

Set these environment variables in your deployment platform:

```bash
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
MAX_CONTENT_LENGTH=52428800  # 50MB
UPLOAD_FOLDER=uploads
CONVERTED_FOLDER=converted
GUNICORN_WORKERS=4
```

## Health Check

Your application includes a health check endpoint at `/health` that returns "OK" for load balancers.

## Troubleshooting

1. **If gunicorn still not found**: Make sure `requirements.txt` is being installed
2. **If port issues**: Check that the `PORT` environment variable is set
3. **If file upload issues**: Ensure `uploads` and `converted` directories exist
4. **If conversion fails**: Check that system dependencies (LibreOffice, Pandoc) are installed

## Local Development

For local development, you can still use:
```bash
python run.py
# or
python app.py
```

This will run the Flask development server with debug mode enabled. 