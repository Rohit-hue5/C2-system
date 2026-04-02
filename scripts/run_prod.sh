#!/bin/bash

echo "[*] Starting C2Lab (PRODUCTION MODE)"

export FLASK_ENV=production
export FLASK_DEBUG=false

# Use eventlet for SocketIO
gunicorn -k eventlet -w 1 app:app --bind 0.0.0.0:5000
