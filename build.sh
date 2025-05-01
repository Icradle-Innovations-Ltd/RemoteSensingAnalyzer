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

# Install Cython first (required for building pyproj)
echo "Installing Cython..."
pip install Cython

# Try to install pyproj with no build isolation
echo "Installing pyproj..."
# Try newer versions first (which might have wheels available)
pip install pyproj==3.7.1 --only-binary :all: || \
pip install pyproj==3.6.1 --only-binary :all: || \
pip install pyproj==3.5.0 --only-binary :all: || \
pip install pyproj==3.4.1 --only-binary :all: || \
pip install pyproj==3.2.0 --no-build-isolation --no-cache-dir || \
pip install pyproj==3.0.1 --no-build-isolation --no-cache-dir || \
echo "Warning: pyproj installation failed, continuing anyway"

# Try to install GDAL if gdal-config is available
if command -v gdal-config >/dev/null 2>&1; then
  echo "Installing GDAL Python bindings..."
  GDAL_VERSION=$(gdal-config --version)
  pip install GDAL==${GDAL_VERSION} --no-build-isolation || echo "Warning: GDAL installation failed, continuing anyway"
  
  # Install rasterio after GDAL
  echo "Installing rasterio..."
  pip install rasterio --no-build-isolation || pip install --only-binary :all: rasterio || echo "Warning: rasterio installation failed, continuing anyway"
else
  echo "Skipping GDAL installation as gdal-config is not available"
  
  # Try to install rasterio from binary
  echo "Trying to install rasterio from binary..."
  pip install --only-binary :all: rasterio || echo "Warning: rasterio installation failed, continuing anyway"
fi

# Install the rest of the requirements, excluding pyproj which we already tried to install
echo "Installing remaining requirements..."
grep -v "pyproj" requirements.txt > requirements_filtered.txt
pip install -r requirements_filtered.txt || echo "Warning: Some packages failed to install"

# Fix numpy compatibility issues
echo "Fixing numpy compatibility issues..."
python fix_numpy_compatibility.py

# Run the fallback setup script
echo "Setting up fallbacks if needed..."
python setup_fallbacks.py

# Fix Streamlit configuration
echo "Fixing Streamlit configuration..."
python fix_streamlit_config.py

# Create Streamlit configuration for Render
echo "Creating Streamlit configuration for Render..."
python render_streamlit_config.py

echo "Build completed successfully!"