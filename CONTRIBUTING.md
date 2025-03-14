# Contributing to JSON to Excel Conversion Tool

Thank you for your interest in contributing to the JSON to Excel Conversion Tool! This document provides guidelines and instructions for contributing to the project. By participating in this project, you agree to abide by its terms and our [Code of Conduct](CODE_OF_CONDUCT.md).

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Development Environment Setup](#development-environment-setup)
  - [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
  - [Issue Tracking](#issue-tracking)
  - [Branching Strategy](#branching-strategy)
  - [Commit Guidelines](#commit-guidelines)
- [Coding Standards](#coding-standards)
  - [Code Style](#code-style)
  - [Documentation](#documentation)
  - [Testing](#testing)
- [Pull Request Process](#pull-request-process)
  - [Creating a Pull Request](#creating-a-pull-request)
  - [Review Process](#review-process)
  - [Continuous Integration](#continuous-integration)
  - [Merging](#merging)
- [Release Process](#release-process)
- [Community](#community)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md) that all contributors are expected to follow. Please read it before participating in this project.

## Getting Started

### Development Environment Setup

To set up your development environment:

1. **Prerequisites**:
   - Python 3.9 or higher
   - Git
   - pip (Python package manager)
   - A code editor (VS Code recommended)

2. **Fork and Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/json-to-excel-converter.git
   cd json-to-excel-converter
   ```

3. **Create a Virtual Environment**:
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. **Install Development Dependencies**:
   ```bash
   # Install the package in development mode with all dependencies
   pip install -e ".[dev]"
   ```

5. **Set Up Pre-commit Hooks**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

For more detailed setup instructions, refer to the [Developer Guide](docs/developer_guide.md).

### Project Structure

The project is organized into the following key directories:

- `src/` - Source code for the tool
  - `backend/` - Core conversion functionality
  - `cli/` - Command-line interface
  - `web/` - Optional web interface
- `tests/` - Test suite
  - `unit/` - Unit tests
  - `integration/` - Integration tests
  - `e2e/` - End-to-end tests
- `docs/` - Documentation

## Development Workflow

### Issue Tracking

1. **Finding Issues**: Browse the [Issues](https://github.com/organization/json-to-excel-converter/issues) section to find tasks marked as "good first issue" or "help wanted".

2. **Creating Issues**: Before starting work on a new feature or bug fix, make sure an issue exists for it. If not, create one with:
   - Clear, descriptive title
   - Detailed description of the problem or feature
   - Steps to reproduce (for bugs)
   - Expected behavior
   - Screenshots or examples (if applicable)

3. **Assigning Issues**: Comment on an issue to express your interest in working on it. A maintainer will assign it to you.

### Branching Strategy

We follow a simplified Git Flow branching strategy:

1. **Main Branches**:
   - `main`: Production-ready code
   - `develop`: Integration branch for features and fixes

2. **Feature Branches**:
   - Create branches from `develop` named according to the feature or fix
   - Pattern: `feature/issue-number-short-description` or `bugfix/issue-number-short-description`
   
   Example:
   ```bash
   # For a new feature
   git checkout develop
   git pull
   git checkout -b feature/123-add-csv-export
   
   # For a bug fix
   git checkout develop
   git pull
   git checkout -b bugfix/456-fix-array-handling
   ```

3. **Keep Your Branch Updated**:
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

### Commit Guidelines

1. **Commit Format**:
   - Use clear, descriptive commit messages
   - Start with a verb in the present tense (e.g., "Add", "Fix", "Update")
   - Reference the issue number using the `#` symbol
   
   Example:
   ```
   Add CSV export functionality
   
   - Implement CSV writer component
   - Add CLI option for CSV format
   - Update documentation
   
   Fixes #123
   ```

2. **Atomic Commits**:
   - Make focused commits that address a single concern
   - Avoid mixing unrelated changes in a single commit

3. **Commit Often**:
   - Make small, logical commits rather than large, monolithic ones
   - This makes the review process easier and provides a better history

## Coding Standards

### Code Style

We follow Python best practices and use tools to enforce a consistent style:

1. **PEP 8**: Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide

2. **Code Formatting**: 
   - We use [Black](https://black.readthedocs.io/) for automatic code formatting
   - Run `black src/ tests/` before committing

3. **Linting**: 
   - We use [Flake8](https://flake8.pycqa.org/) to check for style and logical errors
   - Run `flake8 src/ tests/` to check for issues

4. **Type Hints**:
   - Use Python type annotations for function parameters and return types
   - Example:
     ```python
     def process_json(json_data: Dict[str, Any]) -> pd.DataFrame:
         """Process JSON data into a DataFrame."""
         # Implementation
     ```

### Documentation

1. **Code Documentation**:
   - Use Google-style docstrings for all modules, classes, and functions
   - Include descriptions, parameters, return values, and examples
   - Example:
     ```python
     def transform_json(json_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
         """Transform JSON data into a pandas DataFrame.
         
         Args:
             json_data: The JSON data to transform
             options: Optional transformation options
             
         Returns:
             A pandas DataFrame containing the transformed data
             
         Raises:
             ValueError: If json_data is None or empty
         """
     ```

2. **README and Documentation Files**:
   - Update relevant documentation files when changing functionality
   - Ensure examples are up-to-date
   - Use clear, concise language and include code examples where appropriate

### Testing

1. **Test Requirements**:
   - All new features must include tests
   - Bug fixes should include a test that reproduces the bug
   - Maintain or improve code coverage (minimum 90% required)

2. **Test Types**:
   - **Unit Tests**: Test individual components in isolation
   - **Integration Tests**: Test interactions between components
   - **End-to-End Tests**: Test complete workflows

3. **Running Tests**:
   ```bash
   # Run all tests
   pytest
   
   # Run with coverage report
   pytest --cov=src
   
   # Run specific test types
   pytest tests/unit/
   pytest tests/integration/
   pytest tests/e2e/
   ```

4. **Test Naming and Structure**:
   - Test files should follow the pattern `test_*.py`
   - Test functions should start with `test_`
   - Use descriptive function names that explain what is being tested
   - Follow the Arrange-Act-Assert pattern

## Pull Request Process

### Creating a Pull Request

1. **Ensure your branch is up-to-date**:
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

2. **Run tests and linting locally**:
   ```bash
   # Format code with Black
   black src/ tests/
   
   # Run linting
   flake8 src/ tests/
   
   # Run tests
   pytest
   ```

3. **Create a pull request on GitHub**:
   - Use a clear, descriptive title
   - Reference the issue number in the description with "Fixes #123" or "Closes #123"
   - Fill out the pull request template
   - Provide details on what your changes do and why they're needed
   - Include any relevant screenshots or examples

4. **PR Description Template**:
   ```
   ## Description
   [Describe the changes made in this PR]
   
   ## Related Issue
   Fixes #[issue_number]
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Code refactoring
   - [ ] Performance improvement
   
   ## How Has This Been Tested?
   [Describe the tests run to verify your changes]
   
   ## Checklist
   - [ ] My code follows the style guidelines of this project
   - [ ] I have performed a self-review of my own code
   - [ ] I have commented my code, particularly in hard-to-understand areas
   - [ ] I have made corresponding changes to the documentation
   - [ ] My changes generate no new warnings
   - [ ] I have added tests that prove my fix is effective or that my feature works
   - [ ] New and existing unit tests pass locally with my changes
   ```

### Review Process

1. **Code Reviews**:
   - All pull requests require at least one review from a maintainer
   - Address all review comments before requesting re-review
   - Explain your approach in response to comments when necessary
   - Be open to feedback and suggestions for improvement

2. **Responding to Reviews**:
   - Respond to each comment, either by addressing it or explaining why you chose a different approach
   - Make requested changes in new commits during the review process
   - Once the review is complete, squash commits if requested

### Continuous Integration

1. **CI Pipeline**:
   - Each pull request triggers automated tests and checks
   - The pipeline includes:
     - Code linting with Flake8
     - Format checking with Black
     - Unit, integration, and E2E tests
     - Coverage reports

2. **Passing CI**:
   - All CI checks must pass before a PR can be merged
   - If CI fails, review the logs to identify and fix the issues

### Merging

1. **Merge Requirements**:
   - Approved by at least one maintainer
   - All CI checks pass
   - All discussions resolved
   - Up-to-date with the base branch

2. **Merge Strategy**:
   - Pull requests are merged using the "Squash and merge" strategy
   - This creates a single, clean commit on the target branch
   - The commit message should summarize the changes

3. **After Merge**:
   - Delete the feature branch
   - Update relevant issues and projects
   - Verify the changes work correctly in the target branch

## Release Process

The JSON to Excel Conversion Tool follows Semantic Versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

The release process is as follows:

1. **Release Preparation**:
   - A release branch is created from `develop`
   - Version numbers are updated in appropriate files
   - Final testing and bug fixes are applied

2. **Release Creation**:
   - The release branch is merged to `main`
   - A tag is created with the version number
   - Packages are built and published to distribution channels

3. **Post-Release**:
   - Release notes are published
   - Documentation is updated
   - The release branch is merged back to `develop`

## Community

- **Questions and Discussions**: Use the [Discussions](https://github.com/organization/json-to-excel-converter/discussions) forum for questions and ideas
- **Reporting Bugs**: Open an issue using the bug report template
- **Requesting Features**: Open an issue using the feature request template
- **Getting Help**: Reach out to maintainers through discussions or issues

Thank you for contributing to the JSON to Excel Conversion Tool!