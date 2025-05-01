
# Remote Sensing Data Analyzer

A Streamlit web application for analyzing satellite and remote sensing imagery using frequency domain filtering and AI-powered insights.

## Features

- Image upload and preprocessing
- Frequency domain filtering
- Spectral analysis
- Change detection
- Time series analysis
- AI-powered image interpretation
- Satellite orbit visualization
- Report generation

## Requirements

Python 3.11+ and the following packages (included in requirements.txt):

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

## Local Setup

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

## Deployment on Replit

1. Create a new Python Repl
2. Upload all project files
3. Add your API keys in the Secrets tab (Environment Variables)
4. The deployment is configured automatically through .replit file
5. Click "Deploy" in the Deployments tab

The deployment configuration is already set in .replit:
```toml
[deployment]
deploymentTarget = "autoscale"
run = ["streamlit", "run", "app.py", "--server.port", "5000"]
```

## Project Structure

- `app.py`: Main application file
- `utils.py`: Utility functions
- `filters.py`: Image filtering functions
- `image_processor.py`: Image processing functions
- `modules/`: Feature-specific modules
  - `ai_providers.py`: AI integration
  - `change_detection.py`: Change detection
  - `classification.py`: Image classification
  - `documentation.py`: App documentation
  - And more...

## Usage

1. Upload an image using the sidebar
2. Select analysis type from available tabs
3. Adjust parameters as needed
4. View results and download reports

## License

© 2025 Icradle Innovations Ltd. All rights reserved.
