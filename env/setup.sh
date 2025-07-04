#!/bin/bash

# Setup script for Indic Seamless Service
# This script uses uv for both virtual environment and package management

set -e  # Exit on any error

echo "🚀 Setting up Indic Seamless Service with uv..."

# Configuration
ENV_NAME="indic-seamless"
PYTHON_VERSION="3.10"

# Load environment variables from .env if it exists
if [ -f "../.env" ]; then
    echo "📝 Loading environment variables from .env file..."
    set -a  # Automatically export all variables
    source "../.env"
    set +a  # Turn off automatic export
    echo "✅ Environment variables loaded"
elif [ -f ".env" ]; then
    echo "📝 Loading environment variables from .env file..."
    set -a  # Automatically export all variables
    source ".env"
    set +a  # Turn off automatic export
    echo "✅ Environment variables loaded"
else
    echo "💡 No .env file found. You can create one from env.example for custom configuration."
fi

# Install uv if not available
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    # Install uv using the official installer
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"
    
    # Verify installation
    if command -v uv &> /dev/null; then
        echo "✅ uv installed successfully!"
        uv --version
    else
        echo "❌ uv installation failed. Please install manually:"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
        exit 1
    fi
else
    echo "✅ uv is already installed"
    uv --version
fi

# Ensure uv is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Change to the directory where this script is located
cd "$(dirname "$0")"

# Create virtual environment with uv
echo "🔧 Creating Python ${PYTHON_VERSION} virtual environment with uv..."
if [ -d ".venv" ]; then
    echo "✅ Virtual environment already exists"
else
    echo "📦 Creating new virtual environment..."
    uv venv .venv --python ${PYTHON_VERSION}
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Verify Python version
echo "🐍 Using Python: $(python --version)"
echo "📍 Python location: $(which python)"

# Install dependencies with uv (super fast!)
echo "⚡ Installing dependencies with uv..."

# Try to install from pyproject.toml first (modern approach)
if [ -f "../pyproject.toml" ]; then
    echo "📦 Installing from pyproject.toml..."
    # Save current directory
    ORIGINAL_DIR=$(pwd)
    cd ..
    if uv pip install -e .; then
        echo "✅ All dependencies installed successfully from pyproject.toml!"
        # Return to the original directory
        cd "$ORIGINAL_DIR"
    else
        echo "⚠️  pyproject.toml installation failed, trying requirements.txt..."
        # Return to the original directory first
        cd "$ORIGINAL_DIR"
        uv pip install -r requirements.txt
    fi
elif [ -f "requirements.txt" ]; then
    echo "📦 Installing from requirements.txt..."
    if uv pip install -r requirements.txt; then
        echo "✅ All dependencies installed successfully from requirements.txt!"
    else
        echo "⚠️  Some dependencies failed. Trying essential packages..."
        
        # Install essential packages individually
        ESSENTIAL_PACKAGES=(
            "torch==2.7.1"
            "torchaudio==2.7.1"
            "transformers==4.53.1"
            "fastapi==0.115.14"
            "uvicorn[standard]==0.35.0"
            "python-multipart==0.0.20"
            "librosa==0.11.0"
            "numpy==1.26.4"
            "requests==2.32.4"
            "huggingface-hub==0.33.2"
        )
        
        echo "🔧 Installing essential packages..."
        for package in "${ESSENTIAL_PACKAGES[@]}"; do
            echo "Installing $package..."
            if uv pip install "$package"; then
                echo "✅ $package installed successfully"
            else
                echo "❌ Failed to install $package - continuing with others..."
            fi
        done
    fi
else
    echo "❌ No requirements.txt or pyproject.toml found!"
    exit 1
fi

# Check for Hugging Face authentication
echo "🔍 Checking Hugging Face authentication..."

# Check if HF_TOKEN is set via environment variable
if [ -n "$HF_TOKEN" ]; then
    echo "🔑 HF_TOKEN found in environment variables"
    echo "🔧 Setting up HuggingFace authentication..."
    
    # Set the token for huggingface-hub
    export HUGGINGFACE_HUB_TOKEN="$HF_TOKEN"
    
    # Test authentication
    if python -c "
import os
os.environ['HF_TOKEN'] = '$HF_TOKEN'
from huggingface_hub import HfApi
try:
    user = HfApi().whoami()
    print('✅ HuggingFace authentication successful!')
    print(f'   Logged in as: {user[\"name\"]}')
except Exception as e:
    print(f'❌ HuggingFace authentication failed: {e}')
    exit(1)
    " 2>/dev/null; then
        echo "✅ HuggingFace authentication is working"
    else
        echo "⚠️  HuggingFace authentication failed with provided token"
        echo "💡 Please check your HF_TOKEN in the .env file"
    fi
else
    # Check if user is already logged in via huggingface-cli
    if python -c "from huggingface_hub import HfApi; HfApi().whoami()" 2>/dev/null; then
        echo "✅ Hugging Face authentication is configured via huggingface-cli"
    else
        echo "⚠️  Hugging Face authentication not configured"
        echo "💡 The ai4bharat/indic-seamless model is gated and requires authentication."
        echo "   To fix this, choose one of these options:"
        echo ""
        echo "   Option 1: Use .env file (Recommended)"
        echo "   1. Copy env.example to .env: cp env.example .env"
        echo "   2. Get your token from: https://huggingface.co/settings/tokens"
        echo "   3. Edit .env and set: HF_TOKEN=your_token_here"
        echo "   4. Visit: https://huggingface.co/ai4bharat/indic-seamless"
        echo "   5. Request access to the model"
        echo ""
        echo "   Option 2: Use huggingface-cli"
        echo "   1. Run: huggingface-cli login"
        echo "   2. Enter your Hugging Face token"
        echo ""
        echo "   The service will still start but model loading will fail without authentication."
    fi
fi

echo "✅ Environment setup complete!"

echo ""
echo "🎉 Setup complete! To activate the environment, run:"
echo "   cd $(pwd) && source .venv/bin/activate"
echo ""
echo "📚 Next steps:"
echo "   - Activate environment: source env/.venv/bin/activate"
echo "   - Start the service: python start_service.py"
echo "   - Start structured app: python app_structured.py"
echo "   - Test the service: python tests/workflow_test.py"
echo ""
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️  Note: If you encounter model loading issues:"
    echo "   1. Copy env.example to .env: cp env.example .env"
    echo "   2. Get your HuggingFace token from: https://huggingface.co/settings/tokens"
    echo "   3. Edit .env and set: HF_TOKEN=your_token_here"
    echo "   4. Request access to: https://huggingface.co/ai4bharat/indic-seamless"
    echo ""
fi
echo "⚡ Performance: Using uv for 10-100x faster package management!"
echo "💡 To deactivate the environment later, run: deactivate" 