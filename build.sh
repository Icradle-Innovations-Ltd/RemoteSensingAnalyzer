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
    libspatialindex-dev \
    proj-bin \
    libproj-dev \
    cmake \
    g++

# Print GDAL and PROJ versions
echo "GDAL version:"
gdal-config --version
echo "PROJ version:"
proj --version

# Set environment variables
export CPLUS_INCLUDE_PATH=/usr/include/gdal:/usr/include/proj
export C_INCLUDE_PATH=/usr/include/gdal:/usr/include/proj

# Upgrade pip and install wheel
pip install --upgrade pip
pip install wheel setuptools

# Install pyproj separately with specific version to avoid compilation issues
pip install pyproj==3.2.0

# Install GDAL with the same version as the system
GDAL_VERSION=$(gdal-config --version)
pip install GDAL==${GDAL_VERSION}

# Install the rest of the requirements, excluding pyproj which we already installed
grep -v "pyproj" requirements.txt > requirements_filtered.txt
pip install -r requirements_filtered.txt

echo "Build completed successfully!"#!/usr/bin/env bash
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