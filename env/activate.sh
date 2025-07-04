#!/bin/bash
# Quick activation script for the uv virtual environment

# Check if virtual environment exists
if [ ! -f ".venv/bin/activate" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run 'make setup' or './setup.sh' first"
    exit 1
fi

# Activate the virtual environment
source .venv/bin/activate

echo "✅ Virtual environment activated!"
echo "🐍 Python: $(python --version)"
echo "📍 Location: $(which python)"
echo ""
echo "💡 To deactivate, run: deactivate" 