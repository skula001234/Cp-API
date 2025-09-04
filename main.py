from app import app

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Production server (gunicorn)
    # Run with: gunicorn --bind 0.0.0.0:5000 main:app
    pass
