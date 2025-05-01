"""
Documentation module for the Remote Sensing Data Analyzer
Contains documentation content, tutorials, and examples
"""

def get_documentation_section(section):
    """
    Retrieve a specific documentation section
    
    Parameters:
    ----------
    section : str
        Name of the documentation section to retrieve
    
    Returns:
    -------
    content : str
        Markdown formatted content for the requested section
    """
    
    docs = {
        "overview": """
# Remote Sensing Data Analyzer - Overview

The Remote Sensing Data Analyzer is a comprehensive tool for analyzing satellite imagery using frequency-domain filtering techniques and advanced image processing algorithms. This application helps identify features, extract patterns, and make data-driven decisions based on remote sensing data.

## Key Features

### Frequency Domain Analysis
- Convert spatial image data to the frequency domain using Fast Fourier Transform (FFT)
- Visualize frequency spectrum to identify periodic patterns and texture characteristics
- Apply various filters (low-pass, high-pass, band-stop, band-pass, directional) to highlight or suppress specific features

### Land Cover Analysis
- Classify land cover types using unsupervised clustering algorithms
- Detect specific features such as water bodies, vegetation, and urban areas
- Calculate vegetation indices like NDVI for vegetation health assessment

### Change Detection
- Identify changes between two satellite images of the same area
- Analyze the nature and significance of detected changes
- Generate comprehensive reports on landscape changes

### Time Series Analysis
- Track changes over time using multiple images of the same area
- Detect trends and seasonal patterns in landscape evolution
- Predict future changes based on historical data

### AI-Powered Analysis
- Leverage multiple AI models (OpenAI, Anthropic, xAI) to interpret imagery
- Receive insights and recommendations based on detected patterns
- Generate comprehensive reports combining human and AI expertise

## Applications

- Environmental monitoring and conservation
- Urban planning and development tracking
- Agricultural crop health assessment
- Disaster response and damage assessment
- Land use change detection and monitoring
- Scientific research on landscape patterns and processes
""",

        "spectral_analysis": """
# Spectral Analysis Guide

## What is Spectral Analysis?

Spectral analysis in remote sensing involves analyzing the frequency characteristics of an image rather than its spatial properties. This is achieved through the Fourier Transform, which decomposes the image into its constituent frequency components.

## Why Use Spectral Analysis?

Many features in satellite imagery have distinct frequency signatures:
- Regular patterns (like agricultural fields) appear as bright spots at specific locations in the frequency spectrum
- Smooth areas (like water bodies) have most of their energy in low frequencies
- Rough textures (like forests) have significant energy in high frequencies
- Linear features (like roads or rivers) create line patterns in the frequency domain

## Interpreting the Frequency Spectrum

The 2D Frequency Spectrum display shows:
- The center point represents the DC component (average brightness of the image)
- Distance from center indicates spatial frequency (inverse of wavelength)
- Direction from center indicates the orientation of features
- Brightness indicates the strength of that frequency component

## Using Filters Effectively

### Low-pass Filter
- Preserves low frequencies (large-scale features) while removing high frequencies (fine details)
- Useful for smoothing images, removing noise, and highlighting large-scale patterns
- Applications: Identifying large geological formations, general land cover types

### High-pass Filter
- Preserves high frequencies (fine details) while removing low frequencies (large-scale variations)
- Useful for edge detection and enhancing fine details
- Applications: Detecting borders, small objects, and texture details

### Band-pass Filter
- Preserves frequencies within a specific range
- Useful for isolating patterns with a particular scale
- Applications: Extracting field patterns, regular structures, or specific-sized objects

### Band-stop Filter
- Removes frequencies within a specific range
- Useful for eliminating periodic noise or unwanted patterns
- Applications: Removing sensor artifacts, scan lines, or unwanted repetitive patterns

### Directional Filter
- Preserves features with specific orientations
- Useful for highlighting linear features in particular directions
- Applications: Detecting roads, rivers, boundaries with known orientations

## Practical Tips

1. Start with a low-pass filter to identify major features, then progressively add high frequencies
2. Use the radial profile to identify dominant frequencies in the image
3. Experiment with different cutoff values to achieve optimal results
4. Use gaussian tapering to reduce ringing artifacts around sharp edges
5. For directional features, try the directional filter with varying angles and widths
""",

        "land_cover": """
# Land Cover Analysis Guide

## Introduction to Land Cover Analysis

Land cover analysis is the process of identifying and classifying different types of land cover (e.g., vegetation, water, urban areas) in satellite imagery. This can provide valuable insights for environmental monitoring, urban planning, and resource management.

## Available Techniques

### Unsupervised Classification

The "Classify Land Cover" function uses K-means clustering to automatically identify distinct land cover types in your image:

1. Select the number of classes (typically 3-7 works well for most imagery)
2. The algorithm groups pixels with similar spectral properties
3. Each class is assigned a unique color in the visualization
4. Statistics show the proportion of each class

This approach is useful when you want to:
- Get a quick overview of land cover distribution
- Identify major landscape patterns
- Create a baseline for change detection

### Water Body Detection

The "Water Bodies" feature detection option uses spectral and textural properties to identify water:

1. Dark areas in the image are identified as potential water
2. Texture analysis helps distinguish water from other dark features
3. The result shows water bodies highlighted in blue

This is particularly useful for:
- Flood mapping
- Wetland inventory
- Reservoir monitoring
- Coastal zone management

### Urban Area Detection

The "Urban Areas" feature detection looks for the distinctive texture patterns of built environments:

1. The algorithm detects high-contrast areas with regular patterns
2. Texture measures like Gabor filters identify urban textures
3. Results show urban areas highlighted in red

Applications include:
- Urban growth monitoring
- Development density assessment
- Infrastructure planning
- Impervious surface mapping

## Interpretation Tips

1. **Color Interpretation**: In the land cover classification, colors represent different classes but don't have inherent meaning. You'll need to interpret what each class represents by comparing to the original image.

2. **Mixed Pixels**: Many pixels contain a mixture of land cover types. The classification assigns each pixel to its most dominant class.

3. **Validation**: Always validate results against ground truth or higher-resolution imagery when possible.

4. **Scale Considerations**: Different features are detectable at different spatial resolutions. Urban detection works best on medium to high-resolution imagery.

5. **Spectral Limitations**: Remember that classification is based on the available spectral information. Multi-spectral images will generally provide better results than single-band images.
""",

        "change_detection": """
# Change Detection Guide

## Introduction to Change Detection

Change detection is the process of identifying differences in the state of land features by observing them at different times. This capability is essential for monitoring land use changes, disaster impacts, urban growth, deforestation, and many other environmental changes.

## Available Methods

### Difference Method
- Calculates the absolute difference between pixel values in two images
- Simple and intuitive approach
- Works well when images have similar illumination conditions
- Best for situations with clear, substantial changes

### Ratio Method
- Calculates the ratio between corresponding pixels in the two images
- More robust to illumination differences than simple differencing
- Good for detecting changes in areas with varying lighting conditions
- Effective for highlighting proportional changes

### Regression Method
- Establishes a statistical relationship between the two images
- Adjusts for systematic differences between images
- Most robust to illumination and seasonal differences
- Best for subtle changes or images taken under different conditions

## Interpreting Results

The change detection results include:

### Visual Outputs
- **Change RGB**: The comparison image with changes highlighted in red
- **Change Magnitude**: A heatmap showing the intensity of changes

### Analytical Outputs
- **Change Types**: Classification of changes (e.g., new structure, vegetation growth)
- **Change Size**: Area affected by each change
- **Confidence**: Estimated reliability of each detected change
- **Comprehensive Report**: Detailed analysis of all detected changes

## Change Type Interpretation

The analysis categorizes changes into various types:

- **New Structure**: Significant increase in contrast and texture complexity
- **Structure Removal**: Decrease in contrast and texture complexity
- **Land Clearing**: Increase in brightness and decrease in texture
- **Vegetation Growth**: Increase in brightness with maintained texture
- **Water/Flooding**: Decrease in brightness with increased uniformity
- **Shadowing**: Decrease in brightness with maintained texture edges
- **Subtle Change**: Minor changes in texture or brightness

## Time Series Analysis

The time series simulation functionality provides a way to:

1. Analyze trends over time (even with limited images)
2. Visualize progressive changes
3. Generate trend maps showing areas of increase or decrease
4. Predict future patterns based on established trends

## Practical Tips

1. **Image Alignment**: Ensure images are properly co-registered to avoid false changes
2. **Seasonal Considerations**: Be aware of seasonal effects when comparing images from different times of year
3. **Threshold Adjustment**: Increase the threshold to focus on major changes, decrease to capture subtle changes
4. **Minimum Size**: Adjust the minimum change area size to filter out noise and focus on significant changes
5. **Validation**: Always validate detected changes against additional data sources when possible
""",

        "time_series": """
# Time Series Analysis Guide

## Introduction to Time Series Analysis

Time series analysis involves examining sequential satellite images of the same area captured over time. This approach allows for monitoring gradual changes, detecting trends, identifying seasonal patterns, and predicting future landscape changes.

## Key Concepts

### Temporal Patterns

Satellite imagery time series can reveal several types of temporal patterns:

1. **Trends**: Long-term increases or decreases in values (e.g., urban growth, deforestation)
2. **Seasonality**: Regular patterns that repeat over a fixed period (e.g., annual crop cycles)
3. **Sudden Changes**: Abrupt alterations caused by disturbances (e.g., fires, floods)
4. **Cyclical Patterns**: Irregular variations that don't have a fixed frequency

### Time Series Metrics

The analysis calculates several important metrics:

- **Change Magnitude**: Degree of change between time points
- **Trend Direction and Slope**: Whether values are increasing or decreasing, and how quickly
- **Significance**: Statistical confidence in detected trends
- **Seasonal Amplitude**: Magnitude of seasonal variations
- **Phase**: Timing of peak values within seasonal cycles

## Simulation vs. Actual Time Series

While the application demonstrates time series capabilities through simulation, these same techniques can be applied to actual time series data:

- **Full Time Series**: Use multiple images taken over regular intervals
- **Seasonal Composites**: Combine images from the same season across years
- **Event-Based**: Images before and after specific events (floods, fires, etc.)

## Applications

### Environmental Monitoring
- Track vegetation health changes over time
- Monitor water body expansion or contraction
- Detect gradual land degradation

### Climate Change Studies
- Quantify glacial retreat
- Monitor coastline changes
- Track shifts in vegetation zones

### Urban Development
- Measure urban expansion rates
- Monitor infrastructure development
- Assess impervious surface growth

### Agriculture
- Track crop phenology
- Detect irrigation patterns
- Assess long-term field productivity

## Interpretation Guidelines

1. **Trend Maps**: Red areas show decreasing values, green areas show increasing values
2. **Significance**: Transparent areas in trend maps indicate statistically insignificant changes
3. **Seasonal Patterns**: Color represents the timing of peak values, brightness shows amplitude
4. **Change Reports**: Provide quantitative assessment of dominant patterns

## Advanced Usage

For advanced users with actual time series data:

1. Prepare a sequence of co-registered images
2. Ensure consistent pre-processing (atmospheric correction, normalization)
3. Consider using external data (climate, human activities) to explain observed patterns
4. Use trend analysis results to forecast future conditions
""",

        "ai_analysis": """
# AI-Powered Analysis Guide

## Introduction to AI Analysis

The Remote Sensing Data Analyzer integrates advanced AI models to provide intelligent interpretation of satellite imagery. These models can identify features, understand patterns, and generate insights that might not be immediately apparent to human analysts.

## Available AI Providers

The application supports multiple AI providers to give you flexibility and robustness:

### OpenAI (GPT-4 Vision)
- Comprehensive image understanding capabilities
- Strong general knowledge of geography and environmental systems
- Excellent at explaining detected features

### Anthropic (Claude)
- Detailed analytical capabilities
- Strong reasoning about spatial patterns
- Thorough explanations with scientific context

### xAI (Grok)
- Alternative model with unique perspective
- Complementary analysis approach
- May detect different features than other models

## How AI Analysis Works

1. Both your original and filtered images are sent to the selected AI provider
2. The AI analyzes visual features, patterns, and transformations
3. Results are structured into categories: features detected, filter effects, environmental patterns, applications, and recommendations
4. A comprehensive summary ties everything together

## Interpretation Tips

The AI analysis provides several key components:

### Features Detected
- Physical elements identified in the imagery (forests, urban areas, water bodies, etc.)
- Patterns and textures that may indicate specific land uses
- Anomalies or noteworthy elements that stand out

### Filter Effects
- How the applied filter has transformed the image
- Which features were enhanced or suppressed
- How the frequency domain manipulation affected interpretability

### Environmental Patterns
- Ecological or environmental systems visible in the imagery
- Relationships between different landscape elements
- Potential environmental processes occurring in the area

### Applications
- Practical uses for the insights gained from the analysis
- Fields that could benefit from the processed imagery
- Potential decision-making applications

### Recommendations
- Suggestions for further analysis
- Other filters or techniques that might yield additional insights
- Alternative approaches to consider

## Practical Usage

1. **Compare Providers**: Try different AI providers for varied perspectives
2. **Filtered Insights**: Analyze both original and filtered images to understand what the filtering revealed
3. **Verification**: Use AI insights as a starting point, but verify with domain knowledge
4. **Iterative Approach**: Use AI feedback to guide further filtering and analysis
5. **Report Integration**: Incorporate AI insights into the final reports

## API Key Management

To use different AI providers, you'll need to:
1. Obtain API keys from the respective providers
2. Add these keys in the Settings tab
3. Select your preferred provider for analysis

Remember that different providers may have different rate limits and pricing structures.
""",

        "satellite_data": """
# Satellite Data Guide

## Introduction to Satellite Imagery

Satellite imagery provides a valuable perspective for monitoring and analyzing the Earth's surface. Different satellite sensors offer various capabilities in terms of spatial resolution, spectral bands, temporal frequency, and coverage.

## Satellite Data Sources

### Sentinel-2
- European Space Agency (ESA) satellite constellation
- 10-20m spatial resolution (depending on band)
- 13 spectral bands (visible, near-infrared, shortwave infrared)
- 5-day revisit time
- Free and open data policy
- Excellent for land cover monitoring, agriculture, forestry

### Landsat
- NASA/USGS satellite program (currently Landsat 8-9)
- 15-30m spatial resolution
- 11 spectral bands including thermal
- 16-day revisit time
- Historical archive dating back to 1972
- Free and open data policy
- Great for long-term change detection and time series analysis

### Earth Engine
- Google's platform providing access to multiple satellite datasets
- Includes Sentinel, Landsat, MODIS, and many other sources
- Cloud-based processing capabilities
- APIs for advanced data retrieval and analysis

## Understanding Satellite Bands

Satellite images often contain multiple spectral bands, each capturing energy at different wavelengths:

### Common Band Combinations
- **Natural Color**: Combination of red, green, and blue bands (similar to what human eyes see)
- **False Color Infrared**: Near-infrared, red, green (vegetation appears red)
- **Agriculture**: Near-infrared, shortwave infrared, blue (emphasizes crop health)
- **Urban**: Shortwave infrared, near-infrared, red (emphasizes built environment)

### Key Bands for Analysis
- **Blue**: Water penetration, atmosphere
- **Green**: Plant vigor, urban features
- **Red**: Vegetation absorption, man-made features
- **Near-Infrared (NIR)**: Vegetation reflectance, biomass
- **Shortwave Infrared (SWIR)**: Moisture content, soil types
- **Thermal Infrared**: Surface temperature, heat signatures

## Working with GeoTIFF Files

GeoTIFF files contain georeferenced information along with pixel data:

- **Bands**: Access different spectral bands for specialized analysis
- **Georeferencing**: Data about the geographic location of the image
- **Metadata**: Additional information about acquisition time, processing level, etc.

## Spectral Indices

Spectral indices combine multiple bands to highlight specific features:

### Vegetation Indices
- **NDVI** (Normalized Difference Vegetation Index): (NIR - Red) / (NIR + Red)
  - Values range from -1 to 1
  - Higher values indicate healthier vegetation
  - Useful for monitoring crop health, forest conditions

### Water Indices
- **NDWI** (Normalized Difference Water Index): (Green - NIR) / (Green + NIR)
  - Highlights water bodies
  - Useful for flood mapping, water resource monitoring

### Urban Indices
- **NDBI** (Normalized Difference Built-up Index): (SWIR - NIR) / (SWIR + NIR)
  - Highlights built-up areas
  - Useful for urban growth monitoring

## Best Practices

1. **Preprocessing**: Consider atmospheric correction for accurate analysis
2. **Cloud Filtering**: Check for cloud cover before analysis
3. **Seasonal Awareness**: Be mindful of seasonal effects when comparing images
4. **Resolution Matching**: Ensure images being compared have the same resolution
5. **Band Selection**: Choose appropriate bands for your specific analysis goals
""",

        "faq": """
# Frequently Asked Questions

## General Questions

### What can I do with this application?
The Remote Sensing Data Analyzer allows you to process satellite imagery using frequency-domain techniques to enhance features, detect patterns, identify changes, and extract meaningful information from remote sensing data.

### What image formats are supported?
The application supports common image formats (JPG, PNG) as well as GeoTIFF files that contain geospatial metadata.

### Do I need programming knowledge to use this tool?
No, the intuitive user interface allows analysts without programming knowledge to perform advanced satellite image analysis.

## Technical Questions

### What is a Fourier Transform and why is it useful?
The Fourier Transform converts an image from the spatial domain to the frequency domain, revealing periodic patterns and texture characteristics that may not be visible in the original image. This is particularly useful for identifying regular patterns in landscapes, distinguishing between different land cover types, and filtering out unwanted features.

### What's the difference between the various filters?
- **Low-pass**: Preserves large-scale features while removing fine details
- **High-pass**: Enhances fine details and edges while removing broad patterns
- **Band-stop**: Removes patterns with specific frequencies
- **Band-pass**: Preserves patterns with specific frequencies
- **Directional**: Enhances features with specific orientations

### How does land cover classification work?
The land cover classification uses K-means clustering to group pixels with similar properties. The algorithm automatically identifies patterns in the data and separates them into the specified number of classes.

### What is NDVI and why is it important?
NDVI (Normalized Difference Vegetation Index) uses the red and near-infrared bands to measure vegetation health and density. It's widely used in agriculture, forestry, and environmental monitoring to assess plant vigor and detect changes in vegetation cover.

## Data Questions

### Can I use my own satellite imagery?
Yes, you can upload your own satellite imagery in supported formats. For best results with advanced features, use multi-band imagery like GeoTIFF files from Sentinel-2 or Landsat.

### Where can I get satellite imagery to use with this tool?
Free satellite imagery is available from several sources:
- [USGS Earth Explorer](https://earthexplorer.usgs.gov/) for Landsat data
- [Copernicus Open Access Hub](https://scihub.copernicus.eu/) for Sentinel data
- [Google Earth Engine](https://earthengine.google.com/) for multiple satellite datasets

### How recent is the satellite data?
The recency depends on the source of your imagery. Current operational satellites like Sentinel-2 and Landsat 8-9 provide new imagery every few days. The application itself doesn't impose any limitations on the age of the data you can analyze.

## Analysis Questions

### How accurate is the change detection?
The accuracy of change detection depends on several factors:
- Image quality and alignment
- Appropriate parameter selection (threshold, minimum size)
- Choice of detection method suitable for your specific case
- Verification against ground truth data is always recommended

### What should I do if the AI analysis doesn't seem accurate?
Try these steps:
1. Try a different AI provider
2. Ensure your images are clear and show distinct features
3. Experiment with different filters to highlight features of interest
4. Provide specific feedback to improve future analyses

### Can I export my analysis results?
Yes, you can download:
- Filtered images as PNG files
- Analysis reports as markdown files
- Change detection reports with detailed findings
- AI analysis reports with insights and recommendations

## Troubleshooting

### What should I do if my image doesn't load?
Check that:
- The file is in a supported format (JPG, PNG, or GeoTIFF)
- The file size is reasonable (under 100MB)
- The image dimensions are not extremely large

### Why does the application show an error with my GeoTIFF file?
Common issues include:
- Compressed or unusual GeoTIFF formats
- Missing bands or metadata
- Corrupt files
Try preprocessing your GeoTIFF with GDAL or similar tools before uploading.

### How can I improve performance with large images?
- Use the preprocessing options to reduce resolution if needed
- Work with individual bands rather than full multi-band images
- Consider cropping the area of interest before uploading
""",
    }
    
    # Return requested section or overview if not found
    return docs.get(section, docs["overview"])