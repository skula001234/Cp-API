# ClassPlus Auto Decoder & Key Extractor

A Flask-based web application for automatically decoding ClassPlus encrypted video URLs and extracting DRM keys for video downloading.

## Features

- **Auto Token Generation**: Automatically generates new authentication tokens when old ones expire
- **URL Decoding**: Decodes encrypted ClassPlus video URLs to playable formats
- **DRM Key Extraction**: Extracts Widevine DRM keys for video downloading
- **Smart Fallbacks**: Handles errors gracefully with proper fallback mechanisms
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Modern UI**: Clean, responsive Bootstrap-based interface

## Prerequisites

- Python 3.8+
- Gmail account with App Password (for auto-token generation)
- ClassPlus account access

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd classplus-decoder
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your email credentials
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# Email accounts for auto-token generation
# Format: email1:password1,email2:password2
EMAIL_ACCOUNTS=your_email@gmail.com:your_app_password

# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Optional: Custom secret key for Flask
SECRET_KEY=your-secret-key-here
```

### Gmail App Password Setup

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use this password in your `.env` file

## Usage

### Development Mode

```bash
source venv/bin/activate
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

```bash
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 main:app
```

## API Endpoints

### POST /api/decode
Decodes encrypted video URLs and generates playable URLs.

**Request Body:**
```json
{
  "token": "your_auth_token",
  "encrypted_url": "encrypted_video_url"
}
```

**Response:**
```json
{
  "status": "ok",
  "success": true,
  "url": "playable_video_url",
  "new_token_info": {
    "token": "new_token",
    "generated_by": "email_used"
  },
  "message": "Token was expired, new one generated"
}
```

### POST /api/get-keys
Extracts DRM keys from video URLs.

**Request Body:**
```json
{
  "token": "valid_auth_token",
  "video_url": "decoded_video_url"
}
```

**Response:**
```json
{
  "success": true,
  "data": ["--key key1:value1", "--key key2:value2"],
  "mpd_url": "manifest_url"
}
```

## Project Structure

```
├── app.py                 # Main Flask application
├── main.py               # Entry point for gunicorn
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
├── static/
│   └── app.js          # Frontend JavaScript
├── templates/
│   └── index.html      # Main HTML template
└── utils/
    ├── __init__.py      # Package initialization
    ├── classplus_client.py    # ClassPlus API client
    ├── decoder.py             # URL decoding logic
    ├── drm_manager.py         # DRM key extraction
    └── token_manager.py       # Token generation
```

## How It Works

1. **Token Validation**: The app validates user tokens against ClassPlus API
2. **Auto-Token Generation**: If a token expires, it automatically generates a new one using configured email accounts
3. **URL Decoding**: Encrypted URLs are decoded using base64 and HMAC signatures
4. **DRM Key Extraction**: Uses pywidevine to extract decryption keys from video manifests
5. **Smart Fallbacks**: Handles various error scenarios gracefully

## Security Features

- Rate limiting on API endpoints
- Secure token handling
- Input validation and sanitization
- Error message sanitization for production

## Troubleshooting

### Common Issues

1. **"No email accounts configured"**
   - Ensure your `.env` file has `EMAIL_ACCOUNTS` configured
   - Check that Gmail App Password is correct

2. **"Token validation failed"**
   - Token may be expired
   - Check ClassPlus API status
   - Verify token format

3. **"DRM key extraction failed"**
   - Ensure video URL is properly decoded
   - Check if video has DRM protection
   - Verify token permissions

### Logs

Check application logs for detailed error information:
```bash
tail -f app.log  # If logging to file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes only. Please respect ClassPlus terms of service and use responsibly.

## Disclaimer

This tool is designed to work with ClassPlus educational content that you have legitimate access to. Please ensure you comply with all applicable laws and terms of service.