"""
AI Provider module for the Remote Sensing Data Analyzer
Contains implementation for different AI models (OpenAI, Anthropic, xAI)
"""

import os
import sys
import json
import base64
from io import BytesIO
import numpy as np
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check for available AI providers
AVAILABLE_PROVIDERS = []

# OpenAI
try:
    from openai import OpenAI
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if openai_api_key and openai_api_key != "your_openai_api_key_here":
        AVAILABLE_PROVIDERS.append("openai")
        openai_client = OpenAI(api_key=openai_api_key)
except (ImportError, Exception):
    pass

# Anthropic
try:
    from anthropic import Anthropic
    anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
    if anthropic_api_key and anthropic_api_key != "your_anthropic_api_key_here":
        AVAILABLE_PROVIDERS.append("anthropic")
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        anthropic_client = Anthropic(api_key=anthropic_api_key)
except (ImportError, Exception):
    pass

# xAI / Grok
try:
    xai_api_key = os.environ.get('XAI_API_KEY')
    if xai_api_key and xai_api_key != "your_xai_api_key_here":
        AVAILABLE_PROVIDERS.append("xai")
        xai_client = OpenAI(base_url="https://api.x.ai/v1", api_key=xai_api_key)
except (ImportError, Exception):
    pass

def encode_image_to_base64(image_array):
    """
    Convert a numpy array image to base64 encoded string
    """
    # Convert to uint8 if not already
    if image_array.dtype != np.uint8:
        # Scale to 0-255 range
        if image_array.max() <= 1.0:
            image_array = (image_array * 255).astype(np.uint8)
        else:
            image_array = image_array.astype(np.uint8)
    
    # Convert to RGB if grayscale
    if len(image_array.shape) == 2:
        # Convert grayscale to RGB
        pil_img = Image.fromarray(image_array).convert('RGB')
    else:
        pil_img = Image.fromarray(image_array)
    
    # Save to bytes
    buffered = BytesIO()
    pil_img.save(buffered, format="JPEG")
    
    # Encode as base64
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def analyze_satellite_image(original_image, filtered_image, filter_type, provider="openai"):
    """
    Analyze satellite imagery using multiple AI model options
    
    Parameters:
    ----------
    original_image : ndarray
        The original image
    filtered_image : ndarray
        The filtered image after processing
    filter_type : str
        Type of filter applied (Low-pass, High-pass, or Band-stop)
    provider : str
        AI provider to use ('openai', 'anthropic', 'xai')
    
    Returns:
    -------
    analysis : dict
        Dictionary containing analysis results
    """
    try:
        # Check if the specified provider is available
        if provider not in AVAILABLE_PROVIDERS:
            available_options = ", ".join(AVAILABLE_PROVIDERS) if AVAILABLE_PROVIDERS else "none"
            return {
                "error": f"AI provider '{provider}' is not available. Available options: {available_options}",
                "features_detected": [],
                "filter_effects": [],
                "environmental_patterns": [],
                "applications": [],
                "recommendations": [],
                "summary": f"Error: '{provider}' API key not configured or invalid."
            }
            
        # Convert images to base64 for API
        original_base64 = encode_image_to_base64(original_image)
        filtered_base64 = encode_image_to_base64(filtered_image)
        
        system_prompt = f"""
        You are an expert remote sensing analyst specializing in satellite imagery analysis.
        You will be provided with two images: an original satellite image and a filtered version using a {filter_type} filter.
        
        Analyze both images and provide the following information in a structured JSON response:
        
        1. Features detected in the imagery
        2. Effects of the {filter_type} filtering on the image analysis
        3. Environmental patterns visible in the imagery
        4. Potential applications of this analysis
        5. Recommendations for further analysis
        6. A brief summary of your findings
        
        Format your response as a JSON object with these keys:
        {{
            "features_detected": [list of features],
            "filter_effects": [list of effects],
            "environmental_patterns": [list of patterns],
            "applications": [list of applications],
            "recommendations": [list of recommendations],
            "summary": "brief summary"
        }}
        """
        
        # Choose provider for analysis
        if provider == "openai":
            return analyze_with_openai(original_base64, filtered_base64, system_prompt)
        elif provider == "anthropic":
            return analyze_with_anthropic(original_base64, filtered_base64, system_prompt)
        elif provider == "xai":
            return analyze_with_xai(original_base64, filtered_base64, system_prompt)
        else:
            return {
                "error": f"Unknown provider: {provider}",
                "features_detected": [],
                "filter_effects": [],
                "environmental_patterns": [],
                "applications": [],
                "recommendations": [],
                "summary": "Error: Unknown AI provider specified."
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "features_detected": [],
            "filter_effects": [],
            "environmental_patterns": [],
            "applications": [],
            "recommendations": [],
            "summary": f"Error during analysis: {str(e)}"
        }

def analyze_with_openai(original_base64, filtered_base64, system_prompt):
    """
    Analyze satellite imagery using OpenAI's GPT-4 Vision
    """
    try:
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Here are the original and filtered satellite images. Provide analysis according to the instructions."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{original_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{filtered_base64}"}}
                ]}
            ],
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Parse JSON response
        analysis_results = json.loads(response.choices[0].message.content)
        return analysis_results
        
    except Exception as e:
        return {
            "error": f"OpenAI API error: {str(e)}",
            "features_detected": [],
            "filter_effects": [],
            "environmental_patterns": [],
            "applications": [],
            "recommendations": [],
            "summary": f"Error with OpenAI analysis: {str(e)}"
        }

def analyze_with_anthropic(original_base64, filtered_base64, system_prompt):
    """
    Analyze satellite imagery using Anthropic's Claude
    """
    try:
        # Create messages with the images embedded
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": system_prompt + "\n\nHere are the original and filtered satellite images. Provide analysis according to the instructions."},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": original_base64}},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": filtered_base64}}
                ]
            }
        ]
        
        # Make API call
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=messages,
            max_tokens=1000
        )
        
        # Parse JSON response
        try:
            # Extract JSON from the response
            text_content = response.content[0].text
            # Find JSON content (may be embedded in explanatory text)
            json_start = text_content.find('{')
            json_end = text_content.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = text_content[json_start:json_end]
                analysis_results = json.loads(json_str)
                return analysis_results
            else:
                # If JSON parsing fails, create a structured response from the text
                return {
                    "error": "Failed to parse JSON from Anthropic response",
                    "features_detected": [],
                    "filter_effects": [],
                    "environmental_patterns": [],
                    "applications": [],
                    "recommendations": [],
                    "summary": text_content[:500]  # Truncate long responses
                }
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON response from Anthropic",
                "features_detected": [],
                "filter_effects": [],
                "environmental_patterns": [],
                "applications": [],
                "recommendations": [],
                "summary": response.content[0].text[:500]  # Truncate long responses
            }
            
    except Exception as e:
        return {
            "error": f"Anthropic API error: {str(e)}",
            "features_detected": [],
            "filter_effects": [],
            "environmental_patterns": [],
            "applications": [],
            "recommendations": [],
            "summary": f"Error with Anthropic analysis: {str(e)}"
        }

def analyze_with_xai(original_base64, filtered_base64, system_prompt):
    """
    Analyze satellite imagery using xAI's Grok
    """
    try:
        # Make API call using xAI client (similar to OpenAI pattern)
        response = xai_client.chat.completions.create(
            model="grok-2-vision-1212",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Here are the original and filtered satellite images. Provide analysis according to the instructions."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{original_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{filtered_base64}"}}
                ]}
            ],
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Parse JSON response
        analysis_results = json.loads(response.choices[0].message.content)
        return analysis_results
        
    except Exception as e:
        return {
            "error": f"xAI API error: {str(e)}",
            "features_detected": [],
            "filter_effects": [],
            "environmental_patterns": [],
            "applications": [],
            "recommendations": [],
            "summary": f"Error with xAI analysis: {str(e)}"
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
    # Format current date and time
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Start with report header
    report = f"""
# Satellite Image Analysis Report
**Generated:** {timestamp}

## Image Information
"""

    # Add image information
    if image_info:
        report += f"""
- **Filename:** {image_info.get('filename', 'Unknown')}
- **Image Type:** {image_info.get('type', 'Unknown')}
- **Dimensions:** {image_info.get('dimensions', 'Unknown')}
"""
        # Add GeoTIFF-specific info if available
        if image_info.get('is_geotiff', False):
            report += f"""
- **GeoTIFF Information:**
  - **Bands:** {', '.join(image_info.get('bands', ['Unknown']))}
  - **Selected Band:** {image_info.get('selected_band', 'N/A')}
  - **CRS:** {image_info.get('crs', 'Unknown')}
  - **Bounds:** {image_info.get('bounds', 'Unknown')}
"""

    # Add filter parameters
    report += """
## Processing Parameters
"""
    
    if filter_params:
        filter_type = filter_params.get('type', 'Unknown')
        report += f"- **Filter Type:** {filter_type}\n"
        
        if filter_type == 'Low-pass' or filter_type == 'High-pass':
            report += f"- **Cutoff Radius:** {filter_params.get('cutoff_radius', 'Unknown')}\n"
        elif filter_type == 'Band-stop':
            report += f"""
- **Inner Radius:** {filter_params.get('inner_radius', 'Unknown')}
- **Outer Radius:** {filter_params.get('outer_radius', 'Unknown')}
"""
        
        report += f"- **Gaussian Tapering:** {'Yes' if filter_params.get('gaussian_tapering', False) else 'No'}\n"

    # Add AI analysis
    report += """
## AI Analysis Results
"""
    
    if analysis_results:
        if 'error' in analysis_results:
            report += f"**Error:** {analysis_results['error']}\n"
        else:
            # Features detected
            report += "### Features Detected\n"
            for feature in analysis_results.get('features_detected', []):
                report += f"- {feature}\n"
            
            # Effects of filtering
            report += "\n### Filter Effects\n"
            for effect in analysis_results.get('filter_effects', []):
                report += f"- {effect}\n"
            
            # Environmental patterns
            report += "\n### Environmental Patterns\n"
            for pattern in analysis_results.get('environmental_patterns', []):
                report += f"- {pattern}\n"
            
            # Applications
            report += "\n### Potential Applications\n"
            for app in analysis_results.get('applications', []):
                report += f"- {app}\n"
            
            # Recommendations
            report += "\n### Recommendations\n"
            for rec in analysis_results.get('recommendations', []):
                report += f"- {rec}\n"
            
            # Summary
            report += "\n### Summary\n"
            report += analysis_results.get('summary', 'No summary available.')

    # Add footer
    report += """

---
*Generated by Remote Sensing Data Analyzer with Frequency-Domain Filtering*
*© 2025 AI-Powered Satellite Image Analysis Tool*
"""

    return report

def get_available_providers():
    """
    Get list of available AI providers based on configured API keys
    """
    return AVAILABLE_PROVIDERS