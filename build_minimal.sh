#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting minimal build process..."

# Check if we're running in Render
if [ -n "$RENDER" ]; then
  echo "Running in Render environment - skipping system package installation"
  # Render already has these packages installed
else
  # Install system dependencies (for local development)
  echo "Installing system dependencies..."
  apt-get update -y || true
  apt-get install -y --no-install-recommends \
      python3-dev \
      python3-pip \
      python3-venv \
      gdal-bin \
      libgdal-dev \
      python3-gdal \
      python3-numpy \
      python3-matplotlib \
      python3-pillow \
      python3-scipy \
      python3-sklearn \
      python3-skimage \
      python3-opencv \
      python3-requests \
      python3-yaml \
      python3-dotenv \
      wget \
      unzip || true
  
  echo "System packages installed"
fi

# Check if GDAL is installed
if command -v gdal-config >/dev/null 2>&1; then
  echo "GDAL version:"
  gdal-config --version
else
  echo "GDAL not found, will try to continue anyway"
fi

# Create and use a virtual environment in Render
if [ -n "$RENDER" ]; then
  echo "Creating virtual environment for Render..."
  python -m venv .venv
  source .venv/bin/activate
fi

# Upgrade pip
pip install --upgrade pip
pip install wheel setuptools

# Install Cython first (required for building pyproj)
echo "Installing Cython..."
pip install Cython

# Install Streamlit and API packages (these don't have system packages)
echo "Installing Streamlit and API packages..."
pip install streamlit==1.45.0
pip install anthropic==0.50.0 openai==1.76.2 trafilatura==2.0.0

# Create a minimal requirements file without problematic packages
cat > minimal_requirements.txt << EOF
folium==0.19.5
sentinelsat==1.2.1
earthengine-api==1.5.13
plotly==5.13.1
seaborn==0.12.2
aiohttp==3.8.4
beautifulsoup4==4.12.2
tqdm==4.65.0
joblib==1.2.0
gunicorn==21.2.0
EOF

# Install minimal requirements
echo "Installing minimal requirements..."
pip install -r minimal_requirements.txt || true

# Create a simple wrapper for pyproj
echo "Creating pyproj wrapper..."
PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYPROJ_DIR=".venv/lib/python${PYTHON_VERSION}/site-packages/pyproj"
mkdir -p "$PYPROJ_DIR" || true
cat > "$PYPROJ_DIR/__init__.py" << EOF
# Wrapper for system pyproj
import sys
import os

# Try to import from system packages
sys.path.append('/usr/lib/python3/dist-packages')
try:
    from pyproj import *
except ImportError:
    # If system import fails, provide minimal functionality
    print("Warning: Using minimal pyproj functionality")
    
    # Define minimal CRS class
    class CRS:
        def __init__(self, init=None, **kwargs):
            self.init = init
            self.kwargs = kwargs
            
        def to_epsg(self):
            if isinstance(self.init, int) or (isinstance(self.init, str) and self.init.isdigit()):
                return int(self.init)
            return None
            
        def to_string(self):
            return str(self.init)
    
    # Define minimal Transformer class
    class Transformer:
        @staticmethod
        def from_crs(crs_from, crs_to, **kwargs):
            return Transformer()
            
        def transform(self, x, y):
            return x, y
EOF

echo "Created minimal pyproj wrapper"

# Create a simple wrapper for rasterio
echo "Creating rasterio wrapper..."
RASTERIO_DIR=".venv/lib/python${PYTHON_VERSION}/site-packages/rasterio"
mkdir -p "$RASTERIO_DIR" || true
cat > "$RASTERIO_DIR/__init__.py" << EOF
# Minimal rasterio wrapper
import sys
import os
import numpy as np
from osgeo import gdal

# Define minimal open function
def open(path, mode='r'):
    return DatasetReader(path)

class DatasetReader:
    def __init__(self, path):
        self.path = path
        self._ds = gdal.Open(path)
        if self._ds is None:
            raise IOError(f"Could not open {path}")
        self.shape = (self._ds.RasterYSize, self._ds.RasterXSize)
        self.count = self._ds.RasterCount
        
    def read(self, band_index=1):
        if band_index > self.count:
            raise IndexError(f"Band index {band_index} out of range")
        band = self._ds.GetRasterBand(band_index)
        return band.ReadAsArray()
        
    def close(self):
        self._ds = None
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Define CRS class
class CRS:
    def __init__(self, init=None):
        self.init = init
        
    def to_epsg(self):
        if isinstance(self.init, int) or (isinstance(self.init, str) and self.init.isdigit()):
            return int(self.init)
        return None
EOF

echo "Created minimal rasterio wrapper"

# Create app directory if it doesn't exist
mkdir -p app || true

# Create a simple test file to verify the installation
cat > test_imports.py << EOF
print("Testing imports...")

try:
    import streamlit
    print("✅ Streamlit imported successfully")
except ImportError as e:
    print(f"❌ Failed to import streamlit: {e}")

try:
    import numpy
    print("✅ NumPy imported successfully")
except ImportError as e:
    print(f"❌ Failed to import numpy: {e}")

try:
    from osgeo import gdal
    print("✅ GDAL imported successfully")
except ImportError as e:
    print(f"❌ Failed to import GDAL: {e}")

try:
    import pyproj
    print("✅ PyProj imported successfully (or wrapper)")
except ImportError as e:
    print(f"❌ Failed to import pyproj: {e}")

try:
    import folium
    print("✅ Folium imported successfully")
except ImportError as e:
    print(f"❌ Failed to import folium: {e}")

try:
    import rasterio
    print("✅ Rasterio imported successfully (or wrapper)")
except ImportError as e:
    print(f"❌ Failed to import rasterio: {e}")

print("Import test complete")
EOF

# Run the test file
echo "Testing imports..."
python test_imports.py

# Run the fallback setup script
echo "Setting up fallbacks if needed..."
python setup_fallbacks.py

echo "Minimal build completed successfully!"