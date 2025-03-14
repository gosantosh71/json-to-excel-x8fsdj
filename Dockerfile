# Multi-stage Dockerfile for JSON to Excel Conversion Tool
#
# This Dockerfile defines the build process for creating Docker images of the
# JSON to Excel Conversion Tool with support for both CLI and web interface components.
# It supports separate build targets for development and production use cases.

# Base stage with common setup
FROM python:3.11-slim-bullseye AS base

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Copy requirements files
COPY src/backend/requirements.txt /app/requirements-backend.txt
COPY src/cli/requirements.txt /app/requirements-cli.txt 2>/dev/null || touch /app/requirements-cli.txt
COPY src/web/requirements.txt /app/requirements-web.txt

# Install common Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements-backend.txt

# Backend stage with core functionality
FROM base AS backend

# Copy backend source code
COPY src/backend /app/src/backend

# Build argument for skipping tests
ARG SKIP_TESTS=false

# Run backend tests if not skipped
RUN if [ "$SKIP_TESTS" = "false" ] && [ -d src/backend/tests ]; then \
        echo "Running backend tests..." && \
        pytest -xvs src/backend/tests; \
    else \
        echo "Skipping backend tests..."; \
    fi

# Create data directory for input/output files
RUN mkdir -p /data

# CLI stage
FROM backend AS cli

# Install CLI-specific dependencies if requirements file exists and is not empty
RUN if [ -s requirements-cli.txt ]; then \
        pip install -r requirements-cli.txt; \
    else \
        echo "No CLI-specific requirements found."; \
    fi

# Copy CLI source code
COPY src/cli /app/src/cli

# Run CLI tests if not skipped
RUN if [ "$SKIP_TESTS" = "false" ] && [ -d src/cli/tests ]; then \
        echo "Running CLI tests..." && \
        pytest -xvs src/cli/tests; \
    else \
        echo "Skipping CLI tests..."; \
    fi

# Volume for data files
VOLUME ["/data"]

# Set up CLI entrypoint
ENTRYPOINT ["python", "-m", "src.cli.json_to_excel"]

# Web stage
FROM backend AS web

# Install web-specific dependencies
RUN pip install -r requirements-web.txt

# Copy web source code
COPY src/web /app/src/web

# Run web tests if not skipped
RUN if [ "$SKIP_TESTS" = "false" ] && [ -d src/web/tests ]; then \
        echo "Running web tests..." && \
        pytest -xvs src/web/tests; \
    else \
        echo "Skipping web tests..."; \
    fi

# Volume for data files
VOLUME ["/data"]

# Expose port for web interface
EXPOSE 5000

# Set up web entrypoint
ENTRYPOINT ["python", "-m", "src.web.run"]

# Development stage for CLI
FROM cli AS cli-dev

# Add development-specific configuration
ENV PYTHONPATH=/app \
    FLASK_ENV=development \
    FLASK_DEBUG=1

# Enable source code mounting for development
VOLUME ["/app/src"]

# In development mode, use CMD instead of ENTRYPOINT for flexibility
ENTRYPOINT []
CMD ["/bin/bash"]

# Development stage for web
FROM web AS web-dev

# Add development-specific configuration
ENV PYTHONPATH=/app \
    FLASK_ENV=development \
    FLASK_DEBUG=1

# Enable source code mounting for development
VOLUME ["/app/src"]

# Provide a default command but allow override for development
ENTRYPOINT []
CMD ["python", "-m", "src.web.run"]

# Usage examples:
# Build CLI image:
#   docker build --target cli -t json2excel-cli .
#
# Build web image with tests skipped:
#   docker build --target web --build-arg SKIP_TESTS=true -t json2excel-web .
#
# Run CLI container:
#   docker run -v $(pwd)/data:/data json2excel-cli /data/input.json /data/output.xlsx
#
# Run web container:
#   docker run -p 5000:5000 -v $(pwd)/data:/data json2excel-web
#
# Run CLI development container with interactive shell:
#   docker run -it --rm -v $(pwd)/data:/data -v $(pwd)/src:/app/src json2excel-cli-dev
#
# Run web development container:
#   docker run -it --rm -p 5000:5000 -v $(pwd)/data:/data -v $(pwd)/src:/app/src json2excel-web-dev