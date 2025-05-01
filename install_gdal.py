"""
GDAL Installation Helper Script for Windows

This script helps install GDAL on Windows by downloading and installing
the appropriate wheel file based on your Python version.
"""

import os
import sys
import platform
import subprocess
import tempfile
import urllib.request

def get_python_version():
    """Get the Python version as a string (e.g., '3.13')"""
    return f"{sys.version_info.major}.{sys.version_info.minor}"

def get_architecture():
    """Get the system architecture (e.g., 'win_amd64')"""
    if platform.architecture()[0] == '64bit':
        return 'win_amd64'
    else:
        return 'win32'

def install_gdal():
    """Install GDAL using a pre-built wheel"""
    python_version = get_python_version()
    architecture = get_architecture()
    
    # Check if Python version is supported
    if python_version not in ['3.9', '3.10', '3.11', '3.12', '3.13']:
        print(f"Python {python_version} is not supported by this script.")
        print("Please install GDAL manually or use Python 3.9-3.13.")
        return False
    
    # Define the wheel URL based on Python version and architecture
    # Using Christoph Gohlke's unofficial Windows binaries
    base_url = "https://download.lfd.uci.edu/pythonlibs/archived/cp"
    py_ver_no_dot = python_version.replace('.', '')
    
    # GDAL version to install
    gdal_version = "34"  # GDAL 3.4.x
    
    wheel_filename = f"GDAL-3.4.3-cp{py_ver_no_dot}-cp{py_ver_no_dot}-{architecture}.whl"
    wheel_url = f"{base_url}{py_ver_no_dot}/GDAL/{wheel_filename}"
    
    print(f"Attempting to download GDAL wheel from: {wheel_url}")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        wheel_path = os.path.join(temp_dir, wheel_filename)
        
        try:
            # Download the wheel file
            urllib.request.urlretrieve(wheel_url, wheel_path)
            print(f"Downloaded wheel file to: {wheel_path}")
            
            # Install the wheel
            print("Installing GDAL...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", wheel_path])
            print("GDAL installed successfully!")
            return True
            
        except urllib.error.URLError as e:
            print(f"Error downloading wheel: {e}")
            print("Please install GDAL manually.")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Error installing wheel: {e}")
            print("Please install GDAL manually.")
            return False

if __name__ == "__main__":
    print("GDAL Installation Helper for Windows")
    print("====================================")
    print(f"Python version: {get_python_version()}")
    print(f"Architecture: {get_architecture()}")
    print()
    
    success = install_gdal()
    
    if success:
        print("\nNext steps:")
        print("1. Install the remaining requirements:")
        print("   pip install -r requirements.txt")
        print("2. Run the application:")
        print("   streamlit run app.py")
    else:
        print("\nAlternative installation method:")
        print("1. Visit https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal")
        print("2. Download the appropriate GDAL wheel for your Python version")
        print("3. Install it with: pip install path/to/downloaded/wheel")
        print("4. Then install the remaining requirements: pip install -r requirements.txt")