#!/bin/bash

# Strom AI Assistant Runner Script
# This script activates the virtual environment and runs the audio setup test

echo "=========================================="
echo "  STROM AI ASSISTANT - RUNNER SCRIPT"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv"
    exit 1
clestrfi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/Scripts/activate

# Check if activation was successful
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "✅ Virtual environment activated"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Run audio setup test
echo ""
echo "🎤 Running audio setup test..."
python test_audio_setup.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "🚀 Starting Strom AI Assistant..."
    python main.py
else
    echo ""
    echo "❌ Tests failed. Please check audio setup."
    exit 1
fi

# Deactivate virtual environment
deactivate