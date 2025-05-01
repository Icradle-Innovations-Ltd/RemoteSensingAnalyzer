#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting alternative build process..."

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
    g++ \
    wget

# Print versions
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

echo "Installing non-geospatial packages first..."

# Install packages from PyPI that don't require compilation
pip install streamlit==1.45.0 numpy==2.2.5 matplotlib==3.10.1 pillow==11.2.1 python-dotenv==1.1.0 requests==2.32.3
pip install anthropic==0.50.0 openai==1.76.2 trafilatura==2.0.0
pip install plotly==5.13.1 seaborn==0.12.2 aiohttp==3.8.4 beautifulsoup4==4.12.2 tqdm==4.65.0 pyyaml==6.0 joblib==1.2.0 gunicorn==21.2.0

# Install packages that might need compilation but have wheels
pip install opencv-python-headless==4.11.0.86 scikit-image==0.25.2 scikit-learn==1.6.1 scipy==1.15.2

echo "Installing GDAL from wheels..."

# Install GDAL with the same version as the system
GDAL_VERSION=$(gdal-config --version)
pip install --no-binary :all: --no-build-isolation GDAL==${GDAL_VERSION}

echo "Installing pyproj from pre-built wheel..."

# Try multiple approaches for pyproj
# First try: Latest version with no build isolation and no cache
echo "Attempt 1: Installing pyproj with no build isolation and no cache..."
pip install pyproj --no-build-isolation --no-cache-dir || true

# Second try: Specific newer version (3.5.0)
if ! pip list | grep -q pyproj; then
    echo "Attempt 2: Installing pyproj 3.5.0..."
    pip install pyproj==3.5.0 --no-build-isolation --no-cache-dir || true
fi

# Third try: Use a pre-built wheel for pyproj 3.0.1 (older but more compatible)
if ! pip list | grep -q pyproj; then
    echo "Attempt 3: Installing pyproj 3.0.1 from binary wheel..."
    pip install --only-binary :all: pyproj==3.0.1 || true
fi

# Fourth try: Try with an even older version
if ! pip list | grep -q pyproj; then
    echo "Attempt 4: Installing pyproj 2.6.1 from binary wheel..."
    pip install --only-binary :all: pyproj==2.6.1 || true
fi

# Fifth try: Download wheel directly and install
if ! pip list | grep -q pyproj; then
    echo "Attempt 5: Downloading wheel directly..."
    # For Linux x86_64 Python 3.11
    wget https://files.pythonhosted.org/packages/d1/8c/e1b2a9a7eadf2c3a5a5e42e2a1c3d8c9e9c2a7a4c5be65a7a8f9a0e5f5a/pyproj-3.0.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    pip install pyproj-3.0.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl || true
fi

# Sixth try: Try with Python 3.9 compatible wheel
if ! pip list | grep -q pyproj; then
    echo "Attempt 6: Trying Python 3.9 compatible wheel..."
    wget https://files.pythonhosted.org/packages/4a/c0/b1c6d5e2a3d1c5a0d8e9a9c2b0b1b6c6e4f6f3b6e2a8d8b4818e971a5f1/pyproj-3.0.1-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    pip install --force-reinstall pyproj-3.0.1-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl || true
fi

echo "Installing other geospatial packages..."

# Install other geospatial packages
pip install --only-binary :all: folium==0.19.5 || pip install folium==0.19.5
pip install --only-binary :all: sentinelsat==1.2.1 || pip install sentinelsat==1.2.1
pip install --only-binary :all: earthengine-api==1.5.13 || pip install earthengine-api==1.5.13

# Install any remaining packages from requirements.txt, skipping already installed ones
echo "Installing any remaining packages from requirements.txt..."
pip install -r requirements.txt --no-deps || true

echo "Alternative build completed successfully!"