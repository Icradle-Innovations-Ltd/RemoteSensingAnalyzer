#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Starting Netlify build process..."

# Print Python version
echo "Python version:"
python --version

# Create virtual environment
echo "Creating virtual environment..."
python -m venv .venv
source .venv/bin/activate

# Upgrade pip and install wheel
echo "Upgrading pip and installing wheel..."
pip install --upgrade pip
pip install wheel setuptools

# Install Cython first (required for building pyproj)
echo "Installing Cython..."
pip install Cython

echo "Installing non-geospatial packages first..."

# Install packages from PyPI that don't require compilation
pip install streamlit==1.45.0 numpy==1.24.3 matplotlib==3.10.1 pillow==11.2.1 python-dotenv==1.1.0 requests==2.32.3 || echo "Warning: Some basic packages failed to install"
pip install anthropic==0.50.0 openai==1.76.2 trafilatura==2.0.0 || echo "Warning: Some API packages failed to install"
pip install plotly==5.13.1 seaborn==0.12.2 aiohttp==3.8.4 beautifulsoup4==4.12.2 tqdm==4.65.0 pyyaml==6.0 joblib==1.2.0 gunicorn==21.2.0 || echo "Warning: Some utility packages failed to install"

# Install packages that might need compilation but have wheels
pip install opencv-python-headless==4.11.0.86 scikit-image==0.25.2 scikit-learn==1.6.1 scipy==1.15.2 || echo "Warning: Some scientific packages failed to install"

# Try to install pyproj with Python 3.9 (try newer versions first)
echo "Installing pyproj..."
pip install pyproj==3.7.1 --only-binary :all: || \
pip install pyproj==3.6.1 --only-binary :all: || \
pip install pyproj==3.5.0 --only-binary :all: || \
pip install pyproj==3.4.1 --only-binary :all: || \
pip install pyproj==3.2.0 --no-build-isolation --no-cache-dir || \
pip install pyproj==3.0.1 --no-build-isolation --no-cache-dir || \
echo "Warning: pyproj installation failed, continuing anyway"

# Try to install rasterio from binary
echo "Trying to install rasterio from binary..."
pip install --only-binary :all: rasterio || echo "Warning: rasterio installation failed, continuing anyway"

echo "Installing other geospatial packages..."

# Install other geospatial packages
pip install folium==0.19.5 sentinelsat==1.2.1 earthengine-api==1.5.13 || echo "Warning: Some geospatial packages failed to install"

# Install any remaining packages from requirements.txt, skipping already installed ones
echo "Installing any remaining packages from requirements.txt..."
pip install -r requirements.txt --no-deps || echo "Warning: Some packages from requirements.txt failed to install"

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

# Create a simple index.html file for Netlify
echo "Creating index.html for Netlify..."
cat > index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Remote Sensing Analyzer</title>
    <meta http-equiv="refresh" content="0;url=https://remote-sensing-analyzer.onrender.com">
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #4c8bf5;
        }
        p {
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        .button {
            display: inline-block;
            background-color: #4c8bf5;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin-top: 20px;
        }
        .button:hover {
            background-color: #3a7be0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Remote Sensing Analyzer</h1>
        <p>This application is hosted on Render. You will be redirected automatically.</p>
        <p>If you are not redirected, please click the button below:</p>
        <a class="button" href="https://remote-sensing-analyzer.onrender.com">Go to Application</a>
    </div>
</body>
</html>
EOF

echo "Netlify build completed successfully!"