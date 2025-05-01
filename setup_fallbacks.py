#!/usr/bin/env python3
"""
This script checks for required dependencies and sets up fallbacks if needed.
It should be run before starting the application.
"""

import os
import shutil
import sys

def check_and_setup_fallbacks():
    """Check for required dependencies and set up fallbacks if needed."""
    print("Checking for required dependencies...")
    
    # Check for rasterio
    try:
        import rasterio
        print("✅ rasterio is available")
    except ImportError:
        print("⚠️ rasterio is not available, setting up fallback...")
        # Check if fallback exists
        if os.path.exists('image_processor_fallback.py'):
            # Backup original if it exists and we haven't already
            if os.path.exists('image_processor.py') and not os.path.exists('image_processor.py.bak'):
                shutil.copy2('image_processor.py', 'image_processor.py.bak')
                print("  Original image_processor.py backed up to image_processor.py.bak")
            
            # Copy fallback to main file
            shutil.copy2('image_processor_fallback.py', 'image_processor.py')
            print("  Fallback image processor installed")
        else:
            print("❌ Fallback file image_processor_fallback.py not found!")
    
    # Check for folium
    try:
        import folium
        print("✅ folium is available")
    except ImportError:
        print("⚠️ folium is not available, setting up fallback...")
        # Check if fallback exists
        if os.path.exists('modules/map_overlay_fallback.py'):
            # Backup original if it exists and we haven't already
            if os.path.exists('modules/map_overlay.py') and not os.path.exists('modules/map_overlay.py.bak'):
                shutil.copy2('modules/map_overlay.py', 'modules/map_overlay.py.bak')
                print("  Original modules/map_overlay.py backed up to modules/map_overlay.py.bak")
            
            # Copy fallback to main file
            shutil.copy2('modules/map_overlay_fallback.py', 'modules/map_overlay.py')
            print("  Fallback map overlay installed")
        else:
            print("❌ Fallback file modules/map_overlay_fallback.py not found!")
    
    # Check for numpy/pandas compatibility
    try:
        import numpy
        import pandas
        print("✅ numpy and pandas are available")
    except ImportError as e:
        print(f"⚠️ Issue with numpy/pandas: {e}")
        print("  Run fix_numpy_compatibility.py to resolve")
    
    print("Dependency check complete")

if __name__ == "__main__":
    check_and_setup_fallbacks()