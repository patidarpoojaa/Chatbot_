"""
Production server using Waitress (cross-platform, works on Windows).
Run with: python serve.py
"""
from waitress import serve
from app import app
from config import Config

if __name__ == "__main__":
    print(f"Starting production server on http://0.0.0.0:{Config.PORT}")
    serve(app, host="0.0.0.0", port=Config.PORT, threads=4)
