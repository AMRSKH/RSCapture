#!/bin/bash
# Script to set up a virtual environment and run the RSCapture application.

# Ensure python3 and pip are installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Please install Python3."
    exit 1
fi

if ! command -v pip3 &> /dev/null
then
    echo "pip3 is not installed. Please install pip3."
    exit 1
fi

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null
then
    echo "FFmpeg is not installed. Please install FFmpeg for screen recording functionality."
    echo "You can typically install it using: sudo apt install ffmpeg"
    exit 1
fi


VENV_DIR="rscapture_env"

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Run the application
echo "Starting RSCapture..."
python3 main.py

# Deactivate the virtual environment when done (optional, can be manually done later)
# deactivate
echo "RSCapture finished."
