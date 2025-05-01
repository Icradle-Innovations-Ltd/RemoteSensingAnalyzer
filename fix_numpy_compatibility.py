#!/usr/bin/env python3
"""
This script fixes numpy compatibility issues with pandas and other packages.
It should be run after installing all dependencies.
"""

import os
import sys
import subprocess
import importlib.metadata

def fix_numpy_compatibility():
    """Fix numpy compatibility issues with pandas and other packages."""
    print("Checking for numpy compatibility issues...")
    
    try:
        # Get installed numpy version
        numpy_version = importlib.metadata.version('numpy')
        print(f"Current numpy version: {numpy_version}")
        
        # Reinstall numpy to ensure compatibility
        print("Reinstalling numpy to ensure compatibility...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', 'numpy'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'numpy==1.24.3'])
        
        # Reinstall pandas to ensure compatibility
        print("Reinstalling pandas to ensure compatibility...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', 'pandas'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pandas==2.0.3'])
        
        # Reinstall other packages that might be affected
        print("Reinstalling other affected packages...")
        for package in ['scipy', 'scikit-learn', 'scikit-image']:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', package])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', package])
            except Exception as e:
                print(f"Warning: Failed to reinstall {package}: {e}")
        
        print("Numpy compatibility fix completed successfully")
    except Exception as e:
        print(f"Error fixing numpy compatibility: {e}")
        print("Continuing anyway...")

if __name__ == "__main__":
    fix_numpy_compatibility()