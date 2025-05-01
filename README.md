
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
- **Python 3.11+**: Main programming language
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

Python 3.11+ and the following packages:

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

## Setup & Deployment

### Local Setup

1. Clone the repository
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
