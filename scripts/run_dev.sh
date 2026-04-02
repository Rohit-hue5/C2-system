#!/bin/bash

echo "[*] Starting C2Lab (DEV MODE)"

export FLASK_ENV=development
export FLASK_DEBUG=true

python app.py
