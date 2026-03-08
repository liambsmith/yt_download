#!/bin/bash
# YouTube Video Downloader - Environment Setup Script

set -e

ENV_NAME="yt-dl"

echo "🔧 Setting up YouTube Video Downloader environment..."
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Error: conda is not installed or not in PATH"
    echo "Please install Anaconda or Miniconda first."
    exit 1
fi

# Check if environment already exists
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "⚠️  Environment '${ENV_NAME}' already exists."
    read -p "Do you want to recreate it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping environment creation."
    else
        echo "Removing existing environment..."
        conda env remove -n ${ENV_NAME} -y
    fi
fi

echo "📦 Creating conda environment with Python 3.14..."
conda create -n ${ENV_NAME} python=3.14 -y

echo "🎬 Installing FFmpeg..."
conda install -c conda-forge ffmpeg -y -n ${ENV_NAME}

echo "📥 Installing yt-dlp..."
conda run -n ${ENV_NAME} pip install yt-dlp

echo "🧪 Installing testing dependencies..."
conda run -n ${ENV_NAME} pip install pytest pytest-cov

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  conda activate ${ENV_NAME}"
echo ""
echo "Then run the downloader:"
echo "  python download.py"
echo ""
