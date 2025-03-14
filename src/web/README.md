# JSON to Excel Conversion Tool - Web Interface

![Flask](https://img.shields.io/badge/Flask-2.3.0+-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)

A browser-based interface for the JSON to Excel Conversion Tool, providing an intuitive way to upload JSON files, configure conversion options, and download the resulting Excel files.

## Key Features

- Clean, minimalist web interface for non-technical users
- Drag-and-drop file upload with validation
- Real-time conversion progress tracking
- Configurable conversion options
- Secure file handling and error management
- Responsive design for desktop and mobile devices

![Upload Page](../docs/images/web-upload.png)
![Conversion Progress](../docs/images/web-progress.png)
![Results Page](../docs/images/web-results.png)

## Introduction

The web interface component of the JSON to Excel Conversion Tool provides a user-friendly browser-based experience for converting JSON files to Excel format. This interface is designed for users who prefer a graphical approach over command-line tools, making the conversion process accessible to non-technical users.

The web interface offers all the core functionality of the command-line tool with an intuitive user experience, including drag-and-drop file upload, visual progress tracking, and simple download of converted files.

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Core JSON to Excel conversion components

### Installation Methods

#### 1. Install with Web Interface Option

```bash
# Install the package with web interface support
pip install json-to-excel-converter[web]
```

#### 2. Install from Source

```bash
# Clone the repository
git clone https://github.com/organization/json-to-excel-converter.git
cd json-to-excel-converter

# Install with web dependencies
pip install -e ".[web]"
```

### Verifying Installation

After installation, you can verify that the web interface is properly installed by running:

```bash
json2excel-web --version
```

## Configuration

The web interface can be configured through environment variables, command-line arguments, or a configuration file.

### Configuration File

Create a file named `web_config.json` in your working directory or specify a path with the `--config` option:

```json
{
  "web_interface": {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": false,
    "upload_folder": "./uploads",
    "max_upload_size": 5242880,
    "allowed_extensions": ["json"],
    "session_secret": "change-this-secret-key"
  },
  "conversion": {
    "default_sheet_name": "Sheet1",
    "array_handling": "expand"
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JSON2EXCEL_WEB_HOST` | Host address to bind | 127.0.0.1 |
| `JSON2EXCEL_WEB_PORT` | Port to listen on | 5000 |
| `JSON2EXCEL_WEB_DEBUG` | Enable debug mode | false |
| `JSON2EXCEL_UPLOAD_FOLDER` | Directory for uploaded files | ./uploads |
| `JSON2EXCEL_MAX_UPLOAD_SIZE` | Maximum upload size in bytes | 5242880 (5MB) |
| `JSON2EXCEL_SESSION_SECRET` | Secret key for sessions | None (required) |

### Command-Line Options

```bash
json2excel-web --host 0.0.0.0 --port 8080 --upload-folder ./data/uploads
```

Run `json2excel-web --help` for a complete list of options.

## Usage

### Starting the Web Server

```bash
# Start with default settings
json2excel-web

# Start with custom port
json2excel-web --port 8080

# Start with custom host (accessible from other machines)
json2excel-web --host 0.0.0.0
```

Once started, the web interface will be available at `http://localhost:5000` (or your configured host/port).

### Converting JSON to Excel

1. **Access the Web Interface**
   
   Open your web browser and navigate to the server address (default: `http://localhost:5000`).

2. **Upload a JSON File**
   
   - Click the upload area or drag and drop a JSON file
   - The file will be validated to ensure it's a valid JSON file

3. **Configure Conversion Options**
   
   - **Sheet Name**: Customize the name of the Excel worksheet
   - **Array Handling**: Choose how JSON arrays should be handled
     - Expand arrays into rows (default)
     - Join arrays as text

4. **Start Conversion**
   
   Click the "Convert to Excel" button to begin the conversion process.

5. **Monitor Progress**
   
   The interface will display the conversion progress in real-time.

6. **Download Result**
   
   Once conversion is complete, click "Download Excel File" to save the result.

### File Size Limitations

By default, uploads are limited to 5MB. For larger files, consider:

- Adjusting the `max_upload_size` configuration
- Using the command-line tool for very large files
- Splitting your JSON file into smaller chunks

## Development

### Project Structure

```
src/web/
├── __init__.py          # Package initialization
├── app.py               # Main Flask application
├── config.py            # Configuration handling
├── converters/          # Conversion interface modules
├── routes/              # API and page routes
├── static/              # CSS, JavaScript, images
│   ├── css/
│   ├── js/
│   └── images/
├── templates/           # Jinja2 HTML templates
├── utils/               # Utility functions
└── tests/               # Web interface tests
```

### Setting Up Development Environment

1. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Development Dependencies**

   ```bash
   pip install -e ".[web,dev]"
   ```

3. **Run in Debug Mode**

   ```bash
   json2excel-web --debug
   ```

### Frontend Technologies

- HTML5, CSS3, JavaScript (ES6+)
- [Bootstrap 5](https://getbootstrap.com/) for responsive design
- [Dropzone.js](https://www.dropzonejs.com/) for drag-and-drop file uploads
- [Axios](https://axios-http.com/) for AJAX requests
- [Font Awesome](https://fontawesome.com/) for icons

### Testing

Run the web interface tests with:

```bash
pytest src/web/tests/
```

### Building Frontend Assets

If you make changes to CSS or JavaScript files, you may need to rebuild them:

```bash
# If using npm
npm install
npm run build

# If using yarn
yarn install
yarn build
```

## Security

### Implemented Security Measures

- **File Upload Validation**: Strict checking of file types and sizes
- **CSRF Protection**: Cross-Site Request Forgery prevention with Flask-WTF
- **Secure File Handling**: Secure generation of filenames and paths
- **Content Security Policy**: Restrictions on resource loading
- **XSS Protection**: Proper escaping of user-provided content
- **Rate Limiting**: Prevention of abuse through request limiting

### Security Considerations

- The web interface is designed for internal use or trusted environments
- For public-facing deployments, additional security measures are recommended:
  - Use HTTPS with a proper SSL certificate
  - Implement user authentication
  - Place behind a reverse proxy (Nginx, Apache)
  - Configure appropriate firewalls and access controls

## API Reference

The web interface provides RESTful API endpoints for programmatic interaction.

### Endpoints

#### File Upload

```
POST /api/upload
```

Parameters:
- `file`: The JSON file to upload (multipart/form-data)

Response:
```json
{
  "status": "success",
  "file_id": "abc123def456",
  "filename": "data.json",
  "size": 1234
}
```

#### Conversion

```
POST /api/convert
```

Parameters:
- `file_id`: ID of the previously uploaded file
- `sheet_name`: Name for the Excel worksheet (optional)
- `array_handling`: How to handle arrays: "expand" or "join" (optional)

Response:
```json
{
  "status": "success",
  "job_id": "job789xyz",
  "estimated_time": 2
}
```

#### Conversion Status

```
GET /api/status/<job_id>
```

Response:
```json
{
  "status": "completed",
  "progress": 100,
  "result_id": "result456abc",
  "download_url": "/download/result456abc"
}
```

#### Download Result

```
GET /download/<result_id>
```

Returns the Excel file as an attachment.

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "File too large" error | Increase `max_upload_size` in configuration |
| "Invalid JSON" error | Verify your JSON syntax with a validator |
| Server won't start | Check if the port is already in use |
| Slow conversion for large files | Consider using the CLI version for very large files |
| "Permission denied" error | Ensure the upload directory is writable |
| No conversion result | Check server logs for detailed error messages |

### Debug Mode

For troubleshooting, you can enable debug mode:

```bash
json2excel-web --debug
```

This will provide detailed error information in the browser.

### Logs

Logs are written to the console by default. To save logs to a file, use:

```bash
json2excel-web --log-file web-interface.log
```

### Getting Help

If you encounter issues not covered here:

1. Check the full documentation at [https://json-to-excel-converter.readthedocs.io/](https://json-to-excel-converter.readthedocs.io/)
2. Report issues on our [GitHub repository](https://github.com/organization/json-to-excel-converter/issues)
3. Contact support at support@json-to-excel-converter.org