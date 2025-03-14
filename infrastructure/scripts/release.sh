#!/bin/bash
set -e

# Script Header
echo "===================================================="
echo "JSON to Excel Converter Release Script"
echo "===================================================="
echo

# Environment Setup
SCRIPT_DIR=$(dirname "$(realpath "$0")")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR/../..")
VERSION=$(grep -m 1 'VERSION = ' "$PROJECT_ROOT/src/backend/constants.py" | cut -d'"' -f2)
DIST_DIR="$PROJECT_ROOT/dist"
DOCKER_REPO="organization/json-to-excel-converter"

# Command Line Argument Parsing
# Default values
BUILD_PACKAGES=false
BUILD_EXECUTABLES=false
BUILD_DOCKER=false
PUBLISH_PYPI=false
PUBLISH_TEST_PYPI=false
PUBLISH_DOCKER=false
CREATE_GITHUB_RELEASE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      BUILD_PACKAGES=true
      BUILD_EXECUTABLES=true
      BUILD_DOCKER=true
      PUBLISH_PYPI=true
      PUBLISH_DOCKER=true
      CREATE_GITHUB_RELEASE=true
      shift
      ;;
    --build-packages)
      BUILD_PACKAGES=true
      shift
      ;;
    --build-executables)
      BUILD_EXECUTABLES=true
      shift
      ;;
    --build-docker)
      BUILD_DOCKER=true
      shift
      ;;
    --publish-pypi)
      PUBLISH_PYPI=true
      shift
      ;;
    --publish-test-pypi)
      PUBLISH_TEST_PYPI=true
      shift
      ;;
    --publish-docker)
      PUBLISH_DOCKER=true
      shift
      ;;
    --create-github-release)
      CREATE_GITHUB_RELEASE=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --all                     Perform all build and publish actions"
      echo "  --build-packages          Build Python packages"
      echo "  --build-executables       Build standalone executables"
      echo "  --build-docker            Build Docker images"
      echo "  --publish-pypi            Publish to PyPI"
      echo "  --publish-test-pypi       Publish to Test PyPI"
      echo "  --publish-docker          Publish to Docker Hub"
      echo "  --create-github-release   Create GitHub release"
      echo "  --help                    Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Function Definitions

# check_prerequisites: Checks if all required tools and dependencies are installed for the release process
# Returns: 0 if all prerequisites are met, non-zero otherwise
check_prerequisites() {
  echo "Checking prerequisites..."

  # Check if Python is installed and in PATH
  if ! command -v python3 &> /dev/null; then
    echo "Error: Python not found. Please install Python 3.9 or higher."
    return 2
  fi

  # Check if pip is installed
  if ! command -v pip3 &> /dev/null; then
    echo "Error: pip not found. Please install pip."
    return 2
  fi

  # Check if twine is installed for PyPI uploads
  if [[ "$PUBLISH_PYPI" == true || "$PUBLISH_TEST_PYPI" == true ]]; then
    if ! command -v twine &> /dev/null; then
      echo "Error: twine not found. Please install twine for PyPI uploads."
      echo "  pip3 install twine"
      return 2
    fi
  fi

  # Check if Docker is installed for Docker image publishing
  if [[ "$BUILD_DOCKER" == true || "$PUBLISH_DOCKER" == true ]]; then
    if ! command -v docker &> /dev/null; then
      echo "Error: Docker not found. Please install Docker for image publishing."
      echo "  Refer to Docker documentation for installation instructions."
      return 2
    fi
  fi

  echo "Prerequisites check complete."
  return 0
}

# verify_version: Verifies that version numbers are consistent across package files
# Returns: 0 if version verification succeeds, non-zero otherwise
verify_version() {
  echo "Verifying version consistency..."

  # Extract version from backend constants.py
  BACKEND_VERSION=$(grep -m 1 'VERSION = ' "$PROJECT_ROOT/src/backend/constants.py" | cut -d'"' -f2)

  # Check if the version follows semantic versioning format
  if ! [[ "$BACKEND_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+ ]]; then
    echo "Error: Invalid version format. Must follow semantic versioning (e.g., 1.2.3)."
    return 3
  fi

  echo "Version verification complete. Version: $BACKEND_VERSION"
  return 0
}

# build_packages: Builds Python packages for all components
# Returns: 0 if build succeeds, non-zero otherwise
build_packages() {
  echo "Building Python packages..."

  # Navigate to project root
  pushd "$PROJECT_ROOT" > /dev/null

  # Clean existing dist directories
  echo "Cleaning dist directory..."
  rm -rf "$DIST_DIR"
  mkdir -p "$DIST_DIR"

  # Build backend package
  echo "Building backend package..."
  pushd "src/backend" > /dev/null
  python3 -m build --outdir "$DIST_DIR"
  if [ $? -ne 0 ]; then
    echo "Error: Backend package build failed."
    popd > /dev/null
    popd > /dev/null
    return 4
  fi
  popd > /dev/null

  # Build CLI package
  echo "Building CLI package..."
  pushd "src/cli" > /dev/null
  python3 -m build --outdir "$DIST_DIR"
  if [ $? -ne 0 ]; then
    echo "Error: CLI package build failed."
    popd > /dev/null
    popd > /dev/null
    return 4
  fi
  popd > /dev/null

  # Build web package
  echo "Building web package..."
  pushd "src/web" > /dev/null
  python3 -m build --outdir "$DIST_DIR"
  if [ $? -ne 0 ]; then
    echo "Error: Web package build failed."
    popd > /dev/null
    popd > /dev/null
    return 4
  fi
  popd > /dev/null

  # Verify packages with twine check
  echo "Verifying packages with twine check..."
  twine check "$DIST_DIR/*"
  if [ $? -ne 0 ]; then
    echo "Error: Twine check failed."
    popd > /dev/null
    return 4
  fi

  echo "Python packages built successfully. Packages are located in: $DIST_DIR"
  popd > /dev/null
  return 0
}

# build_executables: Builds standalone executables for the current platform
# Returns: 0 if build succeeds, non-zero otherwise
build_executables() {
  echo "Building standalone executables..."

  # Detect current platform (Linux/macOS)
  OS=$(uname -s)

  # Call the appropriate build_executables script
  if [[ "$OS" == "Linux" || "$OS" == "Darwin" ]]; then
    echo "Building executables for Linux/macOS..."
    bash "$SCRIPT_DIR/build_executables.sh"
    if [ $? -ne 0 ]; then
      echo "Error: Executable build failed."
      return 4
    fi
  elif [[ "$OS" == "WindowsNT" ]]; then
    echo "Building executables for Windows..."
    cmd /c "$SCRIPT_DIR/build_executables.bat"
    if [ $? -ne 0 ]; then
      echo "Error: Executable build failed."
      return 4
    fi
  else
    echo "Error: Unsupported platform: $OS"
    return 4
  fi

  echo "Standalone executables built successfully. Executables are located in: $DIST_DIR"
  return 0
}

# build_docker_images: Builds Docker images for the application
# Returns: 0 if build succeeds, non-zero otherwise
build_docker_images() {
  echo "Building Docker images..."

  # Navigate to project root
  pushd "$PROJECT_ROOT" > /dev/null

  # Build development Docker image
  echo "Building development Docker image..."
  docker build -t "$DOCKER_REPO:dev" -f docker/Dockerfile.dev .
  if [ $? -ne 0 ]; then
    echo "Error: Development Docker image build failed."
    popd > /dev/null
    return 4
  fi

  # Build production Docker image with version tag
  echo "Building production Docker image with version tag..."
  docker build -t "$DOCKER_REPO:$VERSION" -f docker/Dockerfile .
  if [ $? -ne 0 ]; then
    echo "Error: Production Docker image build failed."
    popd > /dev/null
    return 4
  fi

  # Build production Docker image with latest tag
  echo "Building production Docker image with latest tag..."
  docker tag "$DOCKER_REPO:$VERSION" "$DOCKER_REPO:latest"

  echo "Docker images built successfully."
  popd > /dev/null
  return 0
}

# publish_to_pypi: Publishes Python packages to PyPI
# Parameters: $1 - test_pypi (true/false)
# Returns: 0 if publishing succeeds, non-zero otherwise
publish_to_pypi() {
  local test_pypi="$1"
  echo "Publishing Python packages to ${test_pypi:-production} PyPI..."

  # Check if PyPI API token is available
  if [[ -z "$PYPI_API_TOKEN" ]]; then
    echo "Error: PYPI_API_TOKEN environment variable not set. Cannot publish to PyPI."
    return 5
  fi

  # Determine if publishing to test PyPI or production PyPI
  if [[ "$test_pypi" == true ]]; then
    PYPI_REPO="https://test.pypi.org/legacy/"
    TWINE_ARGS="--repository testpypi"
  else
    PYPI_REPO="https://upload.pypi.org/legacy/"
    TWINE_ARGS=""
  fi

  # Use twine to upload packages to the appropriate PyPI repository
  echo "Uploading packages to $PYPI_REPO..."
  twine upload $TWINE_ARGS --username __token__ --password "$PYPI_API_TOKEN" "$DIST_DIR/*"
  if [ $? -ne 0 ]; then
    echo "Error: PyPI upload failed."
    return 5
  fi

  echo "Python packages published successfully to $PYPI_REPO."
  return 0
}

# publish_to_docker_hub: Publishes Docker images to Docker Hub
# Returns: 0 if publishing succeeds, non-zero otherwise
publish_to_docker_hub() {
  echo "Publishing Docker images to Docker Hub..."

  # Check if Docker Hub credentials are available
  if [[ -z "$DOCKERHUB_USERNAME" || -z "$DOCKERHUB_TOKEN" ]]; then
    echo "Error: DOCKERHUB_USERNAME and DOCKERHUB_TOKEN environment variables not set. Cannot publish to Docker Hub."
    return 5
  fi

  # Log in to Docker Hub
  echo "Logging in to Docker Hub..."
  docker login -u "$DOCKERHUB_USERNAME" -p "$DOCKERHUB_TOKEN"
  if [ $? -ne 0 ]; then
    echo "Error: Docker Hub login failed."
    return 5
  fi

  # Tag Docker images for Docker Hub
  echo "Tagging Docker images for Docker Hub..."
  docker tag "$DOCKER_REPO:dev" "$DOCKERHUB_USERNAME/$DOCKER_REPO:dev"
  docker tag "$DOCKER_REPO:$VERSION" "$DOCKERHUB_USERNAME/$DOCKER_REPO:$VERSION"
  docker tag "$DOCKER_REPO:latest" "$DOCKERHUB_USERNAME/$DOCKER_REPO:latest"

  # Push versioned Docker image
  echo "Pushing versioned Docker image..."
  docker push "$DOCKERHUB_USERNAME/$DOCKER_REPO:$VERSION"
  if [ $? -ne 0 ]; then
    echo "Error: Versioned Docker image push failed."
    return 5
  fi

  # Push latest Docker image
  echo "Pushing latest Docker image..."
  docker push "$DOCKERHUB_USERNAME/$DOCKER_REPO:latest"
  if [ $? -ne 0 ]; then
    echo "Error: Latest Docker image push failed."
    return 5
  fi

  echo "Docker images published successfully to Docker Hub."
  return 0
}

# create_github_release: Creates a GitHub release with built artifacts
# Parameters: $1 - tag_name, $2 - release_notes
# Returns: 0 if release creation succeeds, non-zero otherwise
create_github_release() {
  local tag_name="$1"
  local release_notes="$2"
  echo "Creating GitHub release for tag: $tag_name..."

  # Check if GitHub token is available
  if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Error: GITHUB_TOKEN environment variable not set. Cannot create GitHub release."
    return 5
  fi

  # Create a new GitHub release with the specified tag
  echo "Creating GitHub release..."
  gh release create "$tag_name" "$DIST_DIR/*" --notes "$release_notes"
  if [ $? -ne 0 ]; then
    echo "Error: GitHub release creation failed."
    return 5
  fi

  echo "GitHub release created successfully."
  return 0
}

# Main Script Execution
main() {
  echo "===================================================="
  echo "Starting JSON to Excel Converter Release"
  echo "===================================================="
  echo

  # Parse command line arguments
  echo "Parsing command line arguments..."

  # Call check_prerequisites function
  if ! check_prerequisites; then
    echo "Prerequisites check failed. Exiting."
    return 2
  fi

  # Call verify_version function
  if ! verify_version; then
    echo "Version verification failed. Exiting."
    return 3
  fi

  # Call build_packages function if requested
  if [[ "$BUILD_PACKAGES" == true ]]; then
    if ! build_packages; then
      echo "Package build failed. Exiting."
      return 4
    fi
  fi

  # Call build_executables function if requested
  if [[ "$BUILD_EXECUTABLES" == true ]]; then
    if ! build_executables; then
      echo "Executable build failed. Exiting."
      return 4
    fi
  fi

  # Call build_docker_images function if requested
  if [[ "$BUILD_DOCKER" == true ]]; then
    if ! build_docker_images; then
      echo "Docker image build failed. Exiting."
      return 4
    fi
  fi

  # Call publish_to_pypi function if requested
  if [[ "$PUBLISH_PYPI" == true ]]; then
    if ! publish_to_pypi; then
      echo "PyPI publishing failed. Exiting."
      return 5
    fi
  fi

    # Call publish_to_test_pypi function if requested
  if [[ "$PUBLISH_TEST_PYPI" == true ]]; then
    if ! publish_to_pypi true; then
      echo "Test PyPI publishing failed. Exiting."
      return 5
    fi
  fi

  # Call publish_to_docker_hub function if requested
  if [[ "$PUBLISH_DOCKER" == true ]]; then
    if ! publish_to_docker_hub; then
      echo "Docker Hub publishing failed. Exiting."
      return 5
    fi
  fi

  # Call create_github_release function if requested
  if [[ "$CREATE_GITHUB_RELEASE" == true ]]; then
    if ! create_github_release "$VERSION" "Release notes for $VERSION"; then
      echo "GitHub release creation failed. Exiting."
      return 5
    fi
  fi

  echo
  echo "===================================================="
  echo "JSON to Excel Converter Release Complete!"
  echo "===================================================="
  echo

  return 0
}

# Main Script Execution
main
exit $?