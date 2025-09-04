.PHONY: help install test run dev prod stop clean docker-build docker-run docker-stop

# Default target
help:
	@echo "ClassPlus Decoder - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     Install dependencies"
	@echo "  test        Run tests"
	@echo "  dev         Start development server"
	@echo "  run         Start production server"
	@echo "  stop        Stop running server"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container"
	@echo "  docker-stop  Stop Docker container"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean       Clean up temporary files"
	@echo "  logs        Show application logs"
	@echo "  status      Show server status"

# Install dependencies
install:
	@echo "Installing dependencies..."
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Dependencies installed successfully!"

# Run tests
test:
	@echo "Running tests..."
	. venv/bin/activate && python3 test_api.py

# Start development server
dev:
	@echo "Starting development server..."
	. venv/bin/activate && python3 app.py

# Start production server
run:
	@echo "Starting production server..."
	. venv/bin/activate && gunicorn -c gunicorn.conf.py main:app

# Stop server
stop:
	@echo "Stopping server..."
	pkill -f "gunicorn.*main:app" || true
	pkill -f "python.*app.py" || true
	@echo "Server stopped."

# Show logs
logs:
	@echo "Showing logs..."
	@if pgrep -f "gunicorn.*main:app" > /dev/null; then \
		echo "Production server logs:"; \
		journalctl -u classplus-decoder -f --no-pager 2>/dev/null || echo "No systemd logs found"; \
	elif pgrep -f "python.*app.py" > /dev/null; then \
		echo "Development server is running. Check terminal for logs."; \
	else \
		echo "No server is running."; \
	fi

# Show status
status:
	@echo "Server status:"
	@if pgrep -f "gunicorn.*main:app" > /dev/null; then \
		echo "✓ Production server is running (Gunicorn)"; \
	elif pgrep -f "python.*app.py" > /dev/null; then \
		echo "✓ Development server is running (Python)"; \
	else \
		echo "✗ No server is currently running"; \
	fi

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	@echo "Cleanup completed!"

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t classplus-decoder .

docker-run:
	@echo "Running Docker container..."
	docker run -d --name classplus-decoder -p 5000:5000 --env-file .env classplus-decoder

docker-stop:
	@echo "Stopping Docker container..."
	docker stop classplus-decoder || true
	docker rm classplus-decoder || true

# Quick start for development
quick-start: install
	@echo "Quick start completed!"
	@echo "Run 'make dev' to start development server"
	@echo "Run 'make run' to start production server"