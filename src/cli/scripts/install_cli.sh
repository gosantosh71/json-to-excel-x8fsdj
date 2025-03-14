#!/usr/bin/env bash
#
# install_cli.sh - Installation script for the JSON to Excel Conversion Tool CLI
#
# This script automates the installation process by:
# - Checking for proper Python version (3.9+)
# - Creating a virtual environment
# - Installing dependencies
# - Setting up command-line access
# - Configuring shell completion
#

set -e  # Exit on error

# Get script directory regardless of where it's called from
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
CLI_ROOT=${SCRIPT_DIR}/..
BACKEND_ROOT=${SCRIPT_DIR}/../../backend
VENV_DIR=${HOME}/.json2excel
BIN_DIR=${HOME}/.local/bin
COMPLETION_DIR=${HOME}/.bash_completion.d

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print a formatted message with color coding
# Args:
#   $1: message type (info, success, error, warning)
#   $2: message text
print_message() {
    local type=$1
    local message=$2
    local color
    
    case $type in
        info)
            color=$BLUE
            prefix="[INFO] "
            ;;
        success)
            color=$GREEN
            prefix="[SUCCESS] "
            ;;
        error)
            color=$RED
            prefix="[ERROR] "
            ;;
        warning)
            color=$YELLOW
            prefix="[WARNING] "
            ;;
        *)
            color=$NC
            prefix=""
            ;;
    esac
    
    echo -e "${color}${prefix}${message}${NC}"
}

# Check if Python 3.9 or higher is installed
# Returns:
#   0 if requirements are met, 1 otherwise
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_message "error" "Python 3 is not installed. Please install Python 3.9 or higher."
        return 1
    fi
    
    # Check if venv module is available
    if ! python3 -m venv --help &> /dev/null; then
        print_message "error" "Python venv module is not available. Please install it (e.g., python3-venv package)."
        return 1
    fi
    
    # Get Python version
    local version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+\.\d+')
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    
    # Check if version is at least 3.9
    if [[ $major -lt 3 || ($major -eq 3 && $minor -lt 9) ]]; then
        print_message "error" "Python 3.9 or higher is required. Found version: $version"
        return 1
    fi
    
    print_message "info" "Found Python $version"
    return 0
}

# Create a Python virtual environment for the application
# Returns:
#   0 if virtual environment was created successfully, 1 otherwise
create_virtual_environment() {
    if [ -d "$VENV_DIR" ]; then
        print_message "info" "Virtual environment already exists at $VENV_DIR"
        
        # Check if it's a valid virtual environment
        if [ ! -f "$VENV_DIR/bin/activate" ]; then
            print_message "warning" "Existing directory is not a valid virtual environment. Removing and recreating..."
            rm -rf "$VENV_DIR"
        else
            return 0
        fi
    fi
    
    print_message "info" "Creating virtual environment at $VENV_DIR"
    
    # Create directory if it doesn't exist
    mkdir -p "$VENV_DIR"
    
    # Create virtual environment
    if ! python3 -m venv "$VENV_DIR"; then
        print_message "error" "Failed to create virtual environment"
        return 1
    fi
    
    print_message "success" "Virtual environment created successfully"
    return 0
}

# Install required Python dependencies in the virtual environment
# Returns:
#   0 if dependencies were installed successfully, 1 otherwise
install_dependencies() {
    print_message "info" "Installing dependencies..."
    
    # Activate virtual environment
    source "${VENV_DIR}/bin/activate"
    
    # Upgrade pip
    print_message "info" "Upgrading pip to latest version..."
    if ! pip install --upgrade pip > /dev/null 2>&1; then
        print_message "error" "Failed to upgrade pip"
        deactivate
        return 1
    fi
    
    # Install backend package
    print_message "info" "Installing backend package..."
    if [ ! -d "$BACKEND_ROOT" ]; then
        print_message "error" "Backend directory not found: $BACKEND_ROOT"
        deactivate
        return 1
    fi
    
    if ! pip install -e "$BACKEND_ROOT" > /dev/null 2>&1; then
        print_message "error" "Failed to install backend package"
        deactivate
        return 1
    fi
    
    # Install CLI package
    print_message "info" "Installing CLI package..."
    if [ ! -d "$CLI_ROOT" ]; then
        print_message "error" "CLI directory not found: $CLI_ROOT"
        deactivate
        return 1
    fi
    
    if ! pip install -e "$CLI_ROOT" > /dev/null 2>&1; then
        print_message "error" "Failed to install CLI package"
        deactivate
        return 1
    fi
    
    # Deactivate virtual environment
    deactivate
    
    print_message "success" "Dependencies installed successfully"
    return 0
}

# Create a launcher script for easy access to the CLI tool
# Returns:
#   0 if launcher script was created successfully, 1 otherwise
create_launcher_script() {
    print_message "info" "Creating launcher script..."
    
    # Create bin directory if it doesn't exist
    mkdir -p "$BIN_DIR"
    
    # Create launcher script
    local launcher="$BIN_DIR/json_to_excel"
    
    cat > "$launcher" << EOF
#!/usr/bin/env bash
# Launcher script for JSON to Excel Conversion Tool

# Activate virtual environment and run the CLI tool
source "${VENV_DIR}/bin/activate"
python -m json_to_excel.cli "\$@"
deactivate
EOF
    
    # Make launcher executable
    chmod +x "$launcher"
    
    # Create symlink if needed
    if [ ! -f "/usr/local/bin/json_to_excel" ] && [ -d "/usr/local/bin" ] && [ -w "/usr/local/bin" ]; then
        print_message "info" "Creating symlink in /usr/local/bin for system-wide access..."
        ln -sf "$launcher" /usr/local/bin/json_to_excel
    fi
    
    # Check if BIN_DIR is in PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        print_message "warning" "$BIN_DIR is not in your PATH. Add it to your shell configuration file."
        print_message "info" "You can add it by running: echo 'export PATH=\"\$PATH:$BIN_DIR\"' >> ~/.bashrc"
    fi
    
    print_message "success" "Launcher script created at $launcher"
    return 0
}

# Set up command-line completion for the CLI tool
# Returns:
#   0 if shell completion was set up successfully, 1 otherwise
setup_shell_completion() {
    print_message "info" "Setting up shell completion..."
    
    # Create completion directory if it doesn't exist
    mkdir -p "$COMPLETION_DIR"
    
    # Copy completion script
    local completion_script="$COMPLETION_DIR/json_to_excel-completion.bash"
    cp "$SCRIPT_DIR/cli_completion.sh" "$completion_script"
    chmod +x "$completion_script"
    
    # Detect shell
    local shell=$(basename "$SHELL")
    
    # Add to appropriate shell config file
    case $shell in
        bash)
            if ! grep -q "source $completion_script" ~/.bashrc 2>/dev/null; then
                print_message "info" "Adding completion script to ~/.bashrc"
                echo "" >> ~/.bashrc
                echo "# JSON to Excel CLI completion" >> ~/.bashrc
                echo "source $completion_script" >> ~/.bashrc
            fi
            ;;
        zsh)
            if ! grep -q "source $completion_script" ~/.zshrc 2>/dev/null; then
                print_message "info" "Adding completion script to ~/.zshrc"
                echo "" >> ~/.zshrc
                echo "# JSON to Excel CLI completion" >> ~/.zshrc
                echo "source $completion_script" >> ~/.zshrc
                echo "autoload -Uz compinit && compinit" >> ~/.zshrc
            fi
            ;;
        *)
            print_message "warning" "Unknown shell: $shell. Manual configuration required for command completion."
            print_message "info" "Add the following line to your shell config file:"
            print_message "info" "  source $completion_script"
            ;;
    esac
    
    print_message "success" "Shell completion set up successfully"
    return 0
}

# Cleanup in case of failure
cleanup() {
    print_message "warning" "Installation failed. Cleaning up..."
    # Don't remove the virtual environment as it might be salvageable
    print_message "info" "You can retry the installation or remove $VENV_DIR manually."
}

# Main function that orchestrates the installation process
# Returns:
#   0 for success, non-zero for failure
main() {
    print_message "info" "=== JSON to Excel Conversion Tool CLI Installation ==="
    
    # Check if required files and directories exist
    if [ ! -f "$SCRIPT_DIR/cli_completion.sh" ]; then
        print_message "error" "Required file not found: $SCRIPT_DIR/cli_completion.sh"
        return 1
    fi
    
    # Check Python version
    if ! check_python; then
        return 1
    fi
    
    # Create virtual environment
    if ! create_virtual_environment; then
        cleanup
        return 1
    fi
    
    # Install dependencies
    if ! install_dependencies; then
        cleanup
        return 1
    fi
    
    # Create launcher script
    if ! create_launcher_script; then
        cleanup
        return 1
    fi
    
    # Setup shell completion
    if ! setup_shell_completion; then
        # Not critical, continue
        print_message "warning" "Shell completion setup failed, but installation can continue."
    fi
    
    print_message "success" "=== Installation Completed Successfully ==="
    print_message "info" "You can now use the JSON to Excel Conversion Tool by running: json_to_excel"
    print_message "info" "For help, run: json_to_excel --help"
    print_message "info" "To convert a file, run: json_to_excel convert input.json output.xlsx"
    print_message "info" "Note: You may need to restart your shell or run 'source ~/.bashrc' to enable completion"
    
    return 0
}

# Run main function
main
exit $?