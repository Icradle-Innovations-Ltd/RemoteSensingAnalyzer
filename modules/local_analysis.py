"""
Local Analysis module for Remote Sensing Data Analyzer
Provides functions for analyzing images without relying on external API services
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage, stats
from skimage import filters, measure, feature, exposure, color, segmentation
import cv2

def analyze_image_content(image):
    """
    Analyze the content of the image and provide a comprehensive summary
    without relying on external AI services
    
    Parameters:
    ----------
    image : ndarray
        Input image to analyze
    
    Returns:
    -------
    analysis : dict
        Dictionary containing analysis results and insights
    """
    # Convert to grayscale for analysis if needed
    if len(image.shape) > 2:
        gray_img = np.mean(image, axis=2)
    else:
        gray_img = image.copy()
    
    # Normalize
    gray_img = (gray_img - np.min(gray_img)) / (np.max(gray_img) - np.min(gray_img) + 1e-8)
    
    # Analysis results dictionary
    analysis = {}
    
    # Basic image statistics
    analysis['basic_stats'] = {
        'resolution': image.shape,
        'min_value': float(np.min(gray_img)),
        'max_value': float(np.max(gray_img)),
        'mean_value': float(np.mean(gray_img)),
        'std_dev': float(np.std(gray_img))
    }
    
    # Contrast and brightness analysis
    contrast = np.std(gray_img) * 100  # Scale for readability
    brightness = np.mean(gray_img) * 100  # Scale for readability
    
    analysis['visual_quality'] = {
        'contrast': float(contrast),
        'brightness': float(brightness),
        'dynamic_range': float(np.max(gray_img) - np.min(gray_img))
    }
    
    # Determine if the image has good, low, or high contrast
    contrast_quality = ""
    if contrast < 10:
        contrast_quality = "Low"
    elif contrast > 30:
        contrast_quality = "High"
    else:
        contrast_quality = "Good"
    analysis['visual_quality']['contrast_quality'] = contrast_quality
    
    # Determine if the image is dark, well-lit, or bright
    brightness_quality = ""
    if brightness < 30:
        brightness_quality = "Dark"
    elif brightness > 70:
        brightness_quality = "Bright"
    else:
        brightness_quality = "Well-lit"
    analysis['visual_quality']['brightness_quality'] = brightness_quality
    
    # Texture analysis
    grad_x = filters.sobel_h(gray_img)
    grad_y = filters.sobel_v(gray_img)
    gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    
    texture_variety = np.std(gradient_magnitude) * 100  # Scale for readability
    texture_energy = np.sum(gradient_magnitude**2) / gray_img.size
    
    # Local Binary Pattern for texture
    from skimage.feature import local_binary_pattern
    lbp = local_binary_pattern(gray_img, P=8, R=1, method='uniform')
    
    # Calculate texture entropy
    lbp_hist, _ = np.histogram(lbp, bins=10, range=(0, 10), density=True)
    texture_entropy = stats.entropy(lbp_hist + 1e-8)
    
    analysis['texture'] = {
        'complexity': float(texture_variety),
        'energy': float(texture_energy),
        'entropy': float(texture_entropy)
    }
    
    # Determine the texture type
    if texture_variety < 0.5:
        analysis['texture']['type'] = 'Smooth'
    elif texture_variety < 2.0:
        analysis['texture']['type'] = 'Moderate'
    else:
        analysis['texture']['type'] = 'Complex'
    
    # Frequency domain analysis
    f_transform = np.fft.fft2(gray_img)
    f_shift = np.fft.fftshift(f_transform)
    f_magnitude = np.log(np.abs(f_shift) + 1)
    
    # Analyze frequency distribution
    f_energy_low = np.sum(f_magnitude[f_magnitude.shape[0]//2-10:f_magnitude.shape[0]//2+10, 
                                      f_magnitude.shape[1]//2-10:f_magnitude.shape[1]//2+10])
    f_energy_total = np.sum(f_magnitude)
    f_energy_high = f_energy_total - f_energy_low
    
    analysis['frequency'] = {
        'low_frequency_energy': float(f_energy_low / f_energy_total),
        'high_frequency_energy': float(f_energy_high / f_energy_total)
    }
    
    # Determine if image has more low or high frequency content
    if analysis['frequency']['low_frequency_energy'] > 0.7:
        analysis['frequency']['dominant_range'] = 'Low frequency dominated'
    elif analysis['frequency']['high_frequency_energy'] > 0.7:
        analysis['frequency']['dominant_range'] = 'High frequency dominated'
    else:
        analysis['frequency']['dominant_range'] = 'Balanced frequency content'
    
    # Edge analysis
    edges = feature.canny(gray_img, sigma=1.0)
    edge_density = np.sum(edges) / edges.size
    
    analysis['edges'] = {
        'density': float(edge_density),
        'total_count': int(np.sum(edges))
    }
    
    # Determine edge characteristics
    if edge_density < 0.05:
        analysis['edges']['characteristic'] = 'Few edges'
    elif edge_density < 0.15:
        analysis['edges']['characteristic'] = 'Moderate edges'
    else:
        analysis['edges']['characteristic'] = 'Many edges'
    
    # Segmentation-based analysis
    # Use SLIC superpixels to segment the image
    if len(image.shape) > 2:
        segments = segmentation.slic(image, n_segments=50, compactness=10, sigma=1)
    else:
        segments = segmentation.slic(np.stack([gray_img] * 3, axis=-1), 
                                  n_segments=50, compactness=10, sigma=1)
    
    num_segments = len(np.unique(segments))
    
    # Calculate region statistics
    regions = measure.regionprops(segments + 1)
    region_sizes = [region.area for region in regions]
    region_size_variation = np.std(region_sizes) / np.mean(region_sizes)
    
    analysis['segmentation'] = {
        'region_count': num_segments,
        'size_variation': float(region_size_variation)
    }
    
    # Determine homogeneity/heterogeneity
    if region_size_variation < 0.5:
        analysis['segmentation']['homogeneity'] = 'Highly homogeneous'
    elif region_size_variation < 1.0:
        analysis['segmentation']['homogeneity'] = 'Moderately homogeneous'
    else:
        analysis['segmentation']['homogeneity'] = 'Heterogeneous'
    
    # Line detection (for built features)
    lines = cv2.HoughLinesP(edges.astype(np.uint8), 1, np.pi/180, 
                           threshold=25, minLineLength=10, maxLineGap=5)
    
    if lines is not None:
        num_lines = len(lines)
        
        # Calculate line orientations
        orientations = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 != 0:  # Avoid division by zero
                angle = np.arctan((y2 - y1) / (x2 - x1)) * 180 / np.pi
                orientations.append(angle % 180)  # Convert to 0-180 range
        
        # Check if there are dominant orientations (built environment often has regular patterns)
        if orientations:
            hist, bin_edges = np.histogram(orientations, bins=18, range=(0, 180))
            max_count = np.max(hist)
            regularity = max_count / len(orientations)
            
            analysis['linear_features'] = {
                'count': num_lines,
                'regularity': float(regularity)
            }
            
            # Determine if there's a dominant orientation
            if regularity > 0.4:
                dominant_bin = np.argmax(hist)
                dominant_angle = (bin_edges[dominant_bin] + bin_edges[dominant_bin + 1]) / 2
                analysis['linear_features']['dominant_orientation'] = float(dominant_angle)
                
                # Determine orientation category
                if 0 <= dominant_angle < 22.5 or 157.5 <= dominant_angle < 180:
                    orientation_category = "East-West"
                elif 22.5 <= dominant_angle < 67.5:
                    orientation_category = "Northeast-Southwest"
                elif 67.5 <= dominant_angle < 112.5:
                    orientation_category = "North-South"
                else:  # 112.5 <= dominant_angle < 157.5
                    orientation_category = "Northwest-Southeast"
                    
                analysis['linear_features']['orientation_category'] = orientation_category
        else:
            analysis['linear_features'] = {
                'count': 0,
                'regularity': 0.0
            }
    else:
        analysis['linear_features'] = {
            'count': 0,
            'regularity': 0.0
        }
    
    # Content classification
    # Classify the image content based on all the features analyzed
    
    # Detect water (dark, smooth areas)
    potential_water = (gray_img < 0.3) & (gradient_magnitude < 0.05)
    water_percentage = np.sum(potential_water) / potential_water.size * 100
    
    # Detect vegetation (textured, moderate brightness)
    potential_vegetation = (gray_img > 0.3) & (gray_img < 0.7) & (gradient_magnitude > 0.05)
    vegetation_percentage = np.sum(potential_vegetation) / potential_vegetation.size * 100
    
    # Detect built/urban areas (high edge density, regular patterns)
    urban_indicator = edge_density
    if 'regularity' in analysis.get('linear_features', {}):
        urban_indicator *= (1 + analysis['linear_features']['regularity'])
    
    urban_likelihood = min(urban_indicator * 100, 100)
    
    # Natural vs built environment assessment
    natural_indicators = [
        water_percentage / 100,
        vegetation_percentage / 100,
        1 - edge_density * 5,  # Lower edge density suggests natural
        1 - analysis['linear_features'].get('regularity', 0)  # Lower regularity suggests natural
    ]
    
    natural_likelihood = np.mean(natural_indicators) * 100
    built_likelihood = 100 - natural_likelihood
    
    analysis['content_classification'] = {
        'water_percentage': float(water_percentage),
        'vegetation_percentage': float(vegetation_percentage),
        'urban_likelihood': float(urban_likelihood),
        'natural_vs_built': {
            'natural_likelihood': float(natural_likelihood),
            'built_likelihood': float(built_likelihood)
        }
    }
    
    # Generate the final content summary
    if natural_likelihood > 70:
        analysis['content_classification']['primary_category'] = 'Natural landscape'
    elif built_likelihood > 70:
        analysis['content_classification']['primary_category'] = 'Built environment'
    else:
        analysis['content_classification']['primary_category'] = 'Mixed natural and built environment'
    
    # Add more detailed classification
    if water_percentage > 30:
        analysis['content_classification']['subcategory'] = 'Water-dominated'
    elif vegetation_percentage > 30:
        analysis['content_classification']['subcategory'] = 'Vegetation-dominated'
    elif urban_likelihood > 50:
        analysis['content_classification']['subcategory'] = 'Urban/developed'
    else:
        analysis['content_classification']['subcategory'] = 'Mixed terrain'
    
    return analysis

def generate_analysis_report(analysis):
    """
    Generate a comprehensive analysis report based on the local image analysis
    
    Parameters:
    ----------
    analysis : dict
        Analysis results from analyze_image_content
    
    Returns:
    -------
    report : str
        Markdown formatted report
    """
    # Start with report header
    report = """# Image Content Analysis Report

## Summary

"""
    
    # Summary of primary content
    if 'content_classification' in analysis:
        primary = analysis['content_classification'].get('primary_category', 'Unknown')
        sub = analysis['content_classification'].get('subcategory', '')
        
        report += f"This image predominantly shows a **{primary.lower()}**"
        if sub:
            report += f", specifically a **{sub.lower()}** area"
        report += ".\n\n"
        
        # Add natural vs built assessment
        if 'natural_vs_built' in analysis['content_classification']:
            nat = analysis['content_classification']['natural_vs_built']['natural_likelihood']
            built = analysis['content_classification']['natural_vs_built']['built_likelihood']
            
            report += f"The content is approximately **{nat:.1f}%** natural features "
            report += f"and **{built:.1f}%** built/human-made features.\n\n"
    
    # Image characteristics
    report += "## Image Characteristics\n\n"
    
    if 'basic_stats' in analysis:
        res = analysis['basic_stats']['resolution']
        report += f"- **Resolution:** {res[0]} × {res[1]} pixels\n"
    
    if 'visual_quality' in analysis:
        contrast = analysis['visual_quality'].get('contrast_quality', 'Unknown')
        brightness = analysis['visual_quality'].get('brightness_quality', 'Unknown')
        
        report += f"- **Visual Quality:** {contrast} contrast, {brightness} image\n"
    
    if 'texture' in analysis:
        texture_type = analysis['texture'].get('type', 'Unknown')
        report += f"- **Texture:** {texture_type}\n"
    
    if 'frequency' in analysis:
        freq_range = analysis['frequency'].get('dominant_range', 'Unknown')
        report += f"- **Frequency Content:** {freq_range}\n"
    
    if 'edges' in analysis:
        edge_char = analysis['edges'].get('characteristic', 'Unknown')
        report += f"- **Edge Density:** {edge_char}\n"
    
    if 'segmentation' in analysis:
        homogeneity = analysis['segmentation'].get('homogeneity', 'Unknown')
        report += f"- **Region Homogeneity:** {homogeneity}\n"
    
    # Add linear features if available
    if 'linear_features' in analysis and analysis['linear_features']['count'] > 0:
        report += "\n## Linear Features\n\n"
        
        count = analysis['linear_features']['count']
        report += f"- **Linear Feature Count:** {count}\n"
        
        if 'regularity' in analysis['linear_features']:
            reg = analysis['linear_features']['regularity']
            if reg < 0.2:
                pattern = "Irregular"
            elif reg < 0.4:
                pattern = "Somewhat regular"
            else:
                pattern = "Highly regular"
                
            report += f"- **Pattern Regularity:** {pattern}\n"
        
        if 'orientation_category' in analysis['linear_features']:
            orientation = analysis['linear_features']['orientation_category']
            report += f"- **Dominant Orientation:** {orientation}\n"
    
    # Content composition
    report += "\n## Content Composition\n\n"
    
    if 'content_classification' in analysis:
        water = analysis['content_classification'].get('water_percentage', 0)
        veg = analysis['content_classification'].get('vegetation_percentage', 0)
        urban = analysis['content_classification'].get('urban_likelihood', 0)
        
        report += f"- **Water Features:** Approximately {water:.1f}% of the image\n"
        report += f"- **Vegetation:** Approximately {veg:.1f}% of the image\n"
        report += f"- **Urban/Built Features:** Likelihood of {urban:.1f}%\n"
    
    # Interpretation section
    report += "\n## Interpretation\n\n"
    
    # Add interpretations based on the analysis results
    
    # Texture interpretation
    if 'texture' in analysis:
        texture_type = analysis['texture'].get('type', '').lower()
        texture_entropy = analysis['texture'].get('entropy', 0)
        
        if texture_type == 'smooth':
            report += "- The image shows a **relatively uniform area** with minimal texture variation.\n"
        elif texture_type == 'moderate':
            report += "- The image contains **moderate textural complexity**, suggesting a mix of features.\n"
        elif texture_type == 'complex':
            report += "- The image has **high textural complexity**, indicating diverse surface features.\n"
        
        if texture_entropy > 2.0:
            report += "- The **high texture entropy** suggests significant spatial diversity or complexity.\n"
    
    # Edge and pattern interpretation
    if 'edges' in analysis and 'linear_features' in analysis:
        edge_density = analysis['edges'].get('density', 0)
        linear_count = analysis['linear_features'].get('count', 0)
        regularity = analysis['linear_features'].get('regularity', 0)
        
        if edge_density > 0.15 and linear_count > 20 and regularity > 0.4:
            report += "- The **high edge density** and **regular linear patterns** strongly suggest human-made structures such as urban areas or agricultural fields.\n"
        elif edge_density > 0.1 and linear_count > 10:
            report += "- The presence of **defined edges** and **linear features** suggests human influence on the landscape.\n"
        elif edge_density < 0.05 and linear_count < 5:
            report += "- The **low edge density** and **few linear features** suggest a predominantly natural landscape with minimal human development.\n"
    
    # Frequency domain interpretation
    if 'frequency' in analysis:
        low_freq = analysis['frequency'].get('low_frequency_energy', 0)
        high_freq = analysis['frequency'].get('high_frequency_energy', 0)
        
        if low_freq > 0.7:
            report += "- The dominance of **low-frequency content** indicates large-scale patterns or gradual transitions, typical of natural landscapes or atmospheric effects.\n"
        elif high_freq > 0.7:
            report += "- The prevalence of **high-frequency content** suggests fine details, sharp boundaries, or noise, often associated with urban environments or detailed textures.\n"
    
    # Final content interpretation
    if 'content_classification' in analysis:
        primary = analysis['content_classification'].get('primary_category', '').lower()
        subcategory = analysis['content_classification'].get('subcategory', '').lower()
        
        if 'natural landscape' in primary:
            if 'water' in subcategory:
                report += "- This image likely shows a **body of water** such as a lake, river, or coastal area, with minimal human development.\n"
            elif 'vegetation' in subcategory:
                report += "- This image primarily depicts **vegetated terrain** such as forests, grasslands, or other natural vegetation cover.\n"
            else:
                report += "- This image shows a predominantly **natural landscape** with minimal human modification.\n"
        
        elif 'built environment' in primary:
            report += "- This image shows significant **human development**, likely an urban or suburban area, transportation infrastructure, or agricultural system.\n"
        
        elif 'mixed' in primary:
            report += "- This image depicts a **mixed landscape** where natural and human-made features coexist, such as rural settlements, agricultural areas adjacent to natural features, or urban areas with parks/vegetation.\n"
    
    return report

def fetch_image_from_url(url):
    """
    Fetch an image from a URL
    
    Parameters:
    ----------
    url : str
        URL of the image to fetch
    
    Returns:
    -------
    image : ndarray or None
        Image as numpy array if successful, None otherwise
    error : str or None
        Error message if unsuccessful, None otherwise
    """
    try:
        # Need to import requests for this function
        import requests
        from PIL import Image
        import io
        
        # Send a GET request to the URL
        response = requests.get(url, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Read the image from the response content
            image = Image.open(io.BytesIO(response.content))
            
            # Convert PIL Image to numpy array
            image_array = np.array(image)
            
            return image_array, None
        else:
            return None, f"Failed to fetch image: HTTP status code {response.status_code}"
            
    except Exception as e:
        return None, f"Error fetching image: {str(e)}"