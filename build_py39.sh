#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting Python 3.9 build process..."

# Check if we're running in Render
if [ -n "$RENDER" ]; then
  echo "Running in Render environment - using Poetry to install Python 3.9"
  # Render uses Poetry, so we'll use that to set Python version
  if [ ! -f "pyproject.toml" ]; then
    echo "Creating pyproject.toml for Poetry..."
    cat > pyproject.toml << EOF
[tool.poetry]
name = "remote-sensing-analyzer"
version = "0.1.0"
description = "Remote Sensing Data Analyzer"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "3.9.*"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
EOF
  fi
else
  # Install system dependencies (for local development)
  echo "Installing system dependencies..."
  apt-get update -y || true
  apt-get install -y --no-install-recommends \
      build-essential \
      python3.9-dev \
      python3.9-venv \
      python3.9 \
      python3-pip \
      gdal-bin \
      libgdal-dev \
      libspatialindex-dev \
      proj-bin \
      libproj-dev \
      cmake \
      g++ \
      wget || true
fi

# Check if GDAL is installed
if command -v gdal-config >/dev/null 2>&1; then
  echo "GDAL version:"
  gdal-config --version
else
  echo "GDAL not found, will try to continue anyway"
fi

# Check if PROJ is installed
if command -v proj >/dev/null 2>&1; then
  echo "PROJ version:"
  # Different versions of proj use different flags for version
  proj 2>&1 | head -n 1 || echo "Using PROJ but couldn't determine version"
else
  echo "PROJ not found, will try to continue anyway"
fi

# Check Python version
echo "Python version:"
python --version

# Set environment variables if needed
if [ -d "/usr/include/gdal" ] || [ -d "/usr/include/proj" ]; then
  echo "Setting GDAL and PROJ environment variables..."
  export CPLUS_INCLUDE_PATH=/usr/include/gdal:/usr/include/proj
  export C_INCLUDE_PATH=/usr/include/gdal:/usr/include/proj
fi

# Create virtual environment if not using Poetry
if [ -z "$POETRY_ACTIVE" ]; then
  echo "Creating virtual environment..."
  python -m venv .venv
  source .venv/bin/activate
  
  # Verify Python version
  echo "Python version in virtual environment:"
  python --version
fi

# Upgrade pip and install wheel
echo "Upgrading pip and installing wheel..."
pip install --upgrade pip
pip install wheel setuptools

echo "Installing non-geospatial packages first..."

# Install packages from PyPI that don't require compilation
pip install streamlit==1.45.0 numpy==2.2.5 matplotlib==3.10.1 pillow==11.2.1 python-dotenv==1.1.0 requests==2.32.3 || echo "Warning: Some basic packages failed to install"
pip install anthropic==0.50.0 openai==1.76.2 trafilatura==2.0.0 || echo "Warning: Some API packages failed to install"
pip install plotly==5.13.1 seaborn==0.12.2 aiohttp==3.8.4 beautifulsoup4==4.12.2 tqdm==4.65.0 pyyaml==6.0 joblib==1.2.0 gunicorn==21.2.0 || echo "Warning: Some utility packages failed to install"

# Install packages that might need compilation but have wheels
pip install opencv-python-headless==4.11.0.86 scikit-image==0.25.2 scikit-learn==1.6.1 scipy==1.15.2 || echo "Warning: Some scientific packages failed to install"

# Try to install GDAL if gdal-config is available
if command -v gdal-config >/dev/null 2>&1; then
  echo "Installing GDAL Python bindings..."
  GDAL_VERSION=$(gdal-config --version)
  pip install GDAL==${GDAL_VERSION} --no-build-isolation || echo "Warning: GDAL installation failed, continuing anyway"
else
  echo "Skipping GDAL installation as gdal-config is not available"
fi

echo "Installing pyproj..."

# Install pyproj with Python 3.9 (should work better)
pip install pyproj==3.0.1 --no-build-isolation --no-cache-dir || pip install --only-binary :all: pyproj==3.0.1 || echo "Warning: pyproj installation failed, continuing anyway"

echo "Installing other geospatial packages..."

# Install other geospatial packages
pip install folium==0.19.5 sentinelsat==1.2.1 earthengine-api==1.5.13 || echo "Warning: Some geospatial packages failed to install"

# Install any remaining packages from requirements.txt, skipping already installed ones
echo "Installing any remaining packages from requirements.txt..."
pip install -r requirements.txt --no-deps || echo "Warning: Some packages from requirements.txt failed to install"

echo "Python 3.9 build completed successfully!"