@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo Building JSON to Excel Converter Executables
echo ===================================================
echo.

echo Setting environment variables and paths...
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%\..\..
set OUTPUT_DIR=%PROJECT_ROOT%\dist
set PYINSTALLER_OPTS=--clean --noconfirm
set CLI_SPEC=%PROJECT_ROOT%\pyinstaller\cli.spec
set WEB_SPEC=%PROJECT_ROOT%\pyinstaller\web.spec

echo Checking prerequisites...
call :check_prerequisites
if %ERRORLEVEL% neq 0 (
    echo Prerequisites check failed. Please resolve the issues and try again.
    exit /b %ERRORLEVEL%
)

echo Setting up the build environment...
call :setup_environment
if %ERRORLEVEL% neq 0 (
    echo Environment setup failed. Please resolve the issues and try again.
    exit /b %ERRORLEVEL%
)

echo Building CLI executable...
call :build_cli_executable
if %ERRORLEVEL% neq 0 (
    echo CLI build failed. Please resolve the issues and try again.
    exit /b %ERRORLEVEL%
)

echo Building Web executable...
call :build_web_executable
if %ERRORLEVEL% neq 0 (
    echo Web build failed. Please resolve the issues and try again.
    exit /b %ERRORLEVEL%
)

echo Cleaning up build artifacts...
call :cleanup_build_artifacts

echo ===================================================
echo Build completed successfully!
echo Executables are located in: %OUTPUT_DIR%
echo ===================================================

exit /b 0

:check_prerequisites
echo Checking for Python...
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found. Please install Python 3.9 or higher.
    exit /b 2
)

echo Checking for PyInstaller...
where pyinstaller >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: PyInstaller not found. Please install PyInstaller.
    exit /b 2
)

echo Checking for required Python packages...
python -c "try:\n    import pandas, openpyxl, colorama, tqdm, click, tabulate\nexcept ImportError:\n    print('Required packages missing')\n    exit(1)\nexit(0)"
if %ERRORLEVEL% neq 0 (
    echo Error: Required Python packages not found.
    exit /b 2
)

exit /b 0

:setup_environment
echo Setting PYTHONPATH...
set PYTHONPATH=%PROJECT_ROOT%\src\cli;%PROJECT_ROOT%\src\backend
set "PATH=%PROJECT_ROOT%\src\cli;%PROJECT_ROOT%\src\backend;%PATH%"

echo Creating output directory...
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
    if %ERRORLEVEL% neq 0 (
        echo Error: Build directory creation failed.
        exit /b 3
    )
)

exit /b 0

:build_cli_executable
echo Starting CLI build...
echo Running PyInstaller: pyinstaller %PYINSTALLER_OPTS% "%CLI_SPEC%"
pyinstaller %PYINSTALLER_OPTS% "%CLI_SPEC%"
if %ERRORLEVEL% neq 0 (
    echo Error: PyInstaller build process failed.
    exit /b 4
)

echo CLI build completed.
exit /b 0

:build_web_executable
echo Starting Web build...
echo Running PyInstaller: pyinstaller %PYINSTALLER_OPTS% "%WEB_SPEC%"
pyinstaller %PYINSTALLER_OPTS% "%WEB_SPEC%"
if %ERRORLEVEL% neq 0 (
    echo Error: PyInstaller build process failed.
    exit /b 5
)

echo Web build completed.
exit /b 0

:cleanup_build_artifacts
echo Removing build directories...
rmdir /s /q "%PROJECT_ROOT%\build"
if %ERRORLEVEL% equ 0 (
    echo Removed build directory.
) else (
    echo Failed to remove build directory.
)

echo Removing PyInstaller cache files...
del /f /q "%PROJECT_ROOT%\*.spec"
if %ERRORLEVEL% equ 0 (
    echo Removed spec files.
) else (
    echo Failed to remove spec files.
)

echo Removing temporary files...
if exist "%PROJECT_ROOT%\__pycache__" (
    rmdir /s /q "%PROJECT_ROOT%\__pycache__"
    if %ERRORLEVEL% equ 0 (
        echo Removed pycache directory.
    ) else (
        echo Failed to remove pycache directory.
    )
)

exit /b 0