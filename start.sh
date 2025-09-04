#!/bin/bash

# ClassPlus Decoder Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please edit .env file with your email credentials before starting the application."
        exit 1
    else
        print_error ".env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# Function to start development server
start_dev() {
    print_status "Starting development server..."
    python app.py
}

# Function to start production server
start_prod() {
    print_status "Starting production server with Gunicorn..."
    gunicorn -c gunicorn.conf.py main:app
}

# Function to stop server
stop_server() {
    print_status "Stopping server..."
    pkill -f "gunicorn.*main:app" || true
    pkill -f "python.*app.py" || true
    print_status "Server stopped."
}

# Function to show status
show_status() {
    if pgrep -f "gunicorn.*main:app" > /dev/null; then
        print_status "Production server is running (Gunicorn)"
    elif pgrep -f "python.*app.py" > /dev/null; then
        print_status "Development server is running (Python)"
    else
        print_status "No server is currently running"
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing recent logs..."
    journalctl -u classplus-decoder -f --no-pager 2>/dev/null || echo "No systemd service logs found"
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev     Start development server"
    echo "  prod    Start production server with Gunicorn"
    echo "  stop    Stop running server"
    echo "  status  Show server status"
    echo "  logs    Show server logs"
    echo "  help    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev      # Start development server"
    echo "  $0 prod     # Start production server"
    echo "  $0 stop     # Stop server"
}

# Main script logic
case "${1:-dev}" in
    "dev")
        start_dev
        ;;
    "prod")
        start_prod
        ;;
    "stop")
        stop_server
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac