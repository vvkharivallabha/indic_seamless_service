#!/bin/bash

# Activate script for Indic Seamless Service
# This script activates the conda environment

ENV_NAME="indic-seamless"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please run setup.sh first."
    exit 1
fi

# Initialize conda if needed
if ! conda info --base &> /dev/null; then
    eval "$(conda shell.bash hook)"
fi

# Check if environment exists
if ! conda env list | grep -q "^${ENV_NAME} "; then
    echo "❌ Environment '${ENV_NAME}' not found. Please run setup.sh first."
    exit 1
fi

echo "🔧 Activating conda environment '${ENV_NAME}'..."
conda activate "${ENV_NAME}"

echo "✅ Environment activated!"
echo "💡 To deactivate later, run: conda deactivate" 