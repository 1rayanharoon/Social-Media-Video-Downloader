#!/bin/bash

# Install system dependencies for yt-dlp
apt-get update && apt-get install -y ffmpeg

# Start the application
python main.py
