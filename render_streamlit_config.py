#!/usr/bin/env python3
"""
This script creates a Streamlit configuration file in the Render environment.
It should be run before starting the application in Render.
"""

import os
import sys
import toml

def create_render_streamlit_config():
    """Create a Streamlit configuration file in the Render environment."""
    print("Creating Streamlit configuration for Render environment...")
    
    # Check if we're running in Render
    if 'RENDER' in os.environ:
        print("Running in Render environment")
    else:
        print("Not running in Render environment, but continuing anyway")
    
    # Print current working directory for debugging
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # Create .streamlit directory in the home directory
    home_dir = os.path.expanduser("~")
    streamlit_dir = os.path.join(home_dir, '.streamlit')
    os.makedirs(streamlit_dir, exist_ok=True)
    print(f"Created Streamlit config directory: {streamlit_dir}")
    
    # Create config.toml in the home directory
    config_path = os.path.join(streamlit_dir, 'config.toml')
    
    # Configuration for Render
    render_config = {
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
    
    # Write the configuration
    with open(config_path, 'w') as f:
        toml.dump(render_config, f)
    
    print(f"Created Streamlit config file: {config_path}")
    print("Configuration:")
    print("  [server]")
    for key, value in render_config['server'].items():
        print(f"  {key} = {value}")
    
    # Also create in the project directory for good measure
    project_streamlit_dir = '.streamlit'
    os.makedirs(project_streamlit_dir, exist_ok=True)
    project_config_path = os.path.join(project_streamlit_dir, 'config.toml')
    
    with open(project_config_path, 'w') as f:
        toml.dump(render_config, f)
    
    print(f"Also created Streamlit config file in project directory: {project_config_path}")
    
    print("Render Streamlit configuration complete")

if __name__ == "__main__":
    create_render_streamlit_config()