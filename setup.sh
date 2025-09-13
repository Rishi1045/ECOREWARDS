#!/bin/bash
set -e

# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev

# Install Python dependencies
pip install -r backend/requirements.txt

# Create necessary directories
mkdir -p backend/static/uploads
mkdir -p backend/static/results

# Set environment variables
export FLASK_APP=backend/app.py
export FLASK_ENV=production
export PYTHONPATH=$PYTHONPATH:$(pwd)
