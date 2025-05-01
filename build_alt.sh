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
    libproj-dev

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

# Install packages from PyPI that don't require compilation
pip install streamlit==1.45.0 numpy==2.2.5 matplotlib==3.10.1 pillow==11.2.1 python-dotenv==1.1.0 requests==2.32.3 pandas==2.0.0
pip install anthropic==0.50.0 openai==1.76.2 trafilatura==2.0.0
pip install plotly==5.13.1 seaborn==0.12.2 aiohttp==3.8.4 beautifulsoup4==4.12.2 tqdm==4.65.0 pyyaml==6.0 joblib==1.2.0 gunicorn==21.2.0

# Install packages that might need compilation but have wheels
pip install opencv-python-headless==4.11.0.86 scikit-image==0.25.2 scikit-learn==1.6.1 scipy==1.15.2

# Try to install geospatial packages with specific versions known to work
pip install pyproj==3.2.0 --no-build-isolation
pip install folium==0.19.5 sentinelsat==1.2.1

# Install GDAL with the same version as the system
GDAL_VERSION=$(gdal-config --version)
pip install GDAL==${GDAL_VERSION} --no-build-isolation

# Try to install earthengine-api last
pip install earthengine-api==1.5.13

echo "Alternative build completed successfully!"