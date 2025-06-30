#!/bin/bash

# Setup script for Indic Seamless Service
# This script creates a conda environment and installs dependencies

set -e  # Exit on any error

echo "🚀 Setting up Indic Seamless Service..."

# Configuration
ENV_NAME="indic-seamless"
PYTHON_VERSION="3.10"

# Check if conda is available, if not install Miniconda
if ! command -v conda &> /dev/null; then
    # Check if Miniconda is already installed but not in PATH
    if [ -d "$HOME/miniconda3" ]; then
        echo "✅ Miniconda found at $HOME/miniconda3 but not in PATH"
        echo "🔧 Adding Miniconda to PATH..."
        export PATH="$HOME/miniconda3/bin:$PATH"
        
        # Initialize conda for current session
        eval "$($HOME/miniconda3/bin/conda shell.bash hook)"
    else
        echo "📦 Conda not found. Installing Miniconda..."
        
        # Detect system architecture
        ARCH=$(uname -m)
        if [ "$ARCH" = "x86_64" ]; then
            CONDA_ARCH="x86_64"
        elif [ "$ARCH" = "aarch64" ]; then
            CONDA_ARCH="aarch64"
        else
            echo "❌ Unsupported architecture: $ARCH"
            exit 1
        fi
        
        # Download and install Miniconda
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-${CONDA_ARCH}.sh"
        MINICONDA_INSTALLER="/tmp/miniconda_installer.sh"
        
        echo "⬇️  Downloading Miniconda..."
        if ! curl -L "$MINICONDA_URL" -o "$MINICONDA_INSTALLER"; then
            echo "❌ Failed to download Miniconda. Please check your internet connection."
            exit 1
        fi
        
        echo "🔧 Installing Miniconda..."
        if ! bash "$MINICONDA_INSTALLER" -b -p "$HOME/miniconda3"; then
            echo "❌ Failed to install Miniconda."
            rm -f "$MINICONDA_INSTALLER"
            exit 1
        fi
        
        # Clean up installer
        rm -f "$MINICONDA_INSTALLER"
        
        # Add conda to PATH for current session
        export PATH="$HOME/miniconda3/bin:$PATH"
        
        # Initialize conda for bash
        "$HOME/miniconda3/bin/conda" init bash
        
        echo "✅ Miniconda installed successfully!"
        echo "💡 Please restart your terminal or run: source ~/.bashrc"
        echo "   Then run this setup script again."
        exit 0
    fi
else
    echo "✅ Conda is already installed"
    # Initialize conda for current session if not already done
    if ! conda info --base &> /dev/null; then
        eval "$(conda shell.bash hook)"
    fi
fi

# Check if environment already exists
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "✅ Conda environment '${ENV_NAME}' already exists"
    echo "🔧 Activating existing environment..."
    conda activate "${ENV_NAME}"
else
    echo "🔧 Creating conda environment '${ENV_NAME}' with Python ${PYTHON_VERSION}..."
    conda create -n "${ENV_NAME}" python="${PYTHON_VERSION}" -y
    echo "🔧 Activating environment..."
    conda activate "${ENV_NAME}"
fi

# Upgrade pip and install pip-tools
echo "⬆️  Upgrading pip and installing pip-tools..."
pip install --upgrade pip pip-tools

# Install dependencies
echo "🔧 Installing dependencies..."
cd "$(dirname "$0")"  # Change to the directory where this script is located
pip install -r requirements.txt

echo "✅ Environment setup complete!"

echo ""
echo "🎉 Setup complete! To activate the environment, run:"
echo "   conda activate ${ENV_NAME}"
echo ""
echo "📚 Next steps:"
echo "   - Start the service: python start_service.py"
echo "   - Test the service: python tests/workflow_test.py"
echo ""
echo "💡 To deactivate the environment later, run: conda deactivate" 