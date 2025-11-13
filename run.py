#!/usr/bin/env python3
"""
Simple script to run the Appointment Scheduler web app
"""

from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("    APPOINTMENT SCHEDULER WEB APP")
    print("=" * 60)
    print("Starting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
