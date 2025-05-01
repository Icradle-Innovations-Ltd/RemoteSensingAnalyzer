#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install system dependencies
apt-get update -y
apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    gdal-bin \
    libgdal-dev \
    libspatialindex-dev

# Print GDAL version
gdal-config --version

# Set GDAL environment variables
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install GDAL with the same version as the system
GDAL_VERSION=$(gdal-config --version)
pip install GDAL==${GDAL_VERSION}

echo "Build completed successfully!"