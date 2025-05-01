
# Remote Sensing Data Analyzer

A comprehensive Streamlit web application for analyzing satellite and remote sensing imagery using frequency domain filtering, AI-powered insights, and advanced image processing techniques.

## Project Overview

This application provides a powerful platform for environmental scientists, GIS analysts, and researchers to analyze satellite imagery through:

- Frequency domain analysis
- Change detection
- Land cover classification
- Time series analysis
- AI-powered interpretation
- Satellite orbit visualization
- Comprehensive reporting

## Quick Start Guide

### Windows Installation

1. **Run the Installation Script**:
   ```
   .\install.bat
   ```
   This script will:
   - Create a virtual environment
   - Install GDAL using pre-built wheels
   - Install all other dependencies

2. **Configure Environment**:
   Create a `.env` file with your API keys (optional for basic functionality):
   ```
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   XAI_API_KEY=your_xai_key
   EARTHENGINE_USER=your_ee_username
   EARTHENGINE_PASSWORD=your_ee_password
   SENTINEL_USER=your_sentinel_username
   SENTINEL_PASSWORD=your_sentinel_password
   ```

3. **Run the Application**:
   ```
   .venv\Scripts\activate
   python start.py
   ```
   
   Alternatively, you can run the Streamlit app directly:
   ```
   .venv\Scripts\activate
   streamlit run app.py
   ```
   
   The `start.py` script runs all the necessary setup before starting the Streamlit app, including:
   - Fixing numpy compatibility issues
   - Setting up fallbacks for missing dependencies
   - Fixing Streamlit configuration issues
   - Creating Streamlit configuration for Render

### Manual Installation

1. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install GDAL**:
   ```bash
   # On Windows:
   python install_gdal.py
   
   # On Linux:
   sudo apt-get install libgdal-dev
   pip install gdal==$(gdal-config --version)
   
   # On macOS with Homebrew:
   brew install gdal
   pip install gdal
   ```

3. **Install Other Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   Create a `.env` file with your API keys (optional for basic functionality)

5. **Run the Application**:
   ```bash
   python start.py
   ```
   
   Alternatively, you can run the Streamlit app directly:
   ```bash
   streamlit run app.py
   ```
   
   The `start.py` script runs all the necessary setup before starting the Streamlit app, including:
   - Fixing numpy compatibility issues
   - Setting up fallbacks for missing dependencies
   - Fixing Streamlit configuration issues
   - Creating Streamlit configuration for Render

6. **Access the Web Interface**:
   Open your browser and navigate to http://localhost:8501

## Key Features

### Image Processing & Analysis
- **Image Upload**: Support for JPG, PNG, and GeoTIFF formats
- **Preprocessing**: Automatic image preparation and band extraction
- **Frequency Domain Analysis**: FFT-based spectral analysis
- **Multiple Filter Types**:
  - Low-pass filter for noise reduction
  - High-pass filter for edge detection
  - Band-pass filter for pattern isolation
  - Band-stop filter for artifact removal
  - Directional filter for linear feature enhancement

### Land Cover Analysis
- Unsupervised classification
- Water body detection
- Urban area identification
- Vegetation indices (NDVI)
- Texture analysis
- Pattern recognition

### Change Detection
- Multi-temporal image comparison
- Difference and ratio analysis
- Change clustering and classification
- Statistical significance testing
- Change visualization and mapping

### Time Series Analysis
- Temporal trend analysis
- Seasonal pattern detection
- Change trajectory modeling
- Time series visualization
- Predictive analytics

### AI Integration
- **Multiple AI Providers**:
  - OpenAI (GPT-4 Vision)
  - Anthropic (Claude)
  - xAI (Grok)
- Feature detection
- Pattern interpretation
- Environmental analysis
- Technical recommendations

### Satellite Orbit Visualization
- 3D orbit animations
- Coverage mapping
- Ground track visualization
- Satellite information database
- Mission planning tools

### Report Generation
- Comprehensive analysis reports
- Statistical summaries
- Visualization exports
- Technical documentation
- Recommendations

## Technical Stack

### Core Technologies
- **Python 3.9+**: Main programming language (Python 3.9 recommended for best compatibility)
- **Streamlit**: Web application framework
- **NumPy**: Numerical computations
- **SciPy**: Scientific computing
- **Matplotlib**: Data visualization
- **OpenCV**: Image processing
- **Pillow**: Image handling
- **Rasterio**: Geospatial data processing

### AI & Machine Learning
- **scikit-learn**: Machine learning algorithms
- **scikit-image**: Image processing
- **OpenAI API**: GPT-4 Vision integration
- **Anthropic API**: Claude integration
- **xAI API**: Grok integration

### Geospatial Processing
- **earthengine-api**: Google Earth Engine integration
- **sentinelsat**: Sentinel satellite data access
- **folium**: Interactive mapping
- **GDAL**: Geospatial data abstraction

### Additional Libraries
- **python-dotenv**: Environment variable management
- **requests**: HTTP client
- **trafilatura**: Web content extraction

## Project Structure

```
├── app.py                 # Main application file
├── modules/               # Feature-specific modules
│   ├── ai_providers.py    # AI integration
│   ├── change_detection.py# Change detection
│   ├── classification.py  # Image classification
│   ├── documentation.py   # App documentation
│   ├── land_cover.py     # Land cover analysis
│   ├── satellite_orbit.py # Orbit visualization
│   └── time_series.py    # Time series analysis
├── utils.py              # Utility functions
├── filters.py            # Image filtering functions
├── image_processor.py    # Image processing
└── requirements.txt      # Project dependencies
```

## Requirements

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Processor**: Multi-core processor (Intel i5/AMD Ryzen 5 or better recommended)
- **Memory**: Minimum 8GB RAM (16GB+ recommended for large GeoTIFF processing)
- **Storage**: 2GB free disk space for installation, plus space for your data
- **Internet Connection**: Required for satellite data fetching and AI analysis features
- **Display**: 1920x1080 resolution or higher recommended

### Software Requirements

Python 3.9+ and the following packages:

```
anthropic>=0.50.0
earthengine-api>=1.5.13
folium>=0.19.5
matplotlib>=3.10.1
numpy>=2.2.5
openai>=1.76.2
opencv-python>=4.11.0.86
pillow>=11.2.1
python-dotenv>=1.1.0
rasterio>=1.4.3
requests>=2.32.3
scikit-image>=0.25.2
scikit-learn>=1.6.1
scipy>=1.15.2
sentinelsat>=1.2.1
streamlit>=1.45.0
trafilatura>=2.0.0
```

### Python Version Compatibility

This application has been tested with the following Python versions:

- **Python 3.9**: Recommended for deployment on Render and other cloud platforms
  - Best compatibility with geospatial libraries like pyproj
  - Use `./build_py39.sh` for deployment on Render

- **Python 3.8**: Good compatibility with all dependencies
  - Works well for local development

- **Python 3.10**: Generally compatible but may require specific package versions
  - Use `pip install --no-build-isolation` for problematic packages

- **Python 3.11**: May have compatibility issues with some geospatial libraries
  - Specifically, pyproj compilation may fail
  - Use pre-built wheels when possible

### Browser Compatibility

The web interface works best with:
- Google Chrome (latest version)
- Mozilla Firefox (latest version)
- Microsoft Edge (latest version)
- Safari (latest version)

## Setup & Deployment

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/Icradle-Innovations-Ltd/RemoteSensingAnalyzer.git
cd RemoteSensingAnalyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
XAI_API_KEY=your_xai_key
EARTHENGINE_USER=your_ee_username
EARTHENGINE_PASSWORD=your_ee_password
SENTINEL_USER=your_sentinel_username
SENTINEL_PASSWORD=your_sentinel_password
```

4. Run the application:
```bash
streamlit run app.py --server.port 5000
```

The app will be available at http://0.0.0.0:5000

### Deployment on Render

#### Option 1: Deploy from GitHub

1. **Create a new Web Service on Render**:
   - Sign in to your Render account
   - Go to the Dashboard and click "New +"
   - Select "Web Service"
   - Connect your GitHub account if you haven't already
   - Select the repository: `Icradle-Innovations-Ltd/RemoteSensingAnalyzer`

2. **Configure the Web Service**:
   - Name: `remote-sensing-analyzer` (or your preferred name)
   - Environment: `Python 3`
   - Build Command: `./build.sh`
     (This script installs system dependencies including GDAL and Python packages)
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
     (This tells Render to run your Streamlit app using the port assigned by Render)
   - Select the appropriate plan (Free tier works for testing)
   
   > **Note**: If you encounter build issues with geospatial dependencies (especially pyproj), try one of these alternative build scripts:
   > - `./build_alt.sh` - Uses pre-built wheels and multiple fallback options for pyproj
   > - `./build_py39.sh` - Uses Python 3.9 instead of 3.11 (recommended for pyproj compatibility)
   > - `./build_minimal.sh` - Uses system packages and minimal wrappers as a last resort

3. **Set Environment Variables**:
   - Add all the required API keys and credentials as environment variables
   - Reference the `.env.example` file for the required variables

4. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

5. **Access Your Application**:
   - Once deployment is complete, your app will be available at the URL provided by Render

#### Option 2: Deploy from Your Local Repository

1. **Push your code to GitHub**:
   ```bash
   # Initialize Git repository (if not already done)
   git init
   
   # Add the remote repository
   git remote add origin https://github.com/Icradle-Innovations-Ltd/RemoteSensingAnalyzer.git
   
   # Add all files
   git add .
   
   # Commit changes
   git commit -m "Initial commit"
   
   # Push to GitHub
   git push -u origin main
   ```

2. **Follow the steps in Option 1 to deploy from GitHub**

#### Option 3: One-Click Deployment with Render Blueprint

This repository includes a `render.yaml` file that defines the infrastructure needed to run the application.

1. **Fork the repository**:
   - Visit https://github.com/Icradle-Innovations-Ltd/RemoteSensingAnalyzer
   - Click the "Fork" button in the top-right corner

2. **Deploy to Render**:
   - Go to https://dashboard.render.com/blueprints
   - Click "New Blueprint Instance"
   - Connect your GitHub account if you haven't already
   - Select your forked repository
   - Click "Apply Blueprint"

3. **Configure Environment Variables**:
   - After the services are created, go to each service
   - Add the required environment variables
   - Reference the `.env.example` file for the required variables

4. **Access Your Application**:
   - Once deployment is complete, your app will be available at the URL provided by Render

> **Important Note About the Build Command**:  
> The build command `./build.sh` executes our custom build script which:
> - Installs system dependencies including GDAL, which is required for geospatial processing
> - Sets up the correct environment variables for GDAL compilation
> - Installs all Python dependencies from requirements.txt
> - Installs the GDAL Python package matching the system version
> - The script must be executable (Render will handle this automatically)

> **Important Note About the Start Command**:  
> The start command `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` is critical for proper deployment:
> - `$PORT` is a variable that Render automatically sets to the assigned port
> - `--server.address 0.0.0.0` binds the server to all network interfaces, making it publicly accessible
> - Do not change this command unless you know what you're doing

### Deployment on Netlify

Netlify is primarily designed for static sites, but we can use it to create a landing page that redirects to our Render deployment:

#### Option 1: Deploy from GitHub

1. **Create a new site on Netlify**:
   - Sign in to your Netlify account
   - Go to the Dashboard and click "Add new site" > "Import an existing project"
   - Connect your GitHub account if you haven't already
   - Select the repository: `Icradle-Innovations-Ltd/RemoteSensingAnalyzer`

2. **Configure the site**:
   - The build settings are already configured in `netlify.toml`:
     - Build command: `echo 'No build command needed'`
     - Publish directory: `public`
   - No additional configuration is needed
   - This approach creates a completely static site that redirects to the Render deployment
   - It avoids all Python and Node.js dependencies
   - The `public` directory contains:
     - `index.html`: A static HTML page with automatic and manual redirects
     - `_redirects`: A Netlify-specific file that handles redirects

3. **Deploy**:
   - Click "Deploy site"
   - Netlify will automatically build and deploy your landing page

4. **Access Your Landing Page**:
   - Once deployment is complete, your landing page will be available at the URL provided by Netlify
   - The landing page will automatically redirect to your Render deployment

#### Option 2: Deploy from Your Local Repository

1. **Push your code to GitHub**:
   ```bash
   # Initialize Git repository (if not already done)
   git init
   
   # Add the remote repository
   git remote add origin https://github.com/your-username/RemoteSensingAnalyzer.git
   
   # Add all files
   git add .
   
   # Commit changes
   git commit -m "Initial commit"
   
   # Push to GitHub
   git push -u origin main
   ```

2. **Follow the steps in Option 1 to deploy from GitHub**

### Troubleshooting Deployment Issues

If you encounter issues during deployment, here are some common problems and solutions:

1. **pyproj Compilation Errors**:
   - Error messages: 
     - `Cannot assign type 'void (void *, int, const char *) except * nogil' to 'PJ_LOG_FUNCTION'`
     - `ERROR: Cython.Build.cythonize not found. Cython is required to build pyproj.`
   - **Recommended Solution**: Use Python 3.9 which is specified in the pyproject.toml file
     - The project is configured to use Python 3.9 by default on Render
     - You can also use the build command `./build_py39.sh` for additional setup
     - The build scripts now install Cython before attempting to install pyproj
   - Alternative Solution 1: Use the alternative build script by changing the build command to `./build_alt.sh`
     - This script tries multiple approaches to install pyproj, including pre-built wheels
     - It tries newer versions (3.7.1, 3.6.1, 3.5.0, 3.4.1) which have better compatibility
   - Alternative Solution 2: If all else fails, use the minimal build script: `./build_minimal.sh`
     - This script uses system packages and creates minimal wrappers for problematic packages

2. **GDAL Installation Issues**:
   - If you see errors related to GDAL installation, try modifying the build script to use a specific GDAL version
   - You can also try using the `--no-build-isolation` flag when installing GDAL

3. **Memory Limit Exceeded**:
   - If the build process fails due to memory limits, consider upgrading your Render plan
   - Alternatively, simplify the build process by using pre-built wheels where possible

4. **Long Build Times**:
   - Geospatial packages can take a long time to build
   - Be patient during the initial deployment, subsequent deployments may be faster due to caching

5. **Missing Environment Variables**:
   - If the application fails to start, check that all required environment variables are set in the Render dashboard
   - Refer to the `.env.example` file for the required variables

6. **Read-only File System Errors**:
   - Error message: `Read-only file system` or `List directory /var/lib/apt/lists/partial is missing`
   - This is normal in Render's build environment which has a read-only file system
   - The build scripts are designed to handle this by skipping system package installation
   - If you encounter this error, make sure you're using the updated build scripts

7. **NumPy Compatibility Issues**:
   - Error message: `ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject`
   - This is caused by incompatible versions of numpy and pandas
   - The build scripts now include a fix for this issue by reinstalling numpy and pandas with compatible versions
   - If you encounter this error, run `python fix_numpy_compatibility.py`

8. **Streamlit Configuration Issues**:
   - Warning message: `Warning: the config option 'server.enableCORS=false' is not compatible with 'server.enableXsrfProtection=true'`
   - This is caused by incompatible Streamlit configuration settings
   - The build scripts now include a fix for this issue by updating the Streamlit configuration
   - If you encounter this warning, run `python fix_streamlit_config.py`

9. **Netlify Deployment Issues**:
   - Error messages like `python-build: definition not found`, `404 (Not Found)`, or `No matching distribution found for streamlit==1.45.0`
   - These issues are caused by Netlify trying to install Python dependencies
   - The repository now includes a completely static approach for Netlify:
     - `netlify.toml`: Specifies no build command and the public directory
     - `public/index.html`: A static HTML page that redirects to the Render deployment
     - `public/_redirects`: A Netlify-specific file that handles redirects
     - `.netlifyignore`: Ignores all Python files and dependencies
     - `.npmrc`: Prevents npm from installing dependencies
     - `.nvmrc`: Specifies the Node.js version
   - This approach avoids all dependency issues by not using any build process
   - If you encounter deployment issues:
     - Make sure you're using the latest `netlify.toml` configuration
     - Check that the `public` directory exists and contains `index.html` and `_redirects`
     - Set the publish directory to `public` in the Netlify dashboard
     - Try clearing the Netlify cache and redeploying
     - In the Netlify dashboard, go to Site settings > Build & deploy > Continuous Deployment > Build settings and set:
       - Base directory: Not set
       - Build command: `echo 'No build needed'`
       - Publish directory: `public`

### Git Commands for Contributing

To contribute to this project, follow these steps:

1. **Fork the repository**:
   - Visit https://github.com/Icradle-Innovations-Ltd/RemoteSensingAnalyzer
   - Click the "Fork" button in the top-right corner

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/RemoteSensingAnalyzer.git
   cd RemoteSensingAnalyzer
   ```

3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/Icradle-Innovations-Ltd/RemoteSensingAnalyzer.git
   ```

4. **Working with branches**:

   **List all branches**:
   ```bash
   # List local branches
   git branch
   
   # List all branches (local and remote)
   git branch -a
   ```

   **Create a new branch**:
   ```bash
   # Create a new branch and switch to it
   git checkout -b feature/your-feature-name
   
   # Alternative method (Git 2.23+)
   git switch -c feature/your-feature-name
   ```

   **Switch between branches**:
   ```bash
   # Switch to an existing branch
   git checkout branch-name
   
   # Alternative method (Git 2.23+)
   git switch branch-name
   
   # Switch to the main branch
   git checkout main
   ```

   **Delete a branch**:
   ```bash
   # Delete a local branch (after merging)
   git branch -d branch-name
   
   # Force delete a local branch (even if not merged)
   git branch -D branch-name
   
   # Delete a remote branch
   git push origin --delete branch-name
   ```

5. **Make your changes and commit them**:
   ```bash
   # Stage all changes
   git add .
   
   # Stage specific files
   git add file1.py file2.py
   
   # Commit changes
   git commit -m "Add your meaningful commit message here"
   ```

6. **Push your changes to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a pull request**:
   - Go to https://github.com/Icradle-Innovations-Ltd/RemoteSensingAnalyzer
   - Click "Pull requests" > "New pull request"
   - Select "compare across forks"
   - Select your fork and branch
   - Click "Create pull request"

8. **Keep your fork in sync with the upstream repository**:
   ```bash
   # Fetch changes from upstream
   git fetch upstream
   
   # Switch to your main branch
   git checkout main
   
   # Merge upstream changes
   git merge upstream/main
   
   # Push changes to your fork
   git push origin main
   ```

9. **Update your feature branch with latest changes**:
   ```bash
   # Switch to main and get updates
   git checkout main
   git pull upstream main
   
   # Switch back to your feature branch
   git checkout feature/your-feature-name
   
   # Merge changes from main
   git merge main
   
   # Resolve any conflicts if they occur
   # Then push the updated branch
   git push origin feature/your-feature-name
   ```

### Common Git Operations and Troubleshooting

#### Viewing Changes

```bash
# Show status of working directory
git status

# Show changes between working directory and last commit
git diff

# Show changes that are staged
git diff --staged

# Show commit history
git log

# Show commit history with graph visualization
git log --graph --oneline --all
```

#### Undoing Changes

```bash
# Discard changes in working directory for a specific file
git checkout -- filename

# Discard all changes in working directory
git checkout -- .

# Unstage a file (keep the changes in working directory)
git restore --staged filename

# Amend the last commit (e.g., to fix commit message or add forgotten files)
git commit --amend

# Revert a commit (creates a new commit that undoes changes)
git revert commit-hash

# Reset to a previous commit (caution: destructive operation)
git reset --hard commit-hash
```

#### Stashing Changes

```bash
# Temporarily save changes without committing
git stash save "work in progress"

# List stashed changes
git stash list

# Apply most recent stash and keep it in the stash list
git stash apply

# Apply most recent stash and remove it from the stash list
git stash pop

# Apply a specific stash
git stash apply stash@{n}

# Clear all stashes
git stash clear
```

#### Resolving Merge Conflicts

When a merge conflict occurs:

1. **Identify conflicted files**:
   ```bash
   git status
   ```

2. **Open the conflicted files** and look for conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`):
   - Between `<<<<<<< HEAD` and `=======` is your current branch's code
   - Between `=======` and `>>>>>>> branch-name` is the incoming branch's code

3. **Edit the files** to resolve conflicts by choosing one version or manually merging them

4. **Mark as resolved**:
   ```bash
   git add filename
   ```

5. **Complete the merge**:
   ```bash
   git commit
   ```

#### Tagging Releases

```bash
# Create a lightweight tag
git tag v1.0.0

# Create an annotated tag with a message
git tag -a v1.0.0 -m "Version 1.0.0 release"

# Push tags to remote
git push origin --tags

# List all tags
git tag

# Delete a tag
git tag -d v1.0.0
git push origin --delete v1.0.0  # Delete from remote
```

### Docker Deployment

1. **Build the Docker image**:
```bash
docker build -t remote-sensing-analyzer .
```

2. **Run the container**:
```bash
docker run -p 8501:8501 --env-file .env remote-sensing-analyzer
```

3. **Access the application**:
   - Open your browser and navigate to http://localhost:8501

### Deployment on Render

1. **Create a new Web Service on Render**:
   - Connect your GitHub repository
   - Select the repository containing the Remote Sensing Data Analyzer

2. **Configure the Web Service**:
   - Name: `remote-sensing-analyzer` (or your preferred name)
   - Environment: `Python 3`
   - Build Command: `./build.sh`
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - Select the appropriate plan (Free tier works for testing)

3. **Set Environment Variables**:
   - Add all the required API keys and credentials as environment variables
   - Reference the `.env.example` file for the required variables

4. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

5. **Access Your Application**:
   - Once deployment is complete, your app will be available at the URL provided by Render

### Docker Deployment

1. **Build the Docker image**:
```bash
docker build -t remote-sensing-analyzer .
```

2. **Run the container**:
```bash
docker run -p 8501:8501 --env-file .env remote-sensing-analyzer
```

3. **Access the application**:
   - Open your browser and navigate to http://localhost:8501

### Deployment on Replit

1. Create a new Python Repl
2. Upload all project files
3. Add your API keys in the Secrets tab
4. The deployment is configured automatically
5. Click "Deploy" in the Deployments tab

## Usage Guide

1. **Image Upload**:
   - Use sidebar to upload satellite imagery
   - Support for JPG, PNG, and GeoTIFF formats
   - URL-based image fetching available

2. **Analysis Options**:
   - Choose from various analysis tabs
   - Adjust parameters as needed
   - View results in real-time

3. **Visualization**:
   - Original image display
   - FFT spectrum visualization
   - Filtered result preview
   - Interactive maps and plots

4. **Reports**:
   - Generate comprehensive reports
   - Download analysis results
   - Export visualizations

## Application Features

### Visualization Tab
- Side-by-side comparison of original and processed images
- FFT spectrum visualization
- Filter result preview
- Interactive parameter adjustment

### Spectral Analysis Tab
- Frequency domain analysis
- Multiple filter types
- Custom filter parameters
- Radial profile analysis

### Change Detection Tab
- Image comparison tools
- Change magnitude visualization
- Statistical analysis
- Change classification

### AI Analysis Tab
- Feature detection
- Pattern interpretation
- Technical analysis
- Recommendations

### Satellite Orbits Tab
- 3D orbit visualization
- Coverage mapping
- Satellite information
- Mission planning

### Report Generation Tab
- Comprehensive reporting
- Statistical summaries
- Visualization export
- Technical documentation

## License & Attribution

© 2025 Icradle Innovations Ltd. All rights reserved.

The Remote Sensing Data Analyzer is a proprietary tool designed for professional satellite image analysis and interpretation. All data analysis and visualizations are for informational purposes only.

## Setup Instructions

### Local Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd remote-sensing-data-analyzer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with required API keys:
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
XAI_API_KEY=your_xai_key
EARTHENGINE_USER=your_ee_username
EARTHENGINE_PASSWORD=your_ee_password
SENTINEL_USER=your_sentinel_username
SENTINEL_PASSWORD=your_sentinel_password
```

4. Run the application:
```bash
streamlit run app.py --server.port 5000
```

The application will be available at http://0.0.0.0:5000

### Production Environment Setup (Replit)

1. Create a new Python Repl and upload project files
2. Set up environment variables in Replit Secrets:
   - Go to "Tools" → "Secrets"
   - Add all required API keys and credentials
3. Install dependencies:
   - They will be automatically installed from requirements.txt
4. Configure the deployment:
   - Go to "Tools" → "Deployments"
   - The deployment configuration is already set in .replit file
5. Deploy:
   - Click "Deploy" in the Deployments tab
   - Your app will be available at your-repl-name.your-username.repl.co

### Production Health Checks

- Monitor the application logs in the Replit console
- Check the "Deployments" tab for deployment status
- Verify API integrations are working properly
- Monitor memory usage and performance metrics
- Check satellite data source connectivity

## Support & Contact

For technical support, feature requests, or bug reports, please use the project's issue tracker or contact our support team through the application's help interface.

## Sample Data and Basic Usage

### Sample Data Sources

You can use the following sources to obtain sample satellite imagery for testing:

1. **USGS Earth Explorer**: https://earthexplorer.usgs.gov/
   - Landsat imagery
   - MODIS data
   - Digital Elevation Models

2. **Copernicus Open Access Hub**: https://scihub.copernicus.eu/
   - Sentinel-1 (Radar)
   - Sentinel-2 (Optical)

3. **NASA Earthdata**: https://earthdata.nasa.gov/
   - Various satellite products
   - Global datasets

### Basic Usage Workflow

1. **Upload an Image**:
   - Use the sidebar to upload a satellite image (JPG, PNG, or GeoTIFF)
   - For GeoTIFF files, you can select specific bands to analyze

2. **Apply Filters**:
   - Choose a filter type (Low-pass, High-pass, or Band-stop)
   - Adjust filter parameters using the sliders
   - View the filtered result in real-time

3. **Advanced Analysis**:
   - Use the Advanced Analysis Options in the sidebar to access:
     - NDVI calculation (for multi-band images)
     - Land cover classification
     - Change detection (when comparing multiple images)
     - AI-powered analysis (requires API keys)

4. **Export Results**:
   - Download processed images
   - Generate and export analysis reports
   - Save visualizations for presentations

### Troubleshooting

- **Memory Issues**: For large GeoTIFF files, the application automatically resizes images to improve performance
- **API Connection Errors**: Check your internet connection and verify API keys in the .env file
- **Missing Dependencies**: Ensure all required packages are installed using `pip install -r requirements.txt`
