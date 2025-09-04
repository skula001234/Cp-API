# Quick Start Guide

Get the ClassPlus Decoder up and running in 5 minutes!

## 🚀 Super Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd classplus-decoder
```

### 2. One-Command Setup
```bash
make quick-start
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Gmail credentials
```

### 4. Start Development Server
```bash
make dev
```

🎉 **Done!** Your app is running at `http://localhost:5000`

## 🔧 Manual Setup (if needed)

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Start Server
```bash
python app.py
```

## 📱 Using the Application

1. **Open your browser** and go to `http://localhost:5000`
2. **Enter your ClassPlus token** (old tokens work too!)
3. **Paste the encrypted URL** you want to decode
4. **Click "Decode and Play"** - the app will automatically:
   - Validate your token
   - Generate a new one if needed
   - Decode the URL
   - Show the video player

## 🎯 Key Features

- **Auto-token generation** when old tokens expire
- **Smart URL decoding** with fallback mechanisms
- **DRM key extraction** for video downloading
- **Rate limiting** to prevent abuse
- **Error handling** with helpful messages

## 🆘 Need Help?

- **Check logs**: `make logs`
- **View status**: `make status`
- **Run tests**: `make test`
- **Full docs**: See `README.md` and `DEPLOYMENT.md`

## 🚀 Production Deployment

Ready for production? Use one of these:

```bash
# Production server
make run

# Docker deployment
make docker-build
make docker-run

# Systemd service
sudo cp classplus-decoder.service /etc/systemd/system/
sudo systemctl enable classplus-decoder
sudo systemctl start classplus-decoder
```

## 📋 Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Gmail account with App Password
- [ ] ClassPlus account access
- [ ] Network access to ClassPlus API

## 🔐 Gmail App Password Setup

1. Enable 2-factor authentication on your Gmail
2. Go to Google Account → Security → App passwords
3. Generate password for "Mail"
4. Use this password in your `.env` file

---

**That's it!** Your ClassPlus Decoder is ready to use. 🎉