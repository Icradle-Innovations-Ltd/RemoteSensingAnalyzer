"""
Documentation module for the Remote Sensing Data Analyzer
Contains documentation content, tutorials, and examples
"""

# Main documentation sections
ABOUT_APP = """
# About Remote Sensing Data Analyzer

## Overview
The Remote Sensing Data Analyzer is a powerful tool for analyzing satellite imagery using frequency-domain techniques. 
This application allows environmental scientists, GIS analysts, and researchers to explore how different spatial features 
in satellite imagery are represented in the frequency domain and how filtering these frequencies can enhance specific features.

## Key Features
- Upload and process satellite imagery in various formats (JPG, PNG, GeoTIFF)
- Visualize the frequency domain representation using Fast Fourier Transform (FFT)
- Apply customizable filters to highlight or suppress spatial features
- Compare original and processed images side-by-side
- Download filtered results for further analysis
- Advanced features like NDVI computation and texture classification
- AI-powered analysis to interpret results and aid decision-making

## Technology
This application is built with Python using the Streamlit framework, with scientific computing libraries 
including NumPy, SciPy, and scikit-image for image processing operations. OpenAI's advanced models 
provide AI-assisted analysis and interpretation.
"""

# Documentation on frequency domain filtering
FREQUENCY_DOMAIN_GUIDE = """
# Understanding Frequency Domain Filtering

## What is the Frequency Domain?
Every image can be represented as a sum of sinusoidal components of different frequencies. 
The **frequency domain** is an alternative representation that shows how much of each frequency component is present in the image.

In an image:
- **Low frequencies** represent smooth areas and gradual changes
- **High frequencies** represent edges, details, and noise
- **Middle frequencies** often correspond to textures and patterns

## The Fourier Transform
The Fast Fourier Transform (FFT) converts an image from its spatial representation (pixel values) 
into its frequency components. In the FFT visualization:

- The **center** of the spectrum represents low frequencies
- The **periphery** represents high frequencies
- **Brighter spots** indicate stronger frequency components in that direction

## Types of Filters

### Low-Pass Filter
A low-pass filter preserves low frequencies while attenuating high frequencies.
- **Effect**: Smooths the image, reducing noise and fine details
- **Applications**: Noise reduction, removing small-scale features, highlighting broad patterns
- **When to use**: When you want to focus on large-scale features or reduce noise

### High-Pass Filter
A high-pass filter preserves high frequencies while attenuating low frequencies.
- **Effect**: Enhances edges and fine details while removing gradual variations
- **Applications**: Edge detection, feature extraction, enhancing boundaries
- **When to use**: When you want to highlight boundaries, edges, or fine details

### Band-Stop Filter
A band-stop (or notch) filter removes a specific range of frequencies.
- **Effect**: Removes periodic patterns or noise of specific scales
- **Applications**: Removing sensor noise, eliminating grid patterns, artifact reduction
- **When to use**: When your image has specific periodic noise or patterns you want to remove

## Interpreting Results
When comparing the original and filtered images:

- **Highlighted features** in the filtered image indicate elements that were preserved by the filter
- **Missing features** in the filtered image indicate elements that were removed by the filter
- **New artifacts** may appear due to the filtering process, especially without Gaussian tapering
"""

# Tutorial on using the application
TUTORIAL = """
# How to Use the Remote Sensing Data Analyzer

## Quick Start Guide

### Step 1: Upload an Image
- Click the "Upload an image" button in the sidebar
- Select a JPG, PNG, or GeoTIFF file from your computer
- For GeoTIFF files with multiple bands, select the band you want to analyze

### Step 2: Select a Filter
- Choose a filter type from the radio buttons (Low-pass, High-pass, or Band-stop)
- Adjust the filter parameters using the sliders:
  - For Low-pass and High-pass: adjust the cutoff radius
  - For Band-stop: adjust both inner and outer radius
- Toggle "Apply Gaussian tapering" to reduce ringing artifacts

### Step 3: Analyze Results
- Compare the original image, FFT spectrum, and filtered result side-by-side
- Use the AI Analysis button for an automated interpretation of the results
- For GeoTIFF files, explore additional features like NDVI computation or texture classification

### Step 4: Export Results
- Click "Download Filtered Image" to save the processed image
- Use "Generate Report" to create a comprehensive analysis report

## Example Workflows

### Example 1: Enhancing Urban Features
1. Upload a satellite image of an urban area
2. Apply a High-pass filter with cutoff radius at 20-30% of max
3. Observe how roads, buildings, and infrastructure are highlighted
4. Use AI Analysis to identify urban features

### Example 2: Detecting Agricultural Patterns
1. Upload a GeoTIFF of agricultural land
2. If available, compute NDVI to see vegetation health
3. Apply a Band-stop filter to remove sensor noise or artifacts
4. Look for patterns in field boundaries or irrigation systems
5. Generate a report for documentation

### Example 3: Analyzing Natural Features
1. Upload an image containing natural landscapes
2. Apply a Low-pass filter to highlight broader landforms
3. Then try a High-pass filter to detect boundaries like shorelines or forest edges
4. Compare the different filtered outputs to understand the landscape composition

## Advanced Tips
- For noisy images, start with a Low-pass filter to reduce noise before other analysis
- Use the texture classification for distinguishing different land cover types
- Experiment with different cutoff radii to find the optimal filter settings
- When working with GeoTIFF, analyze different bands to highlight specific features
"""

# Examples and case studies
EXAMPLES = """
# Examples and Case Studies

## Case Study 1: Urban Development Monitoring
Frequency domain analysis can be particularly useful for monitoring urban development and infrastructure.

**Process:**
1. Upload high-resolution satellite imagery of urban areas
2. Apply a high-pass filter to emphasize edges and linear features
3. Use texture classification to distinguish between different urban zones
4. Look for patterns indicating development, such as regular grid patterns of new roads

**Key Findings:**
- High-frequency components often correspond to road networks and building edges
- Different urban densities show distinct texture patterns
- Periodic patterns in the FFT spectrum may indicate planned development vs. organic growth

## Case Study 2: Agricultural Monitoring
Frequency analysis helps in assessing crop health and agricultural practices.

**Process:**
1. Upload multi-band satellite imagery of agricultural regions
2. Compute NDVI to assess vegetation health
3. Apply frequency filtering to detect field boundaries and irrigation patterns
4. Compare filtered images over time to monitor changes

**Key Findings:**
- Regular patterns in the FFT spectrum often indicate human agricultural activity
- Low-pass filtering can help identify broader zones of similar crop types
- Band-stop filtering can remove sensor artifacts that might interfere with analysis

## Case Study 3: Coastal Change Analysis
Monitoring coastlines and water bodies with frequency domain techniques.

**Process:**
1. Upload imagery of coastal regions
2. Apply high-pass filtering to enhance the land-water boundary
3. Use band-stop filtering to remove wave patterns if necessary
4. Compare results over time to detect erosion or deposition

**Key Findings:**
- Water bodies typically appear as low-frequency regions
- Coastlines and shorelines are enhanced in high-pass filtered images
- Periodic wave patterns in water can be visible in the FFT spectrum
"""

# Interpretation guide
INTERPRETATION_GUIDE = """
# Interpretation Guide: Making Decisions from Results

## Understanding Filtered Outputs

### For Low-Pass Filtered Images:
- **Smooth areas** represent consistent, homogeneous regions like water bodies, uniform vegetation, or built-up areas
- **Blurred boundaries** indicate transitions between different land cover types
- **Loss of fine detail** is expected; focus on the broader patterns revealed

### For High-Pass Filtered Images:
- **Bright lines** often represent boundaries, roads, or edges between different features
- **Highlighted textures** can indicate different vegetation types or urban densities
- **Dark areas** typically represent homogeneous regions with little internal variation

### For Band-Stop Filtered Images:
- **Removed periodic patterns** might represent eliminated sensor noise or artifacts
- **Preservation of both low and high frequencies** allows seeing both broad patterns and fine details
- **Compare with original** to identify what specific features were removed

## From Analysis to Decision Making

### For Environmental Monitoring:
1. **Identify anomalies** in high-pass filtered images that may indicate disturbances
2. **Track boundaries** between natural systems to monitor encroachment or recovery
3. **Use NDVI results** to assess vegetation health and stress
4. **Look for patterns** in frequency components that might indicate natural vs. human influence

### For Urban Planning:
1. **Analyze development patterns** visible in high-frequency components
2. **Identify infrastructure** highlighted by edge detection
3. **Assess density and arrangement** of built-up areas using texture classification
4. **Monitor changes over time** by comparing frequency components of temporal images

### For Disaster Assessment:
1. **Detect changes** in land cover by comparing before/after high-pass filtered images
2. **Identify damaged infrastructure** as disruptions in regular patterns
3. **Assess extent of impact** by analyzing changes in both low and high frequencies
4. **Prioritize response** based on detected anomalies and pattern disruptions

## Best Practices for Decision Making
1. **Validate with multiple filters** - compare results from different filtering approaches
2. **Incorporate contextual knowledge** - combine frequency analysis with your expertise
3. **Consider temporal aspects** - how do patterns change over time?
4. **Use AI assistance** - leverage the AI analysis feature for additional insights
5. **Generate comprehensive reports** - document your analysis process and findings
6. **Ground-truth when possible** - verify findings with other data sources if available
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
    sections = {
        "about": ABOUT_APP,
        "frequency_domain": FREQUENCY_DOMAIN_GUIDE,
        "tutorial": TUTORIAL,
        "examples": EXAMPLES,
        "interpretation": INTERPRETATION_GUIDE
    }
    
    return sections.get(section, "Documentation section not found.")