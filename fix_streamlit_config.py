#!/usr/bin/env python3
"""
This script checks and fixes the Streamlit configuration.
It should be run before starting the application.
"""

import os
import sys
import toml

def check_and_fix_streamlit_config():
    """Check and fix the Streamlit configuration."""
    print("Checking Streamlit configuration...")
    
    # Create .streamlit directory if it doesn't exist
    os.makedirs('.streamlit', exist_ok=True)
    
    config_path = '.streamlit/config.toml'
    
    # Default configuration
    default_config = {
        'server': {
            'headless': True,
            'enableCORS': True,
            'enableXsrfProtection': True,
            'port': 8501,
            'maxUploadSize': 200
        },
        'browser': {
            'gatherUsageStats': False
        },
        'theme': {
            'primaryColor': '#4c8bf5',
            'backgroundColor': '#ffffff',
            'secondaryBackgroundColor': '#f0f2f6',
            'textColor': '#262730',
            'font': 'sans serif'
        }
    }
    
    # Check if config file exists
    if os.path.exists(config_path):
        try:
            # Load existing config
            with open(config_path, 'r') as f:
                config = toml.load(f)
            
            # Check for incompatible settings
            if config.get('server', {}).get('enableCORS') == False and \
               config.get('server', {}).get('enableXsrfProtection') == True:
                print("⚠️ Incompatible Streamlit settings detected:")
                print("  enableCORS=false is not compatible with enableXsrfProtection=true")
                print("  Fixing configuration...")
                
                # Fix the configuration
                if 'server' not in config:
                    config['server'] = {}
                config['server']['enableCORS'] = True
                
                # Write the fixed config
                with open(config_path, 'w') as f:
                    toml.dump(config, f)
                
                print("✅ Streamlit configuration fixed")
            else:
                print("✅ Streamlit configuration is valid")
        except Exception as e:
            print(f"❌ Error reading Streamlit config: {e}")
            print("  Creating new configuration file...")
            
            # Write the default config
            with open(config_path, 'w') as f:
                toml.dump(default_config, f)
            
            print("✅ New Streamlit configuration created")
    else:
        print("⚠️ Streamlit configuration file not found")
        print("  Creating new configuration file...")
        
        # Write the default config
        with open(config_path, 'w') as f:
            toml.dump(default_config, f)
        
        print("✅ New Streamlit configuration created")

if __name__ == "__main__":
    check_and_fix_streamlit_config()