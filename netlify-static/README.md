# Remote Sensing Analyzer - Netlify Redirect

This is a static site that redirects to the Remote Sensing Analyzer application hosted on Render.

## Deployment

This site is designed to be deployed on Netlify. It contains only static files and redirects all traffic to the Render deployment.

### Files

- `index.html`: A static HTML page with automatic and manual redirects
- `_redirects`: A Netlify-specific file that handles redirects
- `netlify.toml`: Configuration for Netlify

### Deployment Steps

1. Create a new site on Netlify
2. Connect your GitHub repository
3. Set the base directory to `netlify-static`
4. Set the publish directory to `.`
5. Set the build command to `echo 'Static site, no build needed'`
6. Deploy the site

## Why a Separate Directory?

This directory contains only the files needed for the Netlify deployment. This approach avoids all issues with Python dependencies and other build requirements.

The main application is hosted on Render, which is better suited for running the Streamlit application.