#!/usr/bin/env python3
"""Run the Flask application."""

import os

from app import create_app

# Create app with environment-based configuration
config_name = os.getenv("FLASK_ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
