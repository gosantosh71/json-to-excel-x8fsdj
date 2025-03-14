# Deployment Guide for JSON to Excel Conversion Tool Web Interface

This document provides comprehensive instructions for deploying the web interface component of the JSON to Excel Conversion Tool in various environments.

## Prerequisites

Before deploying the web interface, ensure you have the following prerequisites installed:

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment tool (venv or conda)
- Docker and Docker Compose (for containerized deployment)
- Git (for source code management)

## Development Deployment

### Local Development Setup

1.  **Clone the repository**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and activate a virtual environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables**

    Create a `.env` file in the root directory with the following variables:

    ```
    FLASK_APP=src.web.app
    FLASK_ENV=development
    FLASK_DEBUG=1
    SECRET_KEY=<your_secret_key>
    UPLOAD_FOLDER=./uploads
    MAX_CONTENT_LENGTH=5242880
    LOG_LEVEL=INFO
    ```

    Alternatively, set these variables directly in your shell environment.

5.  **Run the development server**

    ```bash
    # Set up development environment
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt

    # Run development server
    FLASK_APP=src.web.app FLASK_ENV=development python -m src.web.run
    ```

### Development with Docker

1.  **Clone the repository**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Build and run using Docker Compose**

    ```bash
    # Build and run with Docker Compose
    docker-compose up --build
    ```

3.  **Access the web interface at http://localhost:5000**

## Production Deployment

### Standalone Server Deployment

1.  **Clone the repository**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and activate a virtual environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install production dependencies**

    ```bash
    pip install gunicorn
    pip install -r requirements.txt
    ```

4.  **Configure environment variables for production**

    Set the following environment variables:

    ```
    FLASK_APP=src.web.app
    FLASK_ENV=production
    SECRET_KEY=<your_strong_secret_key>
    UPLOAD_FOLDER=/var/app/uploads
    MAX_CONTENT_LENGTH=5242880
    LOG_LEVEL=WARNING
    ```

5.  **Run with Gunicorn WSGI server**

    ```bash
    # Install production dependencies
    pip install gunicorn

    # Run with Gunicorn
    FLASK_APP=src.web.app FLASK_ENV=production gunicorn --config src.web.gunicorn.conf.py src.web.wsgi:application
    ```

### Docker Production Deployment

1.  **Clone the repository**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Configure production environment variables**

    Set the required environment variables in a `.env` file or directly in your deployment environment.

3.  **Build and run using production Docker Compose configuration**

    ```bash
    # Build and run production containers
    docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d --build
    ```

4.  **Set up reverse proxy (Nginx or Apache) for SSL termination**

    Configure a reverse proxy to handle SSL termination and forward requests to the Gunicorn server.

    ```nginx
    server {
        listen 80;
        server_name your-domain.com;

        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /path/to/cert.pem;
        ssl_certificate_key /path/to/key.pem;

        location / {
            proxy_pass http://localhost:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

### Cloud Deployment Options

Instructions for deploying to common cloud platforms:

- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service
- Heroku

Follow the platform-specific documentation for deploying containerized applications or Python web applications.

## Configuration

### Environment Variables

List of all supported environment variables and their purposes:

- `FLASK_APP`: Set to `src.web.app`
- `FLASK_ENV`: `development` or `production`
- `FLASK_DEBUG`: `1` for debug mode, `0` for production
- `SECRET_KEY`: Secret key for session encryption
- `UPLOAD_FOLDER`: Directory for file uploads
- `MAX_CONTENT_LENGTH`: Maximum upload file size in bytes
- `LOG_LEVEL`: Logging verbosity (`INFO`, `WARNING`, `ERROR`)
- `GUNICORN_*` variables: Gunicorn server configuration

### Configuration Files

Description of key configuration files:

- `src/web/config/flask_config.py`: Flask application configuration
- `src/web/config/web_interface_config.json`: Web interface settings
- `src/web/config/upload_config.json`: File upload settings
- `src/web/gunicorn.conf.py`: Gunicorn WSGI server configuration

## Security Considerations

Important security considerations for production deployment:

- Always use HTTPS in production
- Set a strong `SECRET_KEY` environment variable
- Configure proper file upload restrictions
- Implement rate limiting
- Use a non-root user in Docker containers
- Keep dependencies updated
- Enable CSRF protection
- Configure Content Security Policy

## Performance Tuning

Guidelines for optimizing performance:

- Adjust Gunicorn worker count based on available CPU cores
- Configure appropriate timeouts
- Implement caching if needed
- Monitor memory usage and adjust resource limits
- Use a CDN for static assets in high-traffic scenarios

## Monitoring and Logging

Recommendations for monitoring and logging:

- Configure appropriate log levels
- Set up log rotation
- Implement health checks
- Monitor resource usage
- Set up alerts for error conditions

## Backup and Recovery

Guidelines for backup and recovery:

- Regularly back up configuration files
- Implement data volume backups for Docker deployments
- Document recovery procedures
- Test restoration processes

## Troubleshooting

Common issues and their solutions:

- Web server connection issues
- File permission problems
- Memory limitations
- Docker networking issues
- Configuration errors

## Deployment Checklist

Pre-deployment checklist for production:

- Security settings verified
- Environment variables configured
- File permissions set correctly
- HTTPS configured
- Resource limits appropriate
- Monitoring in place
- Backup procedures documented

## Code Examples

### Development Server

```bash
# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
FLASK_APP=src.web.app FLASK_ENV=development python -m src.web.run
```

### Gunicorn Production Server

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
FLASK_APP=src.web.app FLASK_ENV=production gunicorn --config src.web.gunicorn.conf.py src.web.wsgi:application
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Docker Production

```bash
# Build and run production containers
docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d --build
```

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## References

| Reference | URL |
| --- | --- |
| Flask Deployment Options | https://flask.palletsprojects.com/en/2.3.x/deploying/ |
| Gunicorn Documentation | https://docs.gunicorn.org/en/stable/ |
| Docker Compose Documentation | https://docs.docker.com/compose/ |
| OWASP Web Security Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Web_Application_Security_Testing_Cheat_Sheet.html |