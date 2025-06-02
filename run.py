#!/usr/bin/env python3
"""
Simple run script for XChange Updater
"""
from app import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting XChange Updater on port {port}")
    print(f"Debug mode: {debug}")
    print(f"OpenAPI spec available at: http://localhost:{port}/openapi.json")
    
    app.run(debug=debug, host='0.0.0.0', port=port)