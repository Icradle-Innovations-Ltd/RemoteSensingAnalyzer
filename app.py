import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
import os
import time
import base64
import json
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import custom modules
import image_processor
import filters
import utils
from modules import ndvi, classification, map_overlay, documentation
# Import AI providers module (replaces ai_analysis)
from modules import ai_providers
# Import satellite image fetcher module
from modules import satellite_fetcher
# Import land cover analysis module
from modules import land_cover
# Import time series and change detection modules
from modules import time_series, change_detection
# Import topography and railways detection modules
from modules import topography, railways
from modules import satellite_orbit
# Import local analysis module (for AI-independent analysis)
from modules import local_analysis

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
    upload_tab, url_tab = st.tabs(["Upload File", "Fetch from URL"])
    
    with upload_tab:
        uploaded_file = st.file_uploader("Upload an image (JPG, PNG, or GeoTIFF)", 
                                        type=["jpg", "jpeg", "png", "tif", "tiff"])
    
    with url_tab:
        image_url = st.text_input("Enter image URL:", 
                                  placeholder="https://example.com/satellite_image.jpg")
        
        fetch_button = st.button("Fetch Image")
        
        if fetch_button and image_url:
            with st.spinner("Fetching image from URL..."):
                # Fetch image from URL
                try:
                    image_array, error = local_analysis.fetch_image_from_url(image_url)
                    
                    if error:
                        st.error(f"Error fetching image: {error}")
                    elif image_array is not None:
                        # Create a virtual file for compatibility with the rest of the code
                        from io import BytesIO
                        from PIL import Image
                        
                        # Convert to PIL Image and then to bytes
                        if len(image_array.shape) == 3 and image_array.shape[2] == 4:
                            # If RGBA, convert to RGB
                            image_pil = Image.fromarray(image_array).convert('RGB')
                        else:
                            image_pil = Image.fromarray(image_array)
                        
                        buf = BytesIO()
                        image_pil.save(buf, format="JPEG")
                        buf.seek(0)
                        
                        # Create a mock uploaded_file with necessary attributes
                        class MockUploadedFile:
                            def __init__(self, buf, filename):
                                self.buf = buf
                                self.name = filename
                                self.type = "image/jpeg"
                            
                            def getvalue(self):
                                return self.buf.getvalue()
                        
                        # Create the mock file
                        uploaded_file = MockUploadedFile(buf, "fetched_image.jpg")
                        
                        st.success("Image fetched successfully!")
                except Exception as e:
                    st.error(f"Error processing fetched image: {str(e)}")
    
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
            with st.expander("Advanced Analysis Options"):
                st.subheader("Vegetation Analysis")
                if st.session_state.is_geotiff and len(st.session_state.bands) >= 4:
                    if st.button("Compute NDVI"):
                        red_band = image_processor.extract_band(st.session_state.original_image, 2)  # Typically band 3
                        nir_band = image_processor.extract_band(st.session_state.original_image, 3)  # Typically band 4
                        st.session_state.filtered_image = ndvi.compute_ndvi(red_band, nir_band)
                        st.info("NDVI computation complete!")
                        
                st.subheader("Land Cover Analysis")
                
                # Land cover classification options
                num_classes = st.slider("Number of Land Cover Classes", 2, 10, 5, 
                                       help="Number of distinct land cover types to identify")
                
                if st.button("Classify Land Cover"):
                    if st.session_state.preprocessed_image is not None:
                        with st.spinner("Classifying land cover..."):
                            # Perform land cover classification
                            classified, class_colors = land_cover.classify_land_cover(
                                st.session_state.preprocessed_image, 
                                num_classes=num_classes
                            )
                            
                            # Visualize the classification
                            colored_classification = land_cover.visualize_land_cover(
                                classified, 
                                class_colors, 
                                title="Land Cover Classification"
                            )
                            
                            # Compute statistics
                            stats = land_cover.compute_land_cover_statistics(
                                classified, 
                                num_classes
                            )
                            
                            # Store results in session state
                            st.session_state.filtered_image = colored_classification
                            st.session_state.land_cover_stats = stats
                            st.session_state.land_cover_classes = num_classes
                            
                            st.success("Land cover classification complete!")
                
                st.subheader("Feature Detection")
                
                feature_options = st.selectbox(
                    "Select feature to detect:",
                    ["Texture Analysis", "Water Bodies", "Urban Areas", "Frequency Patterns", 
                     "Hills & Mountains", "Railways & Roads", "Local Image Analysis"]
                )
                
                if st.button("Detect Features"):
                    if st.session_state.preprocessed_image is not None:
                        with st.spinner(f"Detecting {feature_options}..."):
                            if feature_options == "Texture Analysis":
                                # Apply texture classification
                                st.session_state.filtered_image = classification.texture_classification(
                                    st.session_state.preprocessed_image
                                )
                                st.info("Texture analysis complete!")
                                
                            elif feature_options == "Water Bodies":
                                # Detect water bodies
                                water_threshold = 0.3  # Default threshold
                                water_mask = land_cover.detect_water_bodies(
                                    st.session_state.preprocessed_image, 
                                    threshold=water_threshold
                                )
                                
                                # Create visualization
                                water_viz = np.zeros((*water_mask.shape, 3), dtype=np.float32)
                                water_viz[water_mask, 0] = 0.0  # R
                                water_viz[water_mask, 1] = 0.0  # G
                                water_viz[water_mask, 2] = 1.0  # B (blue for water)
                                
                                # Overlay on original image
                                background = np.repeat(
                                    st.session_state.preprocessed_image[:, :, np.newaxis], 
                                    3, 
                                    axis=2
                                ) if len(st.session_state.preprocessed_image.shape) == 2 else st.session_state.preprocessed_image
                                
                                # Combine with 70% opacity for water
                                water_overlay = 0.7 * water_viz + 0.3 * background
                                
                                st.session_state.filtered_image = water_overlay
                                st.info("Water bodies detection complete!")
                                
                            elif feature_options == "Urban Areas":
                                # Detect urban areas
                                urban_mask = land_cover.detect_urban_areas(
                                    st.session_state.preprocessed_image
                                )
                                
                                # Create visualization
                                urban_viz = np.zeros((*urban_mask.shape, 3), dtype=np.float32)
                                urban_viz[urban_mask, 0] = 1.0  # R (red for urban)
                                urban_viz[urban_mask, 1] = 0.3  # G
                                urban_viz[urban_mask, 2] = 0.3  # B
                                
                                # Overlay on original image
                                background = np.repeat(
                                    st.session_state.preprocessed_image[:, :, np.newaxis], 
                                    3, 
                                    axis=2
                                ) if len(st.session_state.preprocessed_image.shape) == 2 else st.session_state.preprocessed_image
                                
                                # Combine with 70% opacity for urban
                                urban_overlay = 0.7 * urban_viz + 0.3 * background
                                
                                st.session_state.filtered_image = urban_overlay
                                st.info("Urban areas detection complete!")
                                
                            elif feature_options == "Frequency Patterns":
                                if st.session_state.fft_magnitude is not None:
                                    # Analyze frequency patterns
                                    pattern_info = land_cover.analyze_frequency_patterns(
                                        st.session_state.fft_magnitude
                                    )
                                    
                                    # Store pattern information
                                    st.session_state.pattern_info = pattern_info
                                    
                                    # Create visualization of detected patterns
                                    freq_viz = np.copy(st.session_state.fft_magnitude)
                                    
                                    # Use the filtered image to show the result
                                    st.session_state.filtered_image = st.session_state.preprocessed_image
                                    
                                    st.info(f"Detected {pattern_info['num_patterns']} frequency patterns!")
                                    
                                    # Show pattern details
                                    if pattern_info['num_patterns'] > 0:
                                        st.write("#### Detected Patterns")
                                        for i, prop in enumerate(pattern_info['peak_properties']):
                                            st.write(f"Pattern {i+1}:")
                                            st.write(f"- Spatial wavelength: {prop['wavelength']:.2f} pixels")
                                            st.write(f"- Direction: {prop['angle']:.1f}°")
                                            st.write(f"- Intensity: {prop['intensity']:.3f}")
                                else:
                                    st.error("FFT spectrum not available. Please recompute.")
                                    
                            elif feature_options == "Hills & Mountains":
                                # Detect hills and mountains
                                hills_mask, height_estimate = topography.detect_hills_mountains(
                                    st.session_state.preprocessed_image,
                                    min_height=0.2,
                                    slope_threshold=0.15
                                )
                                
                                # Detect ridges and valleys for visualization
                                ridges, valleys = topography.detect_ridges_valleys(
                                    st.session_state.preprocessed_image
                                )
                                
                                # Create visualization
                                terrain_viz = topography.create_terrain_visualization(
                                    st.session_state.preprocessed_image,
                                    hills_mask,
                                    ridges,
                                    valleys
                                )
                                
                                # Store results
                                st.session_state.filtered_image = terrain_viz
                                
                                # Analyze terrain features
                                terrain_analysis = topography.analyze_terrain_features(
                                    st.session_state.preprocessed_image
                                )
                                
                                # Display terrain analysis
                                st.info("Terrain detection complete!")
                                st.write("#### Terrain Analysis")
                                st.write(f"- Hill coverage: {terrain_analysis['hill_percentage']:.2f}% of the image")
                                st.write(f"- Ridge length: {terrain_analysis['ridge_length_pixels']} pixels")
                                st.write(f"- Valley length: {terrain_analysis['valley_length_pixels']} pixels")
                                
                                # Store full analysis for reporting
                                st.session_state.terrain_analysis = terrain_analysis
                                
                            elif feature_options == "Railways & Roads":
                                # Detect railways and roads
                                railways_mask, railway_properties = railways.detect_railways(
                                    st.session_state.preprocessed_image,
                                    direction_tolerance=30,
                                    min_length=15,
                                    threshold=0.6
                                )
                                
                                # Create visualization
                                railway_viz = railways.create_railway_visualization(
                                    st.session_state.preprocessed_image,
                                    railways_mask
                                )
                                
                                # Store results
                                st.session_state.filtered_image = railway_viz
                                
                                # Analyze railway network
                                railway_analysis = railways.analyze_railway_network(
                                    railways_mask,
                                    railway_properties
                                )
                                
                                # Display railway analysis
                                st.info("Railway detection complete!")
                                st.write("#### Railway Network Analysis")
                                st.write(f"- Total length: {railway_analysis['network_length_pixels']:.1f} pixels")
                                st.write(f"- Number of segments: {railway_analysis['segment_count']}")
                                
                                if 'main_direction_degrees' in railway_analysis:
                                    st.write(f"- Main direction: {railway_analysis['main_direction_degrees']:.1f}°")
                                
                                if 'intersection_count' in railway_analysis:
                                    st.write(f"- Intersections: {railway_analysis['intersection_count']}")
                                
                                # Store full analysis for reporting
                                st.session_state.railway_analysis = railway_analysis
                                
                            elif feature_options == "Local Image Analysis":
                                # Run local analysis that doesn't depend on external APIs
                                local_results = local_analysis.analyze_image_content(
                                    st.session_state.preprocessed_image
                                )
                                
                                # Generate report from local analysis
                                local_report = local_analysis.generate_analysis_report(local_results)
                                
                                # Keep original image for display
                                st.session_state.filtered_image = st.session_state.preprocessed_image
                                
                                # Store analysis results
                                st.session_state.local_analysis_results = local_results
                                st.session_state.local_report = local_report
                                
                                # Display summary of analysis
                                st.info("Local image analysis complete!")
                                
                                # Show primary classification
                                if 'content_classification' in local_results:
                                    primary = local_results['content_classification'].get('primary_category', 'Unknown')
                                    subcategory = local_results['content_classification'].get('subcategory', '')
                                    
                                    st.write(f"#### Primary Classification: {primary}")
                                    if subcategory:
                                        st.write(f"Subcategory: {subcategory}")
                                    
                                    # Show natural vs built percentages
                                    if 'natural_vs_built' in local_results['content_classification']:
                                        nat = local_results['content_classification']['natural_vs_built']['natural_likelihood']
                                        built = local_results['content_classification']['natural_vs_built']['built_likelihood']
                                        
                                        st.write(f"Natural features: {nat:.1f}%")
                                        st.write(f"Built/human-made features: {built:.1f}%")
                                
                                # Show textural properties
                                if 'texture' in local_results:
                                    texture_type = local_results['texture'].get('type', 'Unknown')
                                    st.write(f"Texture type: {texture_type}")
                                    
                                # Show detailed analysis in expander
                                with st.expander("View Full Analysis Report"):
                                    st.markdown(local_report)
                
                # Geo-referenced overlay is only applicable for GeoTIFF
                if st.session_state.is_geotiff:
                    st.subheader("Geospatial Visualization")
                    if st.button("Show Map Overlay"):
                        st.write("Creating map overlay...")
                        # Map overlay functionality will be implemented here
        
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")

# Main content area
if st.session_state.preprocessed_image is not None:
    # Create tabs for visualization and analysis
    main_tabs = st.tabs(["Visualization", "Spectral Analysis", "Land Cover", "Change Detection", "AI Analysis", "Satellite Orbits", "Report Generation", "Settings"])
    
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
    
    # Spectral Analysis Tab
    with main_tabs[1]:
        st.subheader("Spectral Analysis")
        st.markdown("""
        Analyze the frequency domain characteristics of your satellite imagery to identify spatial patterns,
        periodic structures, and textural features that may not be visible in the spatial domain.
        """)
        
        # Frequency spectrum visualization
        if st.session_state.fft_magnitude is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("2D Frequency Spectrum")
                fig, ax = plt.subplots(figsize=(8, 8))
                im = ax.imshow(np.log1p(st.session_state.fft_magnitude), cmap='inferno')
                ax.set_title("Log-scaled Magnitude Spectrum")
                ax.axis('off')
                fig.colorbar(im, ax=ax, shrink=0.8)
                st.pyplot(fig)
                
                st.markdown("""
                ### Interpreting the Frequency Spectrum:
                - **Center point**: Represents the DC component (average brightness)
                - **Bright spots**: Indicate strong periodic patterns in the image
                - **Distance from center**: Inversely proportional to the spatial wavelength
                - **Direction from center**: Perpendicular to the orientation of features
                """)
            
            with col2:
                st.subheader("Radial Profile")
                
                # Calculate radial profile (average magnitude vs. distance from center)
                y, x = np.indices(st.session_state.fft_magnitude.shape)
                center = (st.session_state.fft_magnitude.shape[0] // 2, st.session_state.fft_magnitude.shape[1] // 2)
                r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
                r = r.astype(int)
                
                # Calculate the mean
                radial_prof = np.bincount(r.ravel(), st.session_state.fft_magnitude.ravel())
                nr = np.bincount(r.ravel())
                radial_prof = radial_prof / nr
                
                # Plot the radial profile
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.plot(radial_prof)
                ax.set_xlabel('Distance from Center (pixels)')
                ax.set_ylabel('Average Magnitude')
                ax.set_title('Radial Profile of FFT Magnitude')
                ax.grid(True)
                st.pyplot(fig)
                
                st.markdown("""
                ### Radial Profile Interpretation:
                - **Peaks**: Indicate dominant spatial frequencies in the image
                - **Slope**: Overall texture characteristics (steep slope = smooth image)
                - **High values at low distances**: Indicate large-scale patterns
                - **High values at large distances**: Indicate fine details or noise
                """)
        
            # Frequency pattern analysis
            st.subheader("Frequency Pattern Analysis")
            
            if st.button("Analyze Frequency Patterns", key="analyze_freq_btn"):
                with st.spinner("Analyzing frequency patterns..."):
                    # Analyze patterns in the frequency domain
                    pattern_info = land_cover.analyze_frequency_patterns(st.session_state.fft_magnitude)
                    
                    # Store pattern information
                    st.session_state.pattern_info = pattern_info
                    
                    # Display results
                    st.write(f"Detected {pattern_info['num_patterns']} significant frequency patterns")
                    
                    if pattern_info['num_patterns'] > 0:
                        # Create a table of pattern properties
                        pattern_data = []
                        for i, prop in enumerate(pattern_info['peak_properties']):
                            pattern_data.append({
                                "Pattern": i+1,
                                "Wavelength (pixels)": f"{prop['wavelength']:.2f}",
                                "Orientation (°)": f"{prop['angle']:.1f}",
                                "Relative Strength": f"{prop['intensity']:.3f}"
                            })
                        
                        st.table(pattern_data)
                        
                        # Create a visualization of the detected patterns
                        fig, ax = plt.subplots(figsize=(8, 8))
                        ax.imshow(np.log1p(st.session_state.fft_magnitude), cmap='gray')
                        
                        # Mark detected patterns
                        center_y, center_x = st.session_state.fft_magnitude.shape[0] // 2, st.session_state.fft_magnitude.shape[1] // 2
                        for i, prop in enumerate(pattern_info['peak_properties']):
                            # Convert polar coordinates to Cartesian
                            y = center_y + prop['distance'] * np.sin(prop['angle'] * np.pi / 180)
                            x = center_x + prop['distance'] * np.cos(prop['angle'] * np.pi / 180)
                            
                            # Mark the pattern
                            ax.plot(x, y, 'ro', markersize=10, alpha=0.7)
                            ax.text(x+5, y+5, f"{i+1}", color='red', fontsize=12)
                            
                            # Also mark the symmetric point
                            ax.plot(2*center_x - x, 2*center_y - y, 'ro', markersize=10, alpha=0.7)
                            ax.text(2*center_x - x+5, 2*center_y - y+5, f"{i+1}'", color='red', fontsize=12)
                        
                        ax.set_title("Detected Frequency Patterns")
                        ax.axis('off')
                        st.pyplot(fig)
                        
                        # Interpretation of results
                        st.subheader("Interpretation")
                        
                        # Find dominant pattern
                        dominant_idx = np.argmax([p['intensity'] for p in pattern_info['peak_properties']])
                        dominant = pattern_info['peak_properties'][dominant_idx]
                        
                        st.markdown(f"""
                        ### Key Findings:
                        
                        - **Dominant pattern**: Pattern {dominant_idx+1} with a wavelength of {dominant['wavelength']:.2f} pixels
                        - **Orientation**: Main features are oriented at {(dominant['angle']+90)%180:.1f}° from horizontal
                        - **Spatial frequency**: The image has a characteristic spatial frequency of {1/dominant['wavelength']:.5f} cycles/pixel
                        
                        ### Potential Applications:
                        
                        - **Land cover classification**: The frequency signature can help distinguish between different terrain types
                        - **Feature extraction**: The dominant patterns can be used to extract specific landscape elements
                        - **Change detection**: Comparing frequency signatures over time can reveal landscape changes
                        """)
                    else:
                        st.info("No significant frequency patterns detected. The image may have uniform texture or random patterns.")
            
            # Filtering options
            st.subheader("Custom Frequency Filtering")
            
            filter_type = st.radio(
                "Select filter type:",
                ["Low-pass", "High-pass", "Band-pass", "Band-stop", "Directional"],
                key="spectral_filter_type"
            )
            
            # Get the smaller dimension for setting max radius
            height, width = st.session_state.preprocessed_image.shape
            min_dim = min(height, width) // 2
            
            if filter_type == "Low-pass":
                cutoff_radius = st.slider(
                    "Cutoff radius:", 
                    1, min_dim, min_dim // 4,
                    help="Frequencies below this radius will be preserved",
                    key="spectral_lowpass"
                )
                filter_params = {
                    "type": filter_type,
                    "cutoff_radius": cutoff_radius,
                    "gaussian_tapering": True
                }
                
            elif filter_type == "High-pass":
                cutoff_radius = st.slider(
                    "Cutoff radius:", 
                    1, min_dim, min_dim // 4,
                    help="Frequencies above this radius will be preserved",
                    key="spectral_highpass"
                )
                filter_params = {
                    "type": filter_type,
                    "cutoff_radius": cutoff_radius,
                    "gaussian_tapering": True
                }
                
            elif filter_type == "Band-pass":
                col1, col2 = st.columns(2)
                with col1:
                    inner_radius = st.slider(
                        "Inner radius:", 
                        1, min_dim - 1, min_dim // 8,
                        help="Inner boundary of the band to be preserved",
                        key="spectral_bandpass_inner"
                    )
                with col2:
                    outer_radius = st.slider(
                        "Outer radius:", 
                        inner_radius + 1, min_dim, min_dim // 3,
                        help="Outer boundary of the band to be preserved",
                        key="spectral_bandpass_outer"
                    )
                filter_params = {
                    "type": "Band-pass",
                    "inner_radius": inner_radius,
                    "outer_radius": outer_radius,
                    "gaussian_tapering": True
                }
                
            elif filter_type == "Band-stop":
                col1, col2 = st.columns(2)
                with col1:
                    inner_radius = st.slider(
                        "Inner radius:", 
                        1, min_dim - 1, min_dim // 8,
                        help="Inner boundary of the band to be removed",
                        key="spectral_bandstop_inner"
                    )
                with col2:
                    outer_radius = st.slider(
                        "Outer radius:", 
                        inner_radius + 1, min_dim, min_dim // 3,
                        help="Outer boundary of the band to be removed",
                        key="spectral_bandstop_outer"
                    )
                filter_params = {
                    "type": "Band-stop",
                    "inner_radius": inner_radius,
                    "outer_radius": outer_radius,
                    "gaussian_tapering": True
                }
                
            else:  # Directional filter
                col1, col2 = st.columns(2)
                with col1:
                    angle = st.slider(
                        "Direction angle (degrees):", 
                        0, 180, 45,
                        help="Direction of features to preserve (0° = horizontal, 90° = vertical)",
                        key="spectral_direction"
                    )
                with col2:
                    width = st.slider(
                        "Angular width (degrees):", 
                        5, 90, 30,
                        help="Width of the directional filter",
                        key="spectral_width"
                    )
                filter_params = {
                    "type": "Directional",
                    "angle": angle,
                    "width": width,
                    "gaussian_tapering": True
                }
            
            # Apply filter button
            if st.button("Apply Spectral Filter"):
                with st.spinner("Applying filter..."):
                    # Special case for directional filter
                    if filter_type == "Directional":
                        # Create a custom directional filter mask
                        y, x = np.indices(st.session_state.fft_shifted.shape)
                        center_y, center_x = y.shape[0] // 2, x.shape[1] // 2
                        y = y - center_y
                        x = x - center_x
                        
                        # Convert to polar coordinates
                        r = np.sqrt(x**2 + y**2)
                        theta = np.arctan2(y, x) * 180 / np.pi
                        
                        # Normalize angle to 0-180 range
                        theta = np.mod(theta, 180)
                        
                        # Create the filter mask
                        half_width = filter_params['width'] / 2
                        angle = filter_params['angle']
                        angle_diff = np.minimum(np.abs(theta - angle), np.abs(theta - (angle + 180)))
                        
                        # Apply Gaussian tapering around the specified direction
                        if filter_params['gaussian_tapering']:
                            sigma = half_width / 3
                            filter_mask = np.exp(-(angle_diff**2) / (2 * sigma**2))
                        else:
                            filter_mask = (angle_diff <= half_width).astype(float)
                        
                        # Apply the mask to the FFT
                        filtered_fft = st.session_state.fft_shifted * filter_mask
                        
                        # Inverse FFT
                        filtered_img = np.real(np.fft.ifft2(np.fft.ifftshift(filtered_fft)))
                        
                        # Normalize to 0-1 range
                        filtered_img = (filtered_img - filtered_img.min()) / (filtered_img.max() - filtered_img.min())
                    else:
                        # For standard filters (low-pass, high-pass, band-pass, band-stop)
                        # Create filter mask
                        if filter_type == "Band-pass":
                            # Convert band-pass to "not band-stop"
                            band_stop_mask = filters.create_filter_mask(
                                st.session_state.fft_shifted.shape,
                                {
                                    "type": "Band-stop",
                                    "inner_radius": filter_params["inner_radius"],
                                    "outer_radius": filter_params["outer_radius"],
                                    "gaussian_tapering": filter_params["gaussian_tapering"]
                                }
                            )
                            filter_mask = 1 - band_stop_mask
                        else:
                            filter_mask = filters.create_filter_mask(
                                st.session_state.fft_shifted.shape,
                                filter_params
                            )
                        
                        # Apply filter
                        filtered_img = filters.apply_filter(
                            st.session_state.fft_shifted,
                            filter_mask
                        )
                    
                    # Store the filtered image and filter parameters
                    st.session_state.filtered_image = filtered_img
                    st.session_state.last_filter_params = filter_params
                    
                    st.success(f"{filter_type} filter applied successfully!")
                    
                    # Show the filtered image
                    fig, ax = plt.subplots(figsize=(8, 8))
                    ax.imshow(filtered_img, cmap='gray')
                    ax.set_title(f"Filtered Image ({filter_type})")
                    ax.axis('off')
                    st.pyplot(fig)
        else:
            st.info("Please load an image first to enable spectral analysis.")
    
    # Change Detection Tab
    with main_tabs[2]:
        st.subheader("Change Detection")
        st.markdown("""
        Detect and analyze changes between satellite images. Upload two images to compare 
        or use the frequency-filtered results to highlight specific changes.
        """)
        
        # Initialize session state for second image
        if 'second_image' not in st.session_state:
            st.session_state.second_image = None
        if 'change_results' not in st.session_state:
            st.session_state.change_results = None
        
        # File uploader for second image
        st.subheader("Upload Comparison Image")
        second_uploaded_file = st.file_uploader("Upload second image for comparison", 
                                      type=["jpg", "jpeg", "png", "tif", "tiff"],
                                      key="second_image_uploader")
        
        if second_uploaded_file is not None:
            try:
                # Process the uploaded file
                image_data2, is_geotiff2, bands2 = image_processor.process_upload(second_uploaded_file)
                
                # Store in session state
                st.session_state.second_image = image_data2
                
                # Process for comparison (ensure grayscale)
                if len(image_data2.shape) > 2:
                    image2_gray = np.mean(image_data2, axis=2)
                else:
                    image2_gray = image_data2
                
                st.session_state.second_image_processed = image2_gray
                
                # Display the second image
                st.subheader("Comparison Image")
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.imshow(image2_gray, cmap='gray')
                ax.axis('off')
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Error processing second image: {str(e)}")
        
        # Change detection options
        st.subheader("Change Detection Settings")
        
        # Method selector
        method = st.selectbox(
            "Change detection method:",
            ["Difference", "Ratio", "Regression"],
            index=0,
            help="Different methods for detecting changes between images"
        )
        
        # Method mapping
        method_map = {
            "Difference": "diff",
            "Ratio": "ratio",
            "Regression": "regression"
        }
        
        # Threshold
        threshold = st.slider(
            "Change threshold:", 
            0.05, 0.5, 0.1, 0.01,
            help="Higher values detect only more significant changes"
        )
        
        # Minimum change area size
        min_size = st.slider(
            "Minimum change area (pixels):", 
            5, 100, 20,
            help="Minimum size of an area to be considered a significant change"
        )
        
        # Detect changes button
        if st.button("Detect Changes"):
            # Check if we have both images
            if st.session_state.preprocessed_image is not None and st.session_state.second_image_processed is not None:
                with st.spinner("Detecting changes..."):
                    # Ensure images have the same size
                    if st.session_state.preprocessed_image.shape != st.session_state.second_image_processed.shape:
                        st.error("Images must have the same dimensions for change detection.")
                    else:
                        # Run change detection
                        change_map, change_magnitude = change_detection.detect_image_changes(
                            st.session_state.preprocessed_image,
                            st.session_state.second_image_processed,
                            method=method_map[method],
                            threshold=threshold
                        )
                        
                        # Cluster changes
                        labeled_changes, num_changes, change_stats = change_detection.cluster_changes(
                            change_map,
                            change_magnitude,
                            min_size=min_size
                        )
                        
                        # Analyze changes
                        change_analysis = change_detection.analyze_changes(
                            st.session_state.preprocessed_image,
                            st.session_state.second_image_processed,
                            change_stats
                        )
                        
                        # Create RGB visualization
                        change_rgb = change_detection.create_change_rgb(
                            st.session_state.preprocessed_image,
                            st.session_state.second_image_processed,
                            change_map
                        )
                        
                        # Store results
                        st.session_state.change_results = {
                            'change_map': change_map,
                            'change_magnitude': change_magnitude,
                            'labeled_changes': labeled_changes,
                            'num_changes': num_changes,
                            'change_stats': change_stats,
                            'change_analysis': change_analysis,
                            'change_rgb': change_rgb
                        }
                        
                        # Show the results
                        st.session_state.filtered_image = change_rgb
                        
                        st.success(f"Detected {num_changes} significant changes!")
            else:
                st.error("Please ensure both images are uploaded before detecting changes.")
        
        # Display change results if available
        if st.session_state.change_results:
            results = st.session_state.change_results
            
            # Display change map
            st.subheader("Change Visualization")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.imshow(results['change_rgb'])
                ax.set_title("Changes Highlighted in Red")
                ax.axis('off')
                st.pyplot(fig)
            
            with col2:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.imshow(results['change_magnitude'], cmap='hot')
                ax.set_title("Change Magnitude")
                ax.axis('off')
                fig.colorbar(ax.imshow(results['change_magnitude'], cmap='hot'), ax=ax, shrink=0.8)
                st.pyplot(fig)
            
            # Show change analysis
            st.subheader("Change Analysis")
            
            if results['num_changes'] > 0:
                # Create a table of change properties
                change_data = []
                for i, analysis in enumerate(results['change_analysis']):
                    change_data.append({
                        "ID": i+1,
                        "Type": analysis['change_type'],
                        "Size (pixels)": analysis['area'],
                        "Confidence": f"{analysis['confidence']*100:.1f}%",
                        "Intensity Change": f"{analysis['intensity_change']:.3f}"
                    })
                
                st.table(change_data)
                
                # Generate a report
                report = change_detection.generate_change_report(
                    st.session_state.preprocessed_image,
                    st.session_state.second_image_processed,
                    results['change_analysis']
                )
                
                # Store report
                st.session_state.change_report = report
                
                # Show report
                with st.expander("View Complete Change Report"):
                    st.markdown(report)
            else:
                st.info("No significant changes detected with current settings. Try adjusting the threshold or method.")
        
        # Alternative usage: Time series simulator
        st.subheader("Time Series Simulation")
        st.markdown("""
        If you don't have multiple images of the same area, you can simulate a time series
        using the filtered image as a changed version.
        """)
        
        if st.button("Simulate Time Series"):
            if st.session_state.preprocessed_image is not None and st.session_state.filtered_image is not None:
                with st.spinner("Simulating time series..."):
                    # Create a simple time series with original and filtered image
                    # This is a simulation - in a real application, you would use actual time series data
                    time_series_data = [st.session_state.preprocessed_image, st.session_state.filtered_image]
                    
                    # Create some sample dates (just for demonstration)
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    one_year_ago = today - timedelta(days=365)
                    dates = [one_year_ago, today]
                    
                    # Analyze trend
                    slope, p_value = time_series.analyze_trend(time_series_data, dates)
                    
                    # Calculate seasonal metrics (this is just a simulation)
                    metrics = time_series.calculate_seasonal_metrics(time_series_data, dates)
                    
                    # Create visualizations
                    trend_viz = time_series.create_trend_visualization(slope, p_value)
                    
                    # Generate report
                    ts_report = time_series.generate_time_series_report(metrics)
                    
                    # Store results
                    st.session_state.time_series_results = {
                        'slope': slope,
                        'p_value': p_value,
                        'metrics': metrics,
                        'trend_viz': trend_viz,
                        'report': ts_report
                    }
                    
                    # Show the trend visualization
                    st.session_state.filtered_image = trend_viz[:, :, :3]  # Remove alpha channel
                    
                    st.success("Time series simulation complete!")
            else:
                st.error("Please ensure both original and filtered images are available.")
        
        # Display time series results if available
        if 'time_series_results' in st.session_state and st.session_state.time_series_results:
            results = st.session_state.time_series_results
            
            # Show time series report
            with st.expander("View Time Series Report (Simulated)"):
                st.markdown(results['report'])
    
    # AI Analysis Tab
    with main_tabs[3]:
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
                    
                    # Get selected AI provider
                    if 'selected_ai_provider' not in st.session_state:
                        st.session_state.selected_ai_provider = "openai"
                        
                    # Get available providers and check if selected provider is available
                    available_providers = ai_providers.get_available_providers()
                    
                    if len(available_providers) == 0:
                        analysis_results = {
                            "error": "No AI providers available. Please add your API keys in the Settings tab.",
                            "features_detected": [],
                            "filter_effects": [],
                            "environmental_patterns": [],
                            "applications": [],
                            "recommendations": [],
                            "summary": "Error: No AI API keys configured. Go to Settings tab to add your API keys."
                        }
                    elif st.session_state.selected_ai_provider not in available_providers:
                        # If selected provider is not available, use the first available one
                        st.session_state.selected_ai_provider = available_providers[0]
                        st.info(f"Selected provider not available. Using {available_providers[0]} instead.")
                        
                        # Run AI analysis with available provider
                        analysis_results = ai_providers.analyze_satellite_image(
                            st.session_state.preprocessed_image,
                            st.session_state.filtered_image,
                            filter_type,
                            provider=st.session_state.selected_ai_provider
                        )
                    else:
                        # Run AI analysis with selected provider
                        analysis_results = ai_providers.analyze_satellite_image(
                            st.session_state.preprocessed_image,
                            st.session_state.filtered_image,
                            filter_type,
                            provider=st.session_state.selected_ai_provider
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
    # Satellite Orbits Tab
    with main_tabs[5]:
        st.subheader("Satellite Orbit Visualization")
        st.markdown("""
        Visualize satellite orbits and data collection paths. This tool helps understand how
        remote sensing satellites capture imagery and their coverage patterns.
        """)
        
        # Create tabs for different visualizations
        orbit_tabs = st.tabs(["3D Orbit Animation", "Coverage Map", "Satellite Information"])
        
        # 3D Orbit Animation tab
        with orbit_tabs[0]:
            st.subheader("Satellite Orbit Animation")
            
            # Satellite selection
            satellite_options = satellite_orbit.get_satellite_list()
            selected_satellite = st.selectbox(
                "Select satellite:",
                satellite_options,
                index=0,
                key="orbit_satellite_select"
            )
            
            # Animation options
            col1, col2 = st.columns(2)
            with col1:
                duration = st.slider(
                    "Animation duration (hours):",
                    min_value=1,
                    max_value=8,
                    value=4,
                    step=1,
                    key="orbit_duration"
                )
            
            with col2:
                show_ground_track = st.checkbox(
                    "Show ground track",
                    value=True,
                    key="orbit_ground_track"
                )
            
            # Generate animation button
            if st.button("Generate Orbit Animation", key="generate_orbit_btn"):
                with st.spinner(f"Generating orbit animation for {selected_satellite}..."):
                    try:
                        # Generate the orbit animation
                        animation_html, satellite_info = satellite_orbit.create_orbit_animation(
                            selected_satellite,
                            ground_track=show_ground_track,
                            duration_hours=duration
                        )
                        
                        # Store in session state
                        st.session_state.orbit_animation = animation_html
                        st.session_state.selected_satellite_info = satellite_info
                        
                        # Success message
                        st.success(f"Orbit animation for {selected_satellite} generated successfully!")
                    except Exception as e:
                        st.error(f"Error generating orbit animation: {str(e)}")
            
            # Display the animation if available
            if 'orbit_animation' in st.session_state:
                st.subheader("Satellite Orbit")
                st.components.v1.html(st.session_state.orbit_animation, height=600)
                
                # Display satellite information
                if 'selected_satellite_info' in st.session_state:
                    info = st.session_state.selected_satellite_info
                    st.info(f"""
                    **Satellite Information:**
                    - **Altitude:** {info['altitude']} km
                    - **Inclination:** {info['inclination']}°
                    - **Orbital Period:** {info['period']} minutes
                    - **Sensor Resolution:** {info['sensor_resolution']} meters
                    - **Swath Width:** {info['swath_width']} km
                    - **Launch Date:** {info['launch_date']}
                    """)
        
        # Coverage Map tab
        with orbit_tabs[1]:
            st.subheader("Satellite Coverage Map")
            
            # Satellite selection
            satellite_options = satellite_orbit.get_satellite_list()
            selected_satellite = st.selectbox(
                "Select satellite:",
                satellite_options,
                index=0,
                key="coverage_satellite_select"
            )
            
            # Location input
            st.markdown("#### Target Location")
            st.markdown("Enter the coordinates of the area you want to analyze:")
            
            col1, col2 = st.columns(2)
            with col1:
                latitude = st.number_input(
                    "Latitude:",
                    min_value=-90.0,
                    max_value=90.0,
                    value=40.7128,
                    step=0.1,
                    format="%.4f",
                    key="coverage_lat"
                )
            
            with col2:
                longitude = st.number_input(
                    "Longitude:",
                    min_value=-180.0,
                    max_value=180.0,
                    value=-74.0060,
                    step=0.1,
                    format="%.4f",
                    key="coverage_lon"
                )
            
            # Generate coverage map button
            if st.button("Generate Coverage Map", key="generate_coverage_btn"):
                with st.spinner(f"Generating coverage map for {selected_satellite}..."):
                    try:
                        # Generate the coverage map
                        coverage_fig, coverage_info = satellite_orbit.create_coverage_map(
                            selected_satellite,
                            location=(latitude, longitude)
                        )
                        
                        # Store in session state
                        st.session_state.coverage_fig = coverage_fig
                        st.session_state.coverage_info = coverage_info
                        
                        # Success message
                        st.success(f"Coverage map for {selected_satellite} generated successfully!")
                    except Exception as e:
                        st.error(f"Error generating coverage map: {str(e)}")
            
            # Display the coverage map if available
            if 'coverage_fig' in st.session_state:
                st.pyplot(st.session_state.coverage_fig)
                
                # Display coverage information
                if 'coverage_info' in st.session_state:
                    info = st.session_state.coverage_info
                    st.info(f"""
                    **Coverage Information:**
                    - **Swath Width:** {info['swath_width']} km
                    - **Ground Coverage Radius:** {info['ground_coverage_radius']:.2f} km
                    - **Time in View:** {info['time_in_view']:.2f} seconds
                    - **Orbital Velocity:** {info['orbital_velocity']:.2f} km/s
                    """)
        
        # Satellite Information tab
        with orbit_tabs[2]:
            st.subheader("Satellite Catalog Information")
            st.markdown("""
            This table provides information about the various satellites used for remote sensing
            and their orbital parameters.
            """)
            
            # Generate satellite information table
            satellite_table = satellite_orbit.display_satellite_info_table()
            
            # Display the table
            st.components.v1.html(satellite_table, height=400)
            
            # Add explanations
            with st.expander("Understanding Orbital Parameters"):
                st.markdown("""
                ### Key Orbital Parameters:
                
                - **Altitude:** Height above Earth's surface (km)
                - **Inclination:** Angle between the orbital plane and Earth's equator (degrees)
                - **Period:** Time taken to complete one orbit (minutes)
                - **Swath Width:** Width of area captured in a single pass (km)
                - **Resolution:** Smallest object that can be distinguished in imagery (meters)
                
                ### Common Orbit Types:
                
                - **Low Earth Orbit (LEO):** 500-1000 km, period of ~90-100 minutes
                - **Polar Orbit:** High inclination orbit (near 90°) that passes over both poles
                - **Sun-Synchronous Orbit:** Special case of polar orbit that maintains constant solar illumination
                - **Geostationary Orbit:** 35,786 km altitude with period of exactly 24 hours (stays over the same point)
                """)
            
            # Add application to remote sensing
            with st.expander("Relevance to Remote Sensing"):
                st.markdown("""
                ### How Orbital Parameters Affect Remote Sensing:
                
                - **Altitude** affects resolution, field of view, and revisit time
                - **Inclination** determines what parts of Earth the satellite can observe
                - **Period** affects how frequently a location can be revisited
                - **Swath Width** determines the area covered in a single pass
                - **Resolution** determines the level of detail visible in imagery
                
                ### Satellite Sensor Types:
                
                - **Optical:** Captures visible and near-infrared light (similar to photography)
                - **Synthetic Aperture Radar (SAR):** Uses radar to "see" through clouds and darkness
                - **Thermal:** Captures heat signatures
                - **Hyperspectral:** Captures hundreds of spectral bands for detailed analysis
                - **LIDAR:** Uses laser to measure distance and create 3D models
                """)
                
    with main_tabs[6]:
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
                report = ai_providers.generate_full_report(
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
    # Settings Tab
    with main_tabs[7]:
        st.subheader("Application Settings")
        st.markdown("""
        Configure your API keys and satellite data sources here. 
        These settings will be saved to your .env file for future use.
        """)
        
        # AI Model Settings
        st.subheader("AI Model Configuration")
        
        # Get available providers
        available_providers = ai_providers.get_available_providers()
        if not available_providers:
            st.warning("No AI providers are currently configured. Add your API keys below.")
        else:
            st.success(f"Available AI providers: {', '.join(available_providers)}")
            
            # Select AI provider for analysis
            selected_provider = st.selectbox(
                "Select AI provider for analysis:",
                available_providers if available_providers else ["openai", "anthropic", "xai"],
                index=0 if "openai" not in available_providers else available_providers.index("openai"),
                key="provider_select"
            )
            
            # Update session state with selected provider
            if st.button("Set as Default Provider"):
                st.session_state.selected_ai_provider = selected_provider
                st.success(f"Default provider set to {selected_provider}")
                
        # API Key Management
        st.subheader("API Key Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### OpenAI API Key")
            openai_key = st.text_input(
                "Enter your OpenAI API key:",
                type="password",
                key="openai_key_input",
                help="Get your API key from https://platform.openai.com/api-keys"
            )
            
            st.markdown("##### xAI (Grok) API Key")
            xai_key = st.text_input(
                "Enter your xAI API key:",
                type="password",
                key="xai_key_input",
                help="Get your API key from xAI"
            )
        
        with col2:
            st.markdown("##### Anthropic API Key")
            anthropic_key = st.text_input(
                "Enter your Anthropic API key:",
                type="password",
                key="anthropic_key_input",
                help="Get your API key from https://console.anthropic.com/"
            )
            
            # Space for alignment
            st.write("")
            st.write("")
            
        # Save API keys button
        if st.button("Save API Keys to .env"):
            # Read existing .env file
            try:
                with open('.env', 'r') as f:
                    env_content = f.read()
                    
                # Update API keys if provided
                if openai_key:
                    if 'OPENAI_API_KEY=' in env_content:
                        env_content = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={openai_key}', env_content)
                    else:
                        env_content += f'\nOPENAI_API_KEY={openai_key}'
                
                if anthropic_key:
                    if 'ANTHROPIC_API_KEY=' in env_content:
                        env_content = re.sub(r'ANTHROPIC_API_KEY=.*', f'ANTHROPIC_API_KEY={anthropic_key}', env_content)
                    else:
                        env_content += f'\nANTHROPIC_API_KEY={anthropic_key}'
                
                if xai_key:
                    if 'XAI_API_KEY=' in env_content:
                        env_content = re.sub(r'XAI_API_KEY=.*', f'XAI_API_KEY={xai_key}', env_content)
                    else:
                        env_content += f'\nXAI_API_KEY={xai_key}'
                
                # Write updated content back to .env
                with open('.env', 'w') as f:
                    f.write(env_content)
                
                st.success("API keys saved successfully! Reload the application to apply changes.")
                st.info("Click the 'Reload App' button below to reload with new API keys.")
                
                # Reload button
                if st.button("Reload App"):
                    st.experimental_rerun()
                    
            except Exception as e:
                st.error(f"Error saving API keys: {str(e)}")
        
        # Satellite Data Sources
        st.subheader("Satellite Data Sources")
        
        # Check available satellite sources
        available_sources = satellite_fetcher.get_available_sources()
        if not available_sources:
            st.warning("No satellite data sources are configured. Add your credentials below.")
        else:
            st.success(f"Available satellite data sources: {', '.join(available_sources)}")
        
        # Earth Engine credentials
        st.markdown("##### Google Earth Engine")
        ee_user = st.text_input("Earth Engine Username:", key="ee_user")
        ee_password = st.text_input("Earth Engine Password:", type="password", key="ee_pass")
        
        # Sentinel Hub credentials
        st.markdown("##### Sentinel Hub")
        sentinel_user = st.text_input("Sentinel Hub Username:", key="sentinel_user")
        sentinel_password = st.text_input("Sentinel Hub Password:", type="password", key="sentinel_pass")
        
        # Save satellite credentials
        if st.button("Save Satellite Credentials"):
            # Read existing .env file
            try:
                with open('.env', 'r') as f:
                    env_content = f.read()
                    
                # Update credentials if provided
                if ee_user:
                    if 'EARTHENGINE_USER=' in env_content:
                        env_content = re.sub(r'EARTHENGINE_USER=.*', f'EARTHENGINE_USER={ee_user}', env_content)
                    else:
                        env_content += f'\nEARTHENGINE_USER={ee_user}'
                
                if ee_password:
                    if 'EARTHENGINE_PASSWORD=' in env_content:
                        env_content = re.sub(r'EARTHENGINE_PASSWORD=.*', f'EARTHENGINE_PASSWORD={ee_password}', env_content)
                    else:
                        env_content += f'\nEARTHENGINE_PASSWORD={ee_password}'
                
                if sentinel_user:
                    if 'SENTINEL_USER=' in env_content:
                        env_content = re.sub(r'SENTINEL_USER=.*', f'SENTINEL_USER={sentinel_user}', env_content)
                    else:
                        env_content += f'\nSENTINEL_USER={sentinel_user}'
                
                if sentinel_password:
                    if 'SENTINEL_PASSWORD=' in env_content:
                        env_content = re.sub(r'SENTINEL_PASSWORD=.*', f'SENTINEL_PASSWORD={sentinel_password}', env_content)
                    else:
                        env_content += f'\nSENTINEL_PASSWORD={sentinel_password}'
                
                # Write updated content back to .env
                with open('.env', 'w') as f:
                    f.write(env_content)
                
                st.success("Satellite credentials saved successfully! Reload the application to apply changes.")
                
                # Reload button
                if st.button("Reload App", key="reload_satellite"):
                    st.experimental_rerun()
                    
            except Exception as e:
                st.error(f"Error saving satellite credentials: {str(e)}")
else:
    # Display documentation and app information when no image is uploaded
    st.info("👈 Please upload an image using the sidebar to begin analysis.")
    
    # Create tabs for different documentation sections
    doc_tabs = st.tabs(["Overview", "Spectral Analysis", "Land Cover", "Change Detection", "Time Series", "AI Analysis", "FAQ", "Settings"])
    
    with doc_tabs[0]:
        st.markdown(documentation.get_documentation_section("overview"))
    
    with doc_tabs[1]:
        st.markdown(documentation.get_documentation_section("spectral_analysis"))
    
    with doc_tabs[2]:
        st.markdown(documentation.get_documentation_section("land_cover"))
    
    with doc_tabs[3]:
        st.markdown(documentation.get_documentation_section("change_detection"))
    
    with doc_tabs[4]:
        st.markdown(documentation.get_documentation_section("time_series"))
        
    with doc_tabs[5]:
        st.markdown(documentation.get_documentation_section("ai_analysis"))
        
    with doc_tabs[6]:
        st.markdown(documentation.get_documentation_section("faq"))
        
    # Settings Tab (when no image is loaded)
    with doc_tabs[7]:
        st.subheader("Application Settings")
        st.markdown("""
        Configure your API keys and satellite data sources here. 
        These settings will be saved to your .env file for future use.
        """)
        
        # AI Model Settings
        st.subheader("AI Model Configuration")
        
        # Get available providers
        available_providers = ai_providers.get_available_providers()
        if not available_providers:
            st.warning("No AI providers are currently configured. Add your API keys below.")
        else:
            st.success(f"Available AI providers: {', '.join(available_providers)}")
            
        # API Key Management
        st.subheader("API Key Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### OpenAI API Key")
            openai_key = st.text_input(
                "Enter your OpenAI API key:",
                type="password",
                key="openai_key_input_doc",
                help="Get your API key from https://platform.openai.com/api-keys"
            )
            
            st.markdown("##### xAI (Grok) API Key")
            xai_key = st.text_input(
                "Enter your xAI API key:",
                type="password",
                key="xai_key_input_doc",
                help="Get your API key from xAI"
            )
        
        with col2:
            st.markdown("##### Anthropic API Key")
            anthropic_key = st.text_input(
                "Enter your Anthropic API key:",
                type="password",
                key="anthropic_key_input_doc",
                help="Get your API key from https://console.anthropic.com/"
            )
            
            # Space for alignment
            st.write("")
            st.write("")
            
        # Save API keys button
        if st.button("Save API Keys to .env", key="save_api_keys_doc"):
            # Read existing .env file
            try:
                with open('.env', 'r') as f:
                    env_content = f.read()
                    
                # Update API keys if provided
                if openai_key:
                    if 'OPENAI_API_KEY=' in env_content:
                        env_content = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={openai_key}', env_content)
                    else:
                        env_content += f'\nOPENAI_API_KEY={openai_key}'
                
                if anthropic_key:
                    if 'ANTHROPIC_API_KEY=' in env_content:
                        env_content = re.sub(r'ANTHROPIC_API_KEY=.*', f'ANTHROPIC_API_KEY={anthropic_key}', env_content)
                    else:
                        env_content += f'\nANTHROPIC_API_KEY={anthropic_key}'
                
                if xai_key:
                    if 'XAI_API_KEY=' in env_content:
                        env_content = re.sub(r'XAI_API_KEY=.*', f'XAI_API_KEY={xai_key}', env_content)
                    else:
                        env_content += f'\nXAI_API_KEY={xai_key}'
                
                # Write updated content back to .env
                with open('.env', 'w') as f:
                    f.write(env_content)
                
                st.success("API keys saved successfully! Reload the application to apply changes.")
                
                # Reload button
                if st.button("Reload App", key="reload_app_doc"):
                    st.experimental_rerun()
                    
            except Exception as e:
                st.error(f"Error saving API keys: {str(e)}")
            
        # Satellite Data Sources
        st.subheader("Satellite Data Sources")
        
        # Check available satellite sources
        available_sources = satellite_fetcher.get_available_sources()
        if not available_sources:
            st.warning("No satellite data sources are configured. Add your credentials below.")
        else:
            st.success(f"Available satellite data sources: {', '.join(available_sources)}")
            
        # Earth Engine credentials
        st.markdown("##### Google Earth Engine")
        ee_user = st.text_input("Earth Engine Username:", key="ee_user_doc")
        ee_password = st.text_input("Earth Engine Password:", type="password", key="ee_pass_doc")
        
        # Sentinel Hub credentials
        st.markdown("##### Sentinel Hub")
        sentinel_user = st.text_input("Sentinel Hub Username:", key="sentinel_user_doc")
        sentinel_password = st.text_input("Sentinel Hub Password:", type="password", key="sentinel_pass_doc")
        
        # Save satellite credentials
        if st.button("Save Satellite Credentials", key="save_satellite_creds_doc"):
            # Read existing .env file
            try:
                with open('.env', 'r') as f:
                    env_content = f.read()
                    
                # Update credentials if provided
                if ee_user:
                    if 'EARTHENGINE_USER=' in env_content:
                        env_content = re.sub(r'EARTHENGINE_USER=.*', f'EARTHENGINE_USER={ee_user}', env_content)
                    else:
                        env_content += f'\nEARTHENGINE_USER={ee_user}'
                
                if ee_password:
                    if 'EARTHENGINE_PASSWORD=' in env_content:
                        env_content = re.sub(r'EARTHENGINE_PASSWORD=.*', f'EARTHENGINE_PASSWORD={ee_password}', env_content)
                    else:
                        env_content += f'\nEARTHENGINE_PASSWORD={ee_password}'
                
                if sentinel_user:
                    if 'SENTINEL_USER=' in env_content:
                        env_content = re.sub(r'SENTINEL_USER=.*', f'SENTINEL_USER={sentinel_user}', env_content)
                    else:
                        env_content += f'\nSENTINEL_USER={sentinel_user}'
                
                if sentinel_password:
                    if 'SENTINEL_PASSWORD=' in env_content:
                        env_content = re.sub(r'SENTINEL_PASSWORD=.*', f'SENTINEL_PASSWORD={sentinel_password}', env_content)
                    else:
                        env_content += f'\nSENTINEL_PASSWORD={sentinel_password}'
                
                # Write updated content back to .env
                with open('.env', 'w') as f:
                    f.write(env_content)
                
                st.success("Satellite credentials saved successfully! Reload the application to apply changes.")
                
                # Reload button
                if st.button("Reload App", key="reload_satellite_doc"):
                    st.experimental_rerun()
                    
            except Exception as e:
                st.error(f"Error saving satellite credentials: {str(e)}")

# Footer with social media links and expanded features
st.markdown("---")

# Set dark theme for footer
st.markdown("""
<style>
    .footer-container {
        background-color: #262730;
        padding: 20px;
        border-radius: 5px;
        margin-top: 20px;
        color: white;
    }
    .footer-title {
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .footer-text {
        color: white;
        font-size: 0.9rem;
    }
    .footer-link {
        color: #4c8bf5;
        text-decoration: none;
    }
    .footer-link:hover {
        text-decoration: underline;
    }
    .footer-icon {
        filter: invert(1);
    }
    .footer-copyright {
        background-color: #1e1e1e;
        padding: 10px;
        border-radius: 5px;
        margin-top: 20px;
        text-align: center;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Main footer content in a dark-themed container
st.markdown('<div class="footer-container">', unsafe_allow_html=True)

footer_cols = st.columns([1, 1, 1])

with footer_cols[0]:
    st.markdown('<div class="footer-title">Remote Sensing Data Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer-text">A tool for environmental scientists and GIS analysts</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer-text">© 2025 Icradle Innovations Ltd. All rights reserved.</div>', unsafe_allow_html=True)
    
    # Add home button
    if st.button("🏠 Home"):
        st.session_state.uploaded_file = None
        st.session_state.image_data = None
        st.rerun()

with footer_cols[1]:
    st.markdown('<div class="footer-title">Connect With Us</div>', unsafe_allow_html=True)
    
    # Social media links with nicer styling - using white icons and text
    social_links = """
    <div style="display: flex; flex-direction: column; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <a href="{github_url}" target="_blank" style="display: flex; align-items: center; text-decoration: none; color: white;">
                <img src="https://img.icons8.com/ios-glyphs/30/ffffff/github.png" width="20" height="20" class="footer-icon">
                <span style="margin-left: 5px;">GitHub</span>
            </a>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <a href="{website_url}" target="_blank" style="display: flex; align-items: center; text-decoration: none; color: white;">
                <img src="https://img.icons8.com/ios-glyphs/30/ffffff/domain.png" width="20" height="20" class="footer-icon">
                <span style="margin-left: 5px;">Website</span>
            </a>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <a href="{linkedin_url}" target="_blank" style="display: flex; align-items: center; text-decoration: none; color: white;">
                <img src="https://img.icons8.com/ios-glyphs/30/ffffff/linkedin.png" width="20" height="20" class="footer-icon">
                <span style="margin-left: 5px;">LinkedIn</span>
            </a>
        </div>
    </div>
    """.format(
        github_url=os.environ.get("GITHUB_URL", "#"),
        website_url=os.environ.get("WEBSITE_URL", "#"),
        linkedin_url=os.environ.get("LINKEDIN_URL", "#")
    )
    
    st.markdown(social_links, unsafe_allow_html=True)

with footer_cols[2]:
    st.markdown('<div class="footer-title">More Resources</div>', unsafe_allow_html=True)
    
    # Additional links and resources with white text
    additional_links = """
    <div style="display: flex; flex-direction: column; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <a href="{youtube_url}" target="_blank" style="display: flex; align-items: center; text-decoration: none; color: white;">
                <img src="https://img.icons8.com/ios-glyphs/30/ffffff/youtube-play.png" width="20" height="20" class="footer-icon">
                <span style="margin-left: 5px;">YouTube Tutorials</span>
            </a>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <a href="{twitter_url}" target="_blank" style="display: flex; align-items: center; text-decoration: none; color: white;">
                <img src="https://img.icons8.com/ios-glyphs/30/ffffff/twitter.png" width="20" height="20" class="footer-icon">
                <span style="margin-left: 5px;">Twitter</span>
            </a>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <a href="{facebook_url}" target="_blank" style="display: flex; align-items: center; text-decoration: none; color: white;">
                <img src="https://img.icons8.com/ios-glyphs/30/ffffff/facebook-new.png" width="20" height="20" class="footer-icon">
                <span style="margin-left: 5px;">Facebook</span>
            </a>
        </div>
    </div>
    """.format(
        youtube_url=os.environ.get("YOUTUBE_URL", "#"),
        twitter_url=os.environ.get("TWITTER_URL", "#"),
        facebook_url=os.environ.get("FACEBOOK_URL", "#")
    )
    
    st.markdown(additional_links, unsafe_allow_html=True)

# Close the footer container
st.markdown('</div>', unsafe_allow_html=True)

# Copyright notice in a dark-themed bar
st.markdown("""
<div class="footer-copyright">
    Created by Icradle Innovations Ltd. | All data analysis and visualizations are for informational purposes only.
</div>
""", unsafe_allow_html=True)
