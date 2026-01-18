#!/bin/zsh

# Start the Retro Games API
# This script starts the FastAPI server for the retro games catalog

set -e

PROJ_DIR="$(cd "$(dirname "$0")" && pwd)"
API_DIR="$PROJ_DIR/retro-games-api"
VENV_DIR="$API_DIR/.venv"

echo "Starting Retro Games API..."
echo "Project Directory: $PROJ_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    cd "$API_DIR"
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

cd "$API_DIR"

# Install requirements only if not already installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Dependencies already installed"
fi

# Start the API server
python3 -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
