#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting build process..."

# Check if we're running in Render
if [ -n "$RENDER" ]; then
  echo "Running in Render environment - skipping system package installation"
  # Render already has these packages installed
else
  # Install system dependencies (for local development)
  echo "Installing system dependencies..."
  apt-get update -y || true
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
      g++ || true
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

# Set environment variables if needed
if [ -d "/usr/include/gdal" ] || [ -d "/usr/include/proj" ]; then
  echo "Setting GDAL and PROJ environment variables..."
  export CPLUS_INCLUDE_PATH=/usr/include/gdal:/usr/include/proj
  export C_INCLUDE_PATH=/usr/include/gdal:/usr/include/proj
fi

# Create and use a virtual environment in Render
if [ -n "$RENDER" ]; then
  echo "Creating virtual environment for Render..."
  python -m venv .venv
  source .venv/bin/activate
fi

# Upgrade pip and install wheel
echo "Upgrading pip and installing wheel..."
pip install --upgrade pip
pip install wheel setuptools

# Try to install pyproj with no build isolation
echo "Installing pyproj..."
pip install pyproj==3.2.0 --no-build-isolation --no-cache-dir || pip install pyproj==3.0.1 --no-build-isolation --no-cache-dir || pip install --only-binary :all: pyproj==3.0.1 || echo "Warning: pyproj installation failed, continuing anyway"

# Try to install GDAL if gdal-config is available
if command -v gdal-config >/dev/null 2>&1; then
  echo "Installing GDAL Python bindings..."
  GDAL_VERSION=$(gdal-config --version)
  pip install GDAL==${GDAL_VERSION} --no-build-isolation || echo "Warning: GDAL installation failed, continuing anyway"
else
  echo "Skipping GDAL installation as gdal-config is not available"
fi

# Install the rest of the requirements, excluding pyproj which we already tried to install
echo "Installing remaining requirements..."
grep -v "pyproj" requirements.txt > requirements_filtered.txt
pip install -r requirements_filtered.txt || echo "Warning: Some packages failed to install"

echo "Build completed successfully!"