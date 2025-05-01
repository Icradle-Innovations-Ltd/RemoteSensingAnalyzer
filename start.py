#!/usr/bin/env python3
"""
This script runs all the necessary setup before starting the Streamlit app.
It should be run instead of directly running streamlit run app.py.
"""

import os
import sys
import subprocess

def run_setup_and_start():
    """Run all the necessary setup and start the Streamlit app."""
    print("Running setup before starting Streamlit app...")
    
    # Run the numpy compatibility fix
    print("Fixing numpy compatibility issues...")
    try:
        subprocess.run([sys.executable, 'fix_numpy_compatibility.py'], check=True)
    except Exception as e:
        print(f"Warning: Failed to fix numpy compatibility: {e}")
    
    # Run the fallback setup
    print("Setting up fallbacks if needed...")
    try:
        subprocess.run([sys.executable, 'setup_fallbacks.py'], check=True)
    except Exception as e:
        print(f"Warning: Failed to set up fallbacks: {e}")
    
    # Run the Streamlit configuration fix
    print("Fixing Streamlit configuration...")
    try:
        subprocess.run([sys.executable, 'fix_streamlit_config.py'], check=True)
    except Exception as e:
        print(f"Warning: Failed to fix Streamlit configuration: {e}")
    
    # Run the Render Streamlit configuration
    print("Creating Streamlit configuration for Render...")
    try:
        subprocess.run([sys.executable, 'render_streamlit_config.py'], check=True)
    except Exception as e:
        print(f"Warning: Failed to create Render Streamlit configuration: {e}")
    
    # Start the Streamlit app
    print("Starting Streamlit app...")
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'true'
    
    # Run the Streamlit app
    try:
        subprocess.run(['streamlit', 'run', 'app.py'], check=True)
    except Exception as e:
        print(f"Error starting Streamlit app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_setup_and_start()