#!/bin/bash

# Set up the environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install fastapi uvicorn vosk

# Define the model directory
#TODO
MODEL_DIR="kz model"

if [ ! -d "$MODEL_DIR" ]; then
    echo "Model directory $MODEL_DIR not found."
    exit 1
fi

# Create necessary directories
mkdir -p uploads

# Start the FastAPI server
uvicorn server:app --host 0.0.0.0 --port 8000
