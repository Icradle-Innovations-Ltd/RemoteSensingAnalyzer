#!/usr/bin/env python3
"""
This script checks if the Streamlit configuration is being applied correctly.
It should be run after the build process.
"""

import os
import sys
import toml
import streamlit as st

def check_streamlit_config():
    """Check if the Streamlit configuration is being applied correctly."""
    print("Checking Streamlit configuration application...")
    
    # Print current working directory for debugging
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # Check if .streamlit directory exists
    streamlit_dir = '.streamlit'
    if os.path.exists(streamlit_dir):
        print(f"Streamlit config directory exists: {os.path.abspath(streamlit_dir)}")
    else:
        print(f"Streamlit config directory does not exist: {os.path.abspath(streamlit_dir)}")
    
    # Check if config.toml exists
    config_path = os.path.join(streamlit_dir, 'config.toml')
    if os.path.exists(config_path):
        print(f"Streamlit config file exists: {os.path.abspath(config_path)}")
        
        # Load and print the configuration
        try:
            with open(config_path, 'r') as f:
                config = toml.load(f)
            
            print("Current configuration:")
            if 'server' in config:
                server_config = config['server']
                print("  [server]")
                for key, value in server_config.items():
                    print(f"  {key} = {value}")
            else:
                print("  No [server] section found")
        except Exception as e:
            print(f"Error reading config file: {e}")
    else:
        print(f"Streamlit config file does not exist: {os.path.abspath(config_path)}")
    
    # Check Streamlit's runtime configuration
    print("\nStreamlit runtime configuration:")
    try:
        # Get Streamlit's configuration
        print("  Server settings:")
        print(f"  enableCORS = {st.get_option('server.enableCORS')}")
        print(f"  enableXsrfProtection = {st.get_option('server.enableXsrfProtection')}")
    except Exception as e:
        print(f"Error getting Streamlit runtime configuration: {e}")
    
    print("\nConfiguration check complete")

if __name__ == "__main__":
    check_streamlit_config()