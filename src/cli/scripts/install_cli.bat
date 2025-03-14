@echo off
setlocal enabledelayedexpansion

:: ===================================================
:: JSON to Excel Conversion Tool - CLI Installer
:: Version: 1.0.0
:: 
:: This script installs the JSON to Excel Conversion Tool
:: CLI on Windows systems by creating a virtual environment,
:: installing required dependencies, and setting up command
:: line access through the PATH environment variable.
:: ===================================================

:: Global path variables
set "SCRIPT_DIR=%~dp0"
set "CLI_ROOT=%SCRIPT_DIR%\.."
set "BACKEND_ROOT=%SCRIPT_DIR%\..\..\backend"
set "VENV_DIR=%USERPROFILE%\.json2excel"
set "BIN_DIR=%USERPROFILE%\AppData\Local\Programs\json2excel"

:: ===================================================
:: Function: print_message
:: Prints a formatted message with color
:: Parameters:
::   %1 - message type (info, success, error, warning)
::   %2 - message text
:: ===================================================
:print_message
    set "type=%~1"
    set "message=%~2"
    
    if "%type%"=="info" (
        echo [36m[INFO][0m %message%
    ) else if "%type%"=="success" (
        echo [32m[SUCCESS][0m %message%
    ) else if "%type%"=="error" (
        echo [31m[ERROR][0m %message%
    ) else if "%type%"=="warning" (
        echo [33m[WARNING][0m %message%
    ) else (
        echo %message%
    )
    exit /b 0

:: ===================================================
:: Function: check_python
:: Checks if Python 3.9+ is installed
:: Returns:
::   0 - Python requirements are met
::   1 - Python not found or version too low
:: ===================================================
:check_python
    call :print_message info "Checking Python installation..."
    
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        call :print_message error "Python is not installed or not in PATH."
        call :print_message error "Please install Python 3.9 or higher from https://www.python.org/downloads/"
        exit /b 1
    )
    
    for /f "tokens=2" %%V in ('python --version 2^>^&1') do (
        set "python_version=%%V"
    )
    
    for /f "tokens=1,2 delims=." %%a in ("!python_version!") do (
        set "major=%%a"
        set "minor=%%b"
    )
    
    if !major! lss 3 (
        call :print_message error "Python version !python_version! is not supported."
        call :print_message error "Please install Python 3.9 or higher."
        exit /b 1
    )
    
    if !major!==3 (
        if !minor! lss 9 (
            call :print_message error "Python version !python_version! is not supported."
            call :print_message error "Please install Python 3.9 or higher."
            exit /b 1
        )
    )
    
    call :print_message success "Python !python_version! detected."
    exit /b 0

:: ===================================================
:: Function: create_virtual_environment
:: Creates a Python virtual environment
:: Returns:
::   0 - Virtual environment created successfully
::   1 - Failed to create virtual environment
:: ===================================================
:create_virtual_environment
    call :print_message info "Creating virtual environment at !VENV_DIR!..."
    
    if exist "!VENV_DIR!\Scripts\python.exe" (
        call :print_message info "Virtual environment already exists."
        exit /b 0
    )
    
    if not exist "!VENV_DIR!" (
        mkdir "!VENV_DIR!"
        if %errorlevel% neq 0 (
            call :print_message error "Failed to create directory: !VENV_DIR!"
            exit /b 1
        )
    )
    
    python -m venv "!VENV_DIR!"
    if %errorlevel% neq 0 (
        call :print_message error "Failed to create virtual environment."
        exit /b 1
    )
    
    call :print_message success "Virtual environment created successfully."
    exit /b 0

:: ===================================================
:: Function: install_dependencies
:: Installs required Python dependencies
:: Returns:
::   0 - Dependencies installed successfully
::   1 - Failed to install dependencies
:: ===================================================
:install_dependencies
    call :print_message info "Installing dependencies..."
    
    call "!VENV_DIR!\Scripts\activate.bat"
    if %errorlevel% neq 0 (
        call :print_message error "Failed to activate virtual environment."
        exit /b 1
    )
    
    call :print_message info "Upgrading pip..."
    python -m pip install --upgrade pip
    if %errorlevel% neq 0 (
        call :print_message error "Failed to upgrade pip."
        exit /b 1
    )
    
    call :print_message info "Installing backend package..."
    cd "!BACKEND_ROOT!"
    python -m pip install -e .
    if %errorlevel% neq 0 (
        call :print_message error "Failed to install backend package."
        exit /b 1
    )
    
    call :print_message info "Installing CLI package..."
    cd "!CLI_ROOT!"
    python -m pip install -e .
    if %errorlevel% neq 0 (
        call :print_message error "Failed to install CLI package."
        exit /b 1
    )
    
    call :print_message success "Dependencies installed successfully."
    exit /b 0

:: ===================================================
:: Function: create_launcher_script
:: Creates a launcher script and adds to PATH
:: Returns:
::   0 - Launcher created successfully
::   1 - Failed to create launcher
:: ===================================================
:create_launcher_script
    call :print_message info "Creating launcher script..."
    
    if not exist "!BIN_DIR!" (
        mkdir "!BIN_DIR!"
        if %errorlevel% neq 0 (
            call :print_message error "Failed to create bin directory: !BIN_DIR!"
            exit /b 1
        )
    )
    
    :: Create the launcher batch file
    (
        echo @echo off
        echo :: JSON to Excel Conversion Tool CLI Launcher
        echo setlocal
        echo call "!VENV_DIR!\Scripts\activate.bat"
        echo json2excel %%*
        echo exit /b %%errorlevel%%
    ) > "!BIN_DIR!\json2excel.bat"
    
    if %errorlevel% neq 0 (
        call :print_message error "Failed to create launcher script."
        exit /b 1
    )
    
    :: Create Windows shortcut (optional)
    powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('!BIN_DIR!\json2excel.lnk'); $Shortcut.TargetPath = '!BIN_DIR!\json2excel.bat'; $Shortcut.Save()"
    
    call :add_to_path
    if %errorlevel% neq 0 (
        call :print_message warning "Failed to add launcher to PATH. You may need to do this manually."
    )
    
    call :print_message success "Launcher script created at !BIN_DIR!\json2excel.bat"
    exit /b 0

:: ===================================================
:: Function: add_to_path
:: Adds the bin directory to user's PATH
:: Returns:
::   0 - PATH updated successfully
::   1 - Failed to update PATH
:: ===================================================
:add_to_path
    call :print_message info "Adding launcher to PATH..."
    
    :: Check if already in PATH
    echo ;%PATH%; | find /i ";!BIN_DIR!;" > nul
    if %errorlevel% equ 0 (
        call :print_message info "Launcher already in PATH."
        exit /b 0
    )
    
    :: Add to PATH using setx
    setx PATH "%PATH%;!BIN_DIR!"
    if %errorlevel% neq 0 (
        call :print_message error "Failed to update PATH environment variable."
        exit /b 1
    )
    
    call :print_message success "Added launcher to PATH environment variable."
    call :print_message info "You may need to restart your command prompt or terminal to use the 'json2excel' command."
    exit /b 0

:: ===================================================
:: Main installation process
:: ===================================================
:main
    echo.
    echo  ===================================================
    echo  JSON to Excel Conversion Tool - CLI Installer
    echo  ===================================================
    echo.
    
    call :check_python
    if %errorlevel% neq 0 exit /b %errorlevel%
    
    call :create_virtual_environment
    if %errorlevel% neq 0 exit /b %errorlevel%
    
    call :install_dependencies
    if %errorlevel% neq 0 exit /b %errorlevel%
    
    call :create_launcher_script
    if %errorlevel% neq 0 exit /b %errorlevel%
    
    echo.
    call :print_message success "Installation completed successfully!"
    echo.
    call :print_message info "You can now use the JSON to Excel Conversion Tool by running:"
    echo.
    echo     json2excel [input_json_file] [output_excel_file] [options]
    echo.
    call :print_message info "For help and available options, run:"
    echo.
    echo     json2excel --help
    echo.
    call :print_message info "If the 'json2excel' command is not recognized,"
    call :print_message info "try restarting your command prompt or terminal."
    echo.
    
    exit /b 0

:: Start the installation
call :main
exit /b %errorlevel%