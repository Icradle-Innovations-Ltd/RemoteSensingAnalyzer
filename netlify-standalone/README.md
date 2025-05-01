# Remote Sensing Analyzer - Netlify Redirect

This is a standalone static site that redirects to the Remote Sensing Analyzer application hosted on Render.

## Deployment

This site is designed to be deployed on Netlify using the Netlify Drop feature.

### Files

- `index.html`: A static HTML page with automatic and manual redirects
- `_redirects`: A Netlify-specific file that handles redirects
- `netlify.toml`: Configuration for Netlify

### Deployment Steps

1. Go to [Netlify Drop](https://app.netlify.com/drop)
2. Drag and drop this entire folder onto the Netlify Drop area
3. Wait for the deployment to complete
4. Your site will be available at a Netlify subdomain (e.g., random-name.netlify.app)
5. You can customize the domain in the Netlify dashboard

## Why a Standalone Site?

This is a completely standalone site with no connection to the main repository. This approach avoids all issues with Python dependencies and other build requirements.

The main application is hosted on Render, which is better suited for running the Streamlit application.