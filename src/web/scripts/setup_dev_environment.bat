@echo off
setlocal enabledelayedexpansion

rem ============================================================================
rem JSON to Excel Conversion Tool - Development Environment Setup
rem
rem This script sets up the development environment for the JSON to Excel
rem Conversion Tool web interface. It creates a Python virtual environment,
rem installs required dependencies, sets up environment variables, and prepares
rem the application for development use on Windows systems.
rem ============================================================================

echo ========================================================
echo JSON to Excel Conversion Tool - Development Setup
echo ========================================================
echo.

rem Define global variables
set "VENV_DIR=venv"
set "WEB_DIR=..\\.."
set "BACKEND_DIR=..\\..\\..\\backend"
set "FLASK_APP=run.py"
set "FLASK_ENV=development"
set "SECRET_KEY=dev_secret_key_for_development_only"

rem Call the main function
call :main
goto :eof

:check_python
    echo Checking Python version...
    
    python --version > nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Error: Python is not installed or not in PATH.
        echo Please install Python 3.9 or higher and try again.
        exit /b 1
    )
    
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do (
        set "PYTHON_VERSION=%%V"
    )
    
    for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
        set "PYTHON_MAJOR=%%a"
        set "PYTHON_MINOR=%%b"
    )
    
    if !PYTHON_MAJOR! LSS 3 (
        echo Error: Python 3.9 or higher is required.
        echo Current version: !PYTHON_VERSION!
        exit /b 1
    )
    
    if !PYTHON_MAJOR! EQU 3 (
        if !PYTHON_MINOR! LSS 9 (
            echo Error: Python 3.9 or higher is required.
            echo Current version: !PYTHON_VERSION!
            exit /b 1
        )
    )
    
    echo Python !PYTHON_VERSION! detected.
    exit /b 0

:create_virtual_environment
    if exist "%VENV_DIR%" (
        echo Virtual environment already exists at %VENV_DIR%.
    ) else (
        echo Creating virtual environment at %VENV_DIR%...
        python -m venv %VENV_DIR%
        
        if not exist "%VENV_DIR%\Scripts\activate.bat" (
            echo Error: Failed to create virtual environment.
            echo Please check that you have the 'venv' module installed.
            echo Try running: python -m pip install --user virtualenv
            exit /b 1
        )
        
        echo Virtual environment created successfully.
    )
    exit /b 0

:activate_virtual_environment
    echo Activating virtual environment...
    call %VENV_DIR%\Scripts\activate.bat
    
    if not defined VIRTUAL_ENV (
        echo Error: Failed to activate virtual environment.
        echo Please check that %VENV_DIR%\Scripts\activate.bat exists.
        exit /b 1
    )
    
    echo Virtual environment activated successfully.
    exit /b 0

:install_dependencies
    echo Installing dependencies...
    
    echo Upgrading pip...
    python -m pip install --upgrade pip
    if %ERRORLEVEL% neq 0 (
        echo Warning: Failed to upgrade pip. Continuing with installation...
    )
    
    echo Installing backend dependencies from %BACKEND_DIR%\requirements.txt...
    if not exist "%BACKEND_DIR%\requirements.txt" (
        echo Error: Backend requirements.txt not found at %BACKEND_DIR%\requirements.txt
        echo Current directory: %CD%
        exit /b 1
    )
    
    python -m pip install -r "%BACKEND_DIR%\requirements.txt"
    if %ERRORLEVEL% neq 0 (
        echo Warning: Some backend dependencies may not have installed correctly.
    )
    
    echo Installing web interface dependencies from %WEB_DIR%\requirements.txt...
    if not exist "%WEB_DIR%\requirements.txt" (
        echo Error: Web requirements.txt not found at %WEB_DIR%\requirements.txt
        echo Current directory: %CD%
        exit /b 1
    )
    
    python -m pip install -r "%WEB_DIR%\requirements.txt"
    if %ERRORLEVEL% neq 0 (
        echo Warning: Some web dependencies may not have installed correctly.
    )
    
    echo Installing development tools...
    python -m pip install pytest black flake8
    if %ERRORLEVEL% neq 0 (
        echo Warning: Development tools may not have installed correctly.
    )
    
    echo Verifying key dependencies...
    python -c "import flask; import pandas; import openpyxl; print('Dependency verification successful.')" || (
        echo Warning: Some key dependencies may not have installed correctly.
        echo Please check the error messages above and try to install missing packages manually.
    )
    
    exit /b 0

:setup_environment_variables
    echo Setting up environment variables...
    
    set "ENV_FILE=%WEB_DIR%\.env"
    
    echo Creating .env file at %ENV_FILE%...
    (
        echo # Flask Configuration
        echo FLASK_APP=%FLASK_APP%
        echo FLASK_ENV=%FLASK_ENV%
        echo.
        echo # Security Settings
        echo SECRET_KEY=%SECRET_KEY%
        echo WTF_CSRF_ENABLED=True
        echo SESSION_TIMEOUT=30
        echo.
        echo # File Upload Settings
        echo UPLOAD_FOLDER=uploads
        echo MAX_CONTENT_LENGTH=5242880
        echo ALLOWED_EXTENSIONS=.json
        echo.
        echo # Application Settings
        echo DEBUG=True
        echo TESTING=False
        echo LOG_LEVEL=DEBUG
        echo.
        echo # Logging Configuration
        echo LOG_FILE_PATH=./logs/web_interface.log
        echo LOG_FILE_MAX_SIZE_MB=10
        echo LOG_FILE_BACKUP_COUNT=3
    ) > "%ENV_FILE%"
    
    if not exist "%ENV_FILE%" (
        echo Warning: Failed to create .env file. Please create it manually.
        exit /b 1
    )
    
    echo Environment variables set up successfully.
    exit /b 0

:create_directories
    echo Creating necessary directories...
    
    set "UPLOADS_DIR=%WEB_DIR%\uploads"
    set "TEMP_DIR=%WEB_DIR%\temp"
    set "LOGS_DIR=%WEB_DIR%\logs"
    
    if not exist "%UPLOADS_DIR%" (
        mkdir "%UPLOADS_DIR%" 2>nul
        if %ERRORLEVEL% neq 0 (
            echo Warning: Failed to create uploads directory at %UPLOADS_DIR%.
            echo Please create it manually.
        ) else (
            echo Created uploads directory at %UPLOADS_DIR%.
        )
    ) else (
        echo Uploads directory already exists at %UPLOADS_DIR%.
    )
    
    if not exist "%TEMP_DIR%" (
        mkdir "%TEMP_DIR%" 2>nul
        if %ERRORLEVEL% neq 0 (
            echo Warning: Failed to create temp directory at %TEMP_DIR%.
            echo Please create it manually.
        ) else (
            echo Created temp directory at %TEMP_DIR%.
        )
    ) else (
        echo Temp directory already exists at %TEMP_DIR%.
    )
    
    if not exist "%LOGS_DIR%" (
        mkdir "%LOGS_DIR%" 2>nul
        if %ERRORLEVEL% neq 0 (
            echo Warning: Failed to create logs directory at %LOGS_DIR%.
            echo Please create it manually.
        ) else (
            echo Created logs directory at %LOGS_DIR%.
        )
    ) else (
        echo Logs directory already exists at %LOGS_DIR%.
    )
    
    exit /b 0

:main
    echo Starting development environment setup...
    echo Current directory: %CD%
    
    call :check_python
    if %ERRORLEVEL% neq 0 exit /b 1
    
    call :create_virtual_environment
    if %ERRORLEVEL% neq 0 exit /b 1
    
    call :activate_virtual_environment
    if %ERRORLEVEL% neq 0 exit /b 1
    
    call :install_dependencies
    if %ERRORLEVEL% neq 0 (
        echo Warning: There were issues with dependency installation.
        echo The setup will continue, but some features may not work correctly.
    )
    
    call :setup_environment_variables
    if %ERRORLEVEL% neq 0 (
        echo Warning: There were issues with environment variable setup.
        echo The setup will continue, but the application may not work correctly.
    )
    
    call :create_directories
    
    echo.
    echo ========================================================
    echo Setup completed successfully!
    echo.
    echo To start the development server:
    echo 1. Activate the virtual environment: %VENV_DIR%\Scripts\activate
    echo 2. Navigate to the web directory: cd %WEB_DIR%
    echo 3. Run the Flask application: flask run
    echo.
    echo The web interface will be available at: http://localhost:5000
    echo ========================================================
    echo.
    
    pause
    exit /b 0