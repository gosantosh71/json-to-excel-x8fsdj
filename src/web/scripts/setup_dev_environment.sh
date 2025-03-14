#!/bin/bash
# setup_dev_environment.sh
# Script to set up the development environment for the JSON to Excel Conversion Tool web interface

# Global variables
VENV_DIR="venv"
WEB_DIR="../.."
BACKEND_DIR="../../../backend"
FLASK_APP="run.py"
FLASK_ENV="development"
SECRET_KEY="dev_secret_key_for_development_only"

# Function to check Python version
check_python() {
    echo "Checking Python version..."
    if command -v python3 &>/dev/null; then
        python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        python_major=$(echo "$python_version" | cut -d'.' -f1)
        python_minor=$(echo "$python_version" | cut -d'.' -f2)
        
        if [ "$python_major" -eq 3 ] && [ "$python_minor" -ge 9 ]; then
            echo "✓ Python $python_version detected (3.9+ required)"
            return 0
        else
            echo "✗ Python $python_version detected but 3.9+ is required"
            exit 1
        fi
    else
        echo "✗ Python 3 not found. Please install Python 3.9 or higher"
        exit 1
    fi
}

# Function to create virtual environment
create_virtual_environment() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment in $VENV_DIR..."
        python3 -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            echo "✗ Failed to create virtual environment"
            exit 1
        fi
        echo "✓ Virtual environment created"
    else
        echo "✓ Virtual environment already exists"
    fi
}

# Function to activate virtual environment
activate_virtual_environment() {
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "✗ Failed to activate virtual environment"
        exit 1
    fi
    echo "✓ Virtual environment activated"
}

# Function to install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    
    echo "Upgrading pip..."
    pip install --upgrade pip

    echo "Installing backend dependencies..."
    if ! pip install -r "$BACKEND_DIR/requirements.txt"; then
        echo "⚠ Warning: Some backend dependencies may not have installed correctly"
    fi
    
    echo "Installing web interface dependencies..."
    if ! pip install -r "$WEB_DIR/requirements.txt"; then
        echo "⚠ Warning: Some web interface dependencies may not have installed correctly"
    fi
    
    echo "Installing development tools..."
    pip install pytest black flake8
    
    # Verify installation of key packages
    echo "Verifying installation..."
    if python -c "import flask, pandas, openpyxl; print('Flask version:', flask.__version__, ', Pandas version:', pandas.__version__, ', openpyxl version:', openpyxl.__version__)" &>/dev/null; then
        echo "✓ Dependencies installed successfully"
    else
        echo "⚠ Some dependencies may not have installed correctly"
    fi
}

# Function to set up environment variables
setup_environment_variables() {
    echo "Setting up environment variables..."
    ENV_FILE="$WEB_DIR/.env"
    
    # Create .env file with settings from .env.example but with development values
    cat > "$ENV_FILE" << EOF
FLASK_APP=$FLASK_APP
FLASK_ENV=$FLASK_ENV

# Security Settings
SECRET_KEY=$SECRET_KEY
WTF_CSRF_ENABLED=True
SESSION_TIMEOUT=30

# File Upload Settings
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=5242880
ALLOWED_EXTENSIONS=.json

# Application Settings
DEBUG=True
TESTING=False
LOG_LEVEL=INFO

# Backend API Configuration
BACKEND_API_URL=http://localhost:8000/api

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Job Management
MAX_CONCURRENT_JOBS=10
JOB_TIMEOUT_SECONDS=900
COMPLETED_JOB_TTL_MINUTES=60

# Logging Configuration
LOG_FILE_PATH=./logs/web_interface.log
LOG_FILE_MAX_SIZE_MB=10
LOG_FILE_BACKUP_COUNT=3
EOF
    
    echo "✓ Environment variables set up in $ENV_FILE"
}

# Function to create necessary directories
create_directories() {
    echo "Creating necessary directories..."
    
    # Create uploads directory
    if mkdir -p "$WEB_DIR/uploads"; then
        echo "✓ Created uploads directory"
    else
        echo "⚠ Warning: Failed to create uploads directory"
    fi
    
    # Create temp directory
    if mkdir -p "$WEB_DIR/temp"; then
        echo "✓ Created temp directory"
    else
        echo "⚠ Warning: Failed to create temp directory"
    fi
    
    # Create logs directory
    if mkdir -p "$WEB_DIR/logs"; then
        echo "✓ Created logs directory"
    else
        echo "⚠ Warning: Failed to create logs directory"
    fi
}

# Main function
main() {
    echo "====================================================="
    echo "  JSON to Excel Conversion Tool - Dev Environment Setup"
    echo "====================================================="
    echo "This script will set up the development environment for the JSON to Excel Conversion Tool web interface."
    echo
    
    check_python
    create_virtual_environment
    activate_virtual_environment
    install_dependencies
    setup_environment_variables
    create_directories
    
    echo
    echo "====================================================="
    echo "✓ Development environment setup complete!"
    echo
    echo "To start the development server:"
    echo "1. Make sure you're in the web directory: cd $WEB_DIR"
    echo "2. Activate the virtual environment: source $VENV_DIR/bin/activate"
    echo "3. Run the Flask development server: flask run"
    echo "====================================================="
}

# Call main function
main