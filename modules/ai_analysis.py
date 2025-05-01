import os
import base64
import json
import io
from PIL import Image
import numpy as np
from openai import OpenAI

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def encode_image_to_base64(image_array):
    """
    Convert a numpy array image to base64 encoded string
    """
    # Convert numpy array to PIL Image
    if image_array.dtype != np.uint8:
        # Normalize to 0-255 range
        image_array = (image_array * 255).astype(np.uint8)
    
    if len(image_array.shape) == 2:
        # Convert grayscale to RGB
        pil_image = Image.fromarray(image_array, mode='L').convert('RGB')
    else:
        pil_image = Image.fromarray(image_array)
        
    # Save to byte buffer
    buffer = io.BytesIO()
    pil_image.save(buffer, format="JPEG")
    
    # Encode as base64
    base64_encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return base64_encoded

def analyze_satellite_image(original_image, filtered_image, filter_type):
    """
    Analyze satellite imagery using OpenAI's GPT-4 Vision capabilities
    
    Parameters:
    ----------
    original_image : ndarray
        The original image
    filtered_image : ndarray
        The filtered image after processing
    filter_type : str
        Type of filter applied (Low-pass, High-pass, or Band-stop)
    
    Returns:
    -------
    analysis : dict
        Dictionary containing analysis results
    """
    # Encode images to base64
    original_base64 = encode_image_to_base64(original_image)
    filtered_base64 = encode_image_to_base64(filtered_image)
    
    try:
        # Prepare system prompt
        system_prompt = """You are an expert remote sensing analyst specializing in satellite imagery interpretation. 
        You will be shown an original satellite image and a filtered version using frequency domain processing.
        Analyze the images and provide insights about:
        1. Visible features and land cover types
        2. How the filter has enhanced or suppressed certain features
        3. Environmental patterns or anomalies visible
        4. Potential applications of the filtered result
        5. Recommendations for further analysis
        
        Format your response as a structured JSON object with the following keys:
        - "features_detected": List of identified features
        - "filter_effects": How the filter affected the image
        - "environmental_patterns": Any patterns or anomalies detected
        - "applications": Potential uses for this processed image
        - "recommendations": Suggested next steps for analysis
        - "summary": Brief natural language summary of findings
        """
        
        # Prepare the messages
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"I'm analyzing satellite imagery with a {filter_type} filter. Please provide an assessment of what's visible in both the original and filtered images. What insights can be drawn from the filtered result?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{original_base64}",
                            "detail": "high"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{filtered_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        # Make request to OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        # Parse response
        analysis = json.loads(response.choices[0].message.content)
        return analysis
        
    except Exception as e:
        # Return error information
        return {
            "error": str(e),
            "summary": "An error occurred during analysis. Please check your API key or try again later."
        }

def generate_full_report(image_info, filter_params, analysis_results):
    """
    Generate a comprehensive report combining image metadata, filter parameters,
    and AI analysis results
    
    Parameters:
    ----------
    image_info : dict
        Dictionary containing image metadata
    filter_params : dict
        Dictionary containing filter parameters
    analysis_results : dict
        Dictionary containing AI analysis results
    
    Returns:
    -------
    report : str
        Markdown formatted report
    """
    # Build markdown report
    report = """# Satellite Image Analysis Report
    
## Image Information
"""
    # Add image info
    for key, value in image_info.items():
        report += f"- **{key.title()}**: {value}\n"
    
    report += """
## Processing Parameters
"""
    # Add filter info
    filter_type = filter_params.get('type', 'Unknown')
    report += f"- **Filter Type**: {filter_type}\n"
    
    if filter_type == "Low-pass":
        report += f"- **Cutoff Radius**: {filter_params.get('cutoff_radius')}\n"
    elif filter_type == "High-pass":
        report += f"- **Cutoff Radius**: {filter_params.get('cutoff_radius')}\n"
    elif filter_type == "Band-stop":
        report += f"- **Inner Radius**: {filter_params.get('inner_radius')}\n"
        report += f"- **Outer Radius**: {filter_params.get('outer_radius')}\n"
    
    report += f"- **Gaussian Tapering**: {filter_params.get('gaussian_tapering', False)}\n"
    
    # Add AI analysis if available
    if analysis_results and 'error' not in analysis_results:
        report += """
## AI Analysis Results

### Features Detected
"""
        for feature in analysis_results.get('features_detected', []):
            report += f"- {feature}\n"
        
        report += """
### Filter Effects
"""
        for effect in analysis_results.get('filter_effects', []):
            report += f"- {effect}\n"
        
        report += """
### Environmental Patterns
"""
        for pattern in analysis_results.get('environmental_patterns', []):
            report += f"- {pattern}\n"
        
        report += """
### Potential Applications
"""
        for app in analysis_results.get('applications', []):
            report += f"- {app}\n"
        
        report += """
### Recommendations
"""
        for rec in analysis_results.get('recommendations', []):
            report += f"- {rec}\n"
        
        report += """
## Summary
"""
        report += analysis_results.get('summary', 'No summary available.')
        
    else:
        # No AI analysis available
        report += """
## AI Analysis
AI analysis unavailable or encountered an error.
"""
    
    # Add timestamp
    import datetime
    report += f"\n\n*Report generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    
    return report