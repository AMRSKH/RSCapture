#!/bin/bash
# Script to set up a virtual environment and run the RSCapture application.

# Exit immediately if a command exits with a non-zero status.
set -e

# Ensure python3 and pip are installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python3 is not installed. Please install Python3."
    exit 1
fi

if ! command -v pip3 &> /dev/null
then
    echo "Error: pip3 is not installed. Please install pip3."
    exit 1
fi

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null
then
    echo "Error: FFmpeg is not installed. Please install FFmpeg for screen recording functionality."
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

# --- Diagnostic Steps Start ---
echo "--- Diagnostic Information ---"
echo "Current Python executable: $(which python3)"
echo "Current Pip executable: $(which pip)"
echo "--- End Diagnostic Information ---"
# --- Diagnostic Steps End ---

# Clear pip cache (good practice to avoid stale cache issues)
echo "Clearing pip cache..."
pip cache purge || true # '|| true' to prevent script from exiting if purge fails for some reason

# Install dependencies from requirements.txt
echo "Checking and installing missing dependencies from requirements.txt..."
pip install -r requirements.txt

# --- Diagnostic Step 2 ---
echo "--- Installed Packages After pip install ---"
pip list
echo "------------------------------------------"
# --- End Diagnostic Step 2 ---

# Run the application
echo "Starting RSCapture..."
python3 main.py

# Deactivate the virtual environment when done (optional, can be manually done later)
# deactivate
echo "RSCapture finished."
