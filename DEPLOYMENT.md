# Deployment Guide for ClassPlus Decoder

This guide covers multiple deployment options for the ClassPlus Decoder application.

## Prerequisites

- Python 3.8+ installed
- Git installed
- Access to Gmail account with App Password
- ClassPlus account access

## Option 1: Local Development Deployment

### 1. Clone and Setup
```bash
git clone <repository-url>
cd classplus-decoder
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your email credentials
```

### 5. Start Development Server
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Option 2: Production Deployment with Gunicorn

### 1. Setup (same as local)
```bash
git clone <repository-url>
cd classplus-decoder
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env file
```

### 2. Start Production Server
```bash
# Using the startup script
./start.sh prod

# Or manually
gunicorn -c gunicorn.conf.py main:app
```

### 3. Using the Startup Script
```bash
./start.sh help          # Show all commands
./start.sh prod          # Start production server
./start.sh status        # Check server status
./start.sh stop          # Stop server
./start.sh logs          # Show logs
```

## Option 3: Systemd Service Deployment

### 1. Setup Application
```bash
# Follow steps 1-4 from Option 2
```

### 2. Install Systemd Service
```bash
# Copy service file to systemd directory
sudo cp classplus-decoder.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable classplus-decoder
sudo systemctl start classplus-decoder

# Check status
sudo systemctl status classplus-decoder
```

### 3. Service Management
```bash
sudo systemctl start classplus-decoder      # Start service
sudo systemctl stop classplus-decoder       # Stop service
sudo systemctl restart classplus-decoder    # Restart service
sudo systemctl status classplus-decoder     # Check status
sudo journalctl -u classplus-decoder -f     # View logs
```

## Option 4: Docker Deployment

### 1. Build and Run with Docker
```bash
# Build image
docker build -t classplus-decoder .

# Run container
docker run -d \
  --name classplus-decoder \
  -p 5000:5000 \
  --env-file .env \
  classplus-decoder
```

### 2. Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Docker Management
```bash
# View running containers
docker ps

# View logs
docker logs classplus-decoder

# Stop container
docker stop classplus-decoder

# Remove container
docker rm classplus-decoder
```

## Option 5: Nginx Reverse Proxy Setup

### 1. Install Nginx
```bash
sudo apt update
sudo apt install nginx
```

### 2. Configure Nginx
Create `/etc/nginx/sites-available/classplus-decoder`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/classplus-decoder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Configuration

### Required Variables
```env
# Email accounts for auto-token generation
EMAIL_ACCOUNTS=email1:password1,email2:password2

# Flask configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
```

### Optional Variables
```env
# Redis for rate limiting (if using Redis)
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
```

## Security Considerations

### 1. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP (if using Nginx)
sudo ufw allow 443/tcp     # HTTPS (if using SSL)
sudo ufw enable
```

### 2. SSL/TLS Setup (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Rate Limiting
The application includes built-in rate limiting:
- `/api/decode`: 10 requests per minute
- `/api/get-keys`: 5 requests per minute

## Monitoring and Logging

### 1. Application Logs
```bash
# If using systemd
sudo journalctl -u classplus-decoder -f

# If using Docker
docker logs -f classplus-decoder

# If using startup script
./start.sh logs
```

### 2. System Monitoring
```bash
# Check system resources
htop
df -h
free -h

# Check application status
curl -s http://localhost:5000/ | grep -i "classplus"
```

### 3. Health Checks
```bash
# Test API endpoints
python3 test_api.py

# Manual health check
curl -f http://localhost:5000/
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **Permission Denied**
   ```bash
   sudo chown -R $USER:$USER /workspace
   chmod +x start.sh
   ```

3. **Environment Variables Not Loading**
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # Verify file permissions
   cat .env
   ```

4. **Dependencies Issues**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Performance Tuning

1. **Gunicorn Workers**
   ```bash
   # Adjust workers based on CPU cores
   workers = (2 x num_cores) + 1
   ```

2. **Database Connection Pooling** (if applicable)
   ```bash
   # Add to gunicorn.conf.py
   worker_connections = 1000
   max_requests = 1000
   ```

## Backup and Recovery

### 1. Application Backup
```bash
# Backup application files
tar -czf classplus-decoder-backup-$(date +%Y%m%d).tar.gz \
  --exclude=venv \
  --exclude=__pycache__ \
  --exclude=*.pyc \
  .
```

### 2. Environment Backup
```bash
# Backup environment file
cp .env .env.backup.$(date +%Y%m%d)
```

### 3. Recovery
```bash
# Restore from backup
tar -xzf classplus-decoder-backup-YYYYMMDD.tar.gz
cp .env.backup.YYYYMMDD .env
```

## Updates and Maintenance

### 1. Application Updates
```bash
# Pull latest changes
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart classplus-decoder
```

### 2. System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Restart application after system updates
sudo systemctl restart classplus-decoder
```

## Support

For issues and support:
1. Check the logs first
2. Review this deployment guide
3. Check the main README.md
4. Review application error messages
5. Check system resources and permissions