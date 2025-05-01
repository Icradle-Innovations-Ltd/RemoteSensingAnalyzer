import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
import os
import time
import base64
import json
from datetime import datetime

# Import custom modules
import image_processor
import filters
import utils
from modules import ndvi, classification, map_overlay, ai_analysis, documentation

# Set page configuration
st.set_page_config(
    page_title="Remote Sensing Data Analyzer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a title and description
st.title("🌍 Remote Sensing Data Analyzer")
st.markdown("*Frequency-domain filtering and analysis for satellite imagery*")

# Initialize session state variables if they don't exist
if 'original_image' not in st.session_state:
    st.session_state.original_image = None
if 'preprocessed_image' not in st.session_state:
    st.session_state.preprocessed_image = None
if 'fft_image' not in st.session_state:
    st.session_state.fft_image = None
if 'filtered_image' not in st.session_state:
    st.session_state.filtered_image = None
if 'fft_magnitude' not in st.session_state:
    st.session_state.fft_magnitude = None
if 'fft_shifted' not in st.session_state:
    st.session_state.fft_shifted = None
if 'selected_band' not in st.session_state:
    st.session_state.selected_band = None
if 'is_geotiff' not in st.session_state:
    st.session_state.is_geotiff = False
if 'bands' not in st.session_state:
    st.session_state.bands = None
if 'last_filter_params' not in st.session_state:
    st.session_state.last_filter_params = {}
if 'img_info' not in st.session_state:
    st.session_state.img_info = {}
    
# Sidebar
with st.sidebar:
    st.header("Upload & Controls")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload an image (JPG, PNG, or GeoTIFF)", 
                                    type=["jpg", "jpeg", "png", "tif", "tiff"])
    
    # Only show the rest of the controls if an image is uploaded
    if uploaded_file is not None:
        try:
            # Process the uploaded file
            image_data, is_geotiff, bands = image_processor.process_upload(uploaded_file)
            
            # Update session state
            st.session_state.original_image = image_data
            st.session_state.is_geotiff = is_geotiff
            st.session_state.bands = bands
            
            # Band selection for GeoTIFF
            if is_geotiff and bands and len(bands) > 1:
                band_options = list(range(1, len(bands) + 1))
                selected_band = st.selectbox(
                    "Select band to analyze:", 
                    band_options,
                    index=0
                )
                st.session_state.selected_band = selected_band
                
                # Extract the selected band
                preprocessed_img = image_processor.extract_band(image_data, selected_band - 1)
                st.session_state.preprocessed_image = preprocessed_img
                
                # Show band info if available
                if bands and len(bands) >= selected_band:
                    st.info(f"Band {selected_band}: {bands[selected_band - 1]}")
            else:
                # For non-GeoTIFF or single-band GeoTIFF
                preprocessed_img = image_processor.preprocess_image(image_data)
                st.session_state.preprocessed_image = preprocessed_img
                st.session_state.selected_band = 0
            
            # Compute FFT if we have a preprocessed image
            if st.session_state.preprocessed_image is not None:
                fft_shifted, fft_magnitude = utils.compute_fft(st.session_state.preprocessed_image)
                st.session_state.fft_shifted = fft_shifted
                st.session_state.fft_magnitude = fft_magnitude
            
            # Display image info
            img_height, img_width = st.session_state.preprocessed_image.shape
            st.session_state.img_info = {
                "width": img_width,
                "height": img_height,
                "type": "GeoTIFF" if is_geotiff else uploaded_file.type,
                "size_kb": round(len(uploaded_file.getvalue()) / 1024, 2)
            }
            
            # Show image info
            st.subheader("Image Information")
            st.write(f"Dimensions: {img_width} x {img_height}")
            st.write(f"Type: {st.session_state.img_info['type']}")
            st.write(f"Size: {st.session_state.img_info['size_kb']} KB")
            
            # Filter selection
            st.subheader("Filter Selection")
            filter_type = st.radio(
                "Select filter type:",
                ["Low-pass", "High-pass", "Band-stop"]
            )
            
            # Filter parameters
            st.subheader("Filter Parameters")
            
            # Get the smaller dimension for setting max radius
            min_dim = min(img_height, img_width) // 2
            
            # Different sliders based on filter type
            if filter_type == "Low-pass":
                cutoff_radius = st.slider(
                    "Cutoff radius:", 
                    1, min_dim, min_dim // 4,
                    help="Frequencies below this radius will be preserved"
                )
                gaussian_tapering = st.checkbox("Apply Gaussian tapering", 
                                               value=True,
                                               help="Smooths the filter transition to reduce ringing artifacts")
                filter_params = {
                    "type": filter_type,
                    "cutoff_radius": cutoff_radius,
                    "gaussian_tapering": gaussian_tapering
                }
            
            elif filter_type == "High-pass":
                cutoff_radius = st.slider(
                    "Cutoff radius:", 
                    1, min_dim, min_dim // 4,
                    help="Frequencies above this radius will be preserved"
                )
                gaussian_tapering = st.checkbox("Apply Gaussian tapering", 
                                               value=True,
                                               help="Smooths the filter transition to reduce ringing artifacts")
                filter_params = {
                    "type": filter_type,
                    "cutoff_radius": cutoff_radius,
                    "gaussian_tapering": gaussian_tapering
                }
            
            else:  # Band-stop
                inner_radius = st.slider(
                    "Inner radius:", 
                    1, min_dim - 1, min_dim // 8,
                    help="Inner boundary of the band to be removed"
                )
                outer_radius = st.slider(
                    "Outer radius:", 
                    inner_radius + 1, min_dim, min_dim // 3,
                    help="Outer boundary of the band to be removed"
                )
                gaussian_tapering = st.checkbox("Apply Gaussian tapering", 
                                               value=True,
                                               help="Smooths the filter transition to reduce ringing artifacts")
                filter_params = {
                    "type": filter_type,
                    "inner_radius": inner_radius,
                    "outer_radius": outer_radius,
                    "gaussian_tapering": gaussian_tapering
                }
            
            # Create filter mask
            if st.session_state.fft_shifted is not None:
                filter_mask = filters.create_filter_mask(
                    st.session_state.fft_shifted.shape,
                    filter_params
                )
                
                # Apply filter and perform inverse FFT
                filtered_img = filters.apply_filter(
                    st.session_state.fft_shifted,
                    filter_mask
                )
                
                # Store the filtered image and filter parameters
                st.session_state.filtered_image = filtered_img
                st.session_state.last_filter_params = filter_params
            
            # Advanced Options Expander
            with st.expander("Advanced Options"):
                if st.session_state.is_geotiff and len(st.session_state.bands) >= 4:
                    if st.button("Compute NDVI"):
                        red_band = image_processor.extract_band(st.session_state.original_image, 2)  # Typically band 3
                        nir_band = image_processor.extract_band(st.session_state.original_image, 3)  # Typically band 4
                        st.session_state.filtered_image = ndvi.compute_ndvi(red_band, nir_band)
                        st.info("NDVI computation complete!")
                
                if st.button("Apply Texture Classification"):
                    if st.session_state.preprocessed_image is not None:
                        st.session_state.filtered_image = classification.texture_classification(
                            st.session_state.preprocessed_image
                        )
                        st.info("Texture classification complete!")
                
                # Geo-referenced overlay is only applicable for GeoTIFF
                if st.session_state.is_geotiff:
                    st.write("Map overlay functionality available for GeoTIFF")
        
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")

# Main content area
if st.session_state.preprocessed_image is not None:
    # Create tabs for visualization and analysis
    main_tabs = st.tabs(["Visualization", "AI Analysis", "Report Generation"])
    
    # Visualization Tab
    with main_tabs[0]:
        # Create three columns for side-by-side comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Original Image")
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.imshow(st.session_state.preprocessed_image, cmap='gray')
            ax.axis('off')
            st.pyplot(fig)
            
            if st.session_state.is_geotiff and st.session_state.selected_band is not None and st.session_state.selected_band > 0:
                st.caption(f"Band {st.session_state.selected_band}")
        
        with col2:
            st.subheader("FFT Spectrum")
            if st.session_state.fft_magnitude is not None:
                fig, ax = plt.subplots(figsize=(5, 5))
                im = ax.imshow(st.session_state.fft_magnitude, cmap='viridis')
                ax.axis('off')
                fig.colorbar(im, ax=ax, shrink=0.8)
                st.pyplot(fig)
                
                # Add explanation
                st.caption("Brighter areas indicate stronger frequency components")
        
        with col3:
            st.subheader("Filtered Result")
            if st.session_state.filtered_image is not None:
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.imshow(st.session_state.filtered_image, cmap='gray')
                ax.axis('off')
                st.pyplot(fig)
                
                # Add filter info
                if 'type' in st.session_state.last_filter_params:
                    filter_info = f"Filter: {st.session_state.last_filter_params['type']}"
                    st.caption(filter_info)
                
                # Download button
                if st.button("Download Filtered Image", key="download_img_btn"):
                    # Convert filtered image to bytes
                    filtered_pil = Image.fromarray(
                        (st.session_state.filtered_image * 255).astype(np.uint8)
                    )
                    buf = io.BytesIO()
                    filtered_pil.save(buf, format='PNG')
                    btn = st.download_button(
                        label="Download PNG",
                        data=buf.getvalue(),
                        file_name="filtered_image.png",
                        mime="image/png"
                    )
    
    # AI Analysis Tab
    with main_tabs[1]:
        st.subheader("AI-Powered Image Analysis")
        st.markdown("""
        Our AI analysis uses advanced computer vision models to interpret both your original and filtered images.
        This can help identify features, patterns, and potential applications of your processed imagery.
        """)
        
        # Initialize session state for AI analysis
        if 'ai_analysis_results' not in st.session_state:
            st.session_state.ai_analysis_results = None
            
        # AI Analysis button
        if st.button("Analyze with AI", key="analyze_ai_btn"):
            with st.spinner("Analyzing imagery with AI..."):
                if st.session_state.preprocessed_image is not None and st.session_state.filtered_image is not None:
                    # Get filter type
                    filter_type = st.session_state.last_filter_params.get('type', 'Unknown')
                    
                    # Run AI analysis
                    analysis_results = ai_analysis.analyze_satellite_image(
                        st.session_state.preprocessed_image,
                        st.session_state.filtered_image,
                        filter_type
                    )
                    
                    # Store results
                    st.session_state.ai_analysis_results = analysis_results
                    
                    st.success("Analysis complete!")
        
        # Display AI analysis results if available
        if st.session_state.ai_analysis_results:
            results = st.session_state.ai_analysis_results
            
            if 'error' in results:
                st.error(f"Analysis error: {results['error']}")
            else:
                # Features detected
                st.subheader("Features Detected")
                for feature in results.get('features_detected', []):
                    st.markdown(f"- {feature}")
                
                # Effects of filtering
                st.subheader("Filter Effects")
                for effect in results.get('filter_effects', []):
                    st.markdown(f"- {effect}")
                
                # Environmental patterns
                st.subheader("Environmental Patterns")
                for pattern in results.get('environmental_patterns', []):
                    st.markdown(f"- {pattern}")
                
                # Applications
                st.subheader("Potential Applications")
                for app in results.get('applications', []):
                    st.markdown(f"- {app}")
                
                # Recommendations
                st.subheader("Recommendations")
                for rec in results.get('recommendations', []):
                    st.markdown(f"- {rec}")
                
                # Summary
                st.subheader("Summary")
                st.write(results.get('summary', 'No summary available.'))
        else:
            st.info("Click 'Analyze with AI' to get insights about your imagery.")
    
    # Report Generation Tab
    with main_tabs[2]:
        st.subheader("Report Generation")
        st.markdown("""
        Generate a comprehensive report that combines image information, processing parameters,
        and AI analysis results. This report can be used for documentation, sharing insights,
        or supporting decision-making processes.
        """)
        
        # Initialize session state for report
        if 'report_content' not in st.session_state:
            st.session_state.report_content = None
            
        # Generate report button
        if st.button("Generate Report", key="gen_report_btn"):
            if st.session_state.img_info and st.session_state.last_filter_params:
                # Generate report
                report = ai_analysis.generate_full_report(
                    st.session_state.img_info,
                    st.session_state.last_filter_params,
                    st.session_state.ai_analysis_results
                )
                
                # Store report
                st.session_state.report_content = report
                
                st.success("Report generated successfully!")
        
        # Display and download report if available
        if st.session_state.report_content:
            st.markdown(st.session_state.report_content)
            
            # Download report button
            if st.button("Download Report", key="download_report_btn"):
                # Prepare report for download
                report_bytes = st.session_state.report_content.encode()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"satellite_analysis_report_{timestamp}.md"
                
                st.download_button(
                    label="Download Markdown Report",
                    data=report_bytes,
                    file_name=filename,
                    mime="text/markdown"
                )
        else:
            st.info("Click 'Generate Report' to create a comprehensive analysis report.")
else:
    # Display documentation and app information when no image is uploaded
    st.info("👈 Please upload an image using the sidebar to begin analysis.")
    
    # Create tabs for different documentation sections
    doc_tabs = st.tabs(["About", "Tutorial", "Frequency Domain Guide", "Examples", "Interpretation Guide"])
    
    with doc_tabs[0]:
        st.markdown(documentation.get_documentation_section("about"))
    
    with doc_tabs[1]:
        st.markdown(documentation.get_documentation_section("tutorial"))
    
    with doc_tabs[2]:
        st.markdown(documentation.get_documentation_section("frequency_domain"))
    
    with doc_tabs[3]:
        st.markdown(documentation.get_documentation_section("examples"))
        
    with doc_tabs[4]:
        st.markdown(documentation.get_documentation_section("interpretation"))

# Footer
st.markdown("---")
st.markdown("Remote Sensing Data Analyzer with Frequency-Domain Filtering | A tool for environmental scientists and GIS analysts")
