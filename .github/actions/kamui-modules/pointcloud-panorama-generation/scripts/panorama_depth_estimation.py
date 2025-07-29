#!/usr/bin/env python3
import cv2
import numpy as np
import sys
import os
from PIL import Image
import time

def load_panorama_image(image_path):
    """Load and validate panorama image"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        height, width = img.shape[:2]
        aspect_ratio = width / height
        
        print(f"📐 Image dimensions: {width}x{height} (aspect ratio: {aspect_ratio:.2f})")
        
        # Check if it's approximately 2:1 (equirectangular)
        if abs(aspect_ratio - 2.0) > 0.5:
            print(f"⚠️  Warning: Image aspect ratio {aspect_ratio:.2f} is not close to 2:1")
            print("    Equirectangular panoramas should have 2:1 aspect ratio")
        
        return img
        
    except Exception as e:
        print(f"❌ Error loading panorama: {e}")
        sys.exit(1)

def simulate_midas_depth_estimation(image, target_resolution):
    """Simulate MiDaS depth estimation for panorama images"""
    print(f"🎯 Target depth resolution: {target_resolution}")
    
    # Parse resolution
    width_str, height_str = target_resolution.split('x')
    target_width, target_height = int(width_str), int(height_str)
    
    # Resize image for processing
    resized = cv2.resize(image, (target_width, target_height))
    
    # Convert to grayscale for depth simulation
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    
    # Simulate depth estimation using edge-based heuristics
    # Real MiDaS would use deep learning model here
    
    # Apply Gaussian blur to simulate depth
    blurred = cv2.GaussianBlur(gray, (15, 15), 0)
    
    # Create depth map using gradient magnitude and brightness
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
    
    # Normalize gradient
    gradient_magnitude = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX)
    
    # Combine brightness and edge information for depth
    # Brighter areas tend to be closer, edges tend to be closer
    brightness_weight = 0.4
    edge_weight = 0.6
    
    # Invert brightness (darker = farther in typical scenarios)
    inverted_brightness = 255 - blurred
    
    # Combine for final depth map
    depth_map = (inverted_brightness * brightness_weight + 
                gradient_magnitude * edge_weight).astype(np.uint8)
    
    # Apply panorama-specific corrections
    height, width = depth_map.shape
    
    # Pole area compression - reduce depth variation near poles
    for y in range(height):
        pole_factor = abs(y - height/2) / (height/2)  # 0 at equator, 1 at poles
        compression = 1.0 - pole_factor * 0.3  # Reduce variation by up to 30% at poles
        depth_map[y, :] = depth_map[y, :] * compression
    
    # Seamline continuity - ensure left and right edges match
    edge_width = max(1, width // 100)  # 1% of width
    left_edge = depth_map[:, :edge_width].mean(axis=1)
    right_edge = depth_map[:, -edge_width:].mean(axis=1)
    average_edge = (left_edge + right_edge) / 2
    
    for i, avg_val in enumerate(average_edge):
        depth_map[i, :edge_width] = avg_val
        depth_map[i, -edge_width:] = avg_val
    
    return depth_map

def save_depth_maps(depth_map, output_dir, base_name):
    """Save depth maps in multiple formats"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Created/verified output directory: {output_dir}")
    
    # Save grayscale depth map
    depth_gray_path = os.path.join(output_dir, f"{base_name}_depth_gray.png")
    success = cv2.imwrite(depth_gray_path, depth_map)
    if not success:
        raise RuntimeError(f"Failed to save grayscale depth map: {depth_gray_path}")
    print(f"💾 Saved grayscale depth map: {depth_gray_path}")
    
    # Save colorized depth map for visualization
    depth_color = cv2.applyColorMap(depth_map, cv2.COLORMAP_PLASMA)
    depth_color_path = os.path.join(output_dir, f"{base_name}_depth.png")
    success = cv2.imwrite(depth_color_path, depth_color)
    if not success:
        raise RuntimeError(f"Failed to save color depth map: {depth_color_path}")
    print(f"💾 Saved color depth map: {depth_color_path}")
    
    # Calculate statistics
    mean_depth = np.mean(depth_map)
    std_depth = np.std(depth_map)
    min_depth = np.min(depth_map)
    max_depth = np.max(depth_map)
    
    print(f"📊 Depth Statistics:")
    print(f"   Mean: {mean_depth:.2f}")
    print(f"   Std:  {std_depth:.2f}")  
    print(f"   Range: {min_depth} - {max_depth}")
    
    return depth_gray_path, depth_color_path

def main():
    if len(sys.argv) != 4:
        print("Usage: python panorama_depth_estimation.py <input_image> <output_dir> <resolution>")
        sys.exit(1)
    
    input_image = sys.argv[1]
    output_dir = sys.argv[2]
    target_resolution = sys.argv[3]
    
    # Convert to absolute paths using GitHub workspace
    workspace = os.environ.get("GITHUB_WORKSPACE", os.getcwd())
    print(f"🌐 GitHub workspace: {workspace}")
    print(f"🌐 Current working directory: {os.getcwd()}")
    
    # Make paths absolute relative to workspace
    if not os.path.isabs(input_image):
        input_image = os.path.join(workspace, input_image)
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(workspace, output_dir)
    
    print(f"🔍 Absolute input image: {input_image}")
    print(f"🔍 Absolute output directory: {output_dir}")
    
    print(f"🌐 Starting panorama depth estimation...")
    print(f"   Input: {input_image}")
    print(f"   Output: {output_dir}")
    print(f"   Resolution: {target_resolution}")
    
    start_time = time.time()
    
    # Load panorama image
    panorama = load_panorama_image(input_image)
    
    # Generate depth estimation
    depth_map = simulate_midas_depth_estimation(panorama, target_resolution)
    
    # Save results
    base_name = os.path.splitext(os.path.basename(input_image))[0]
    depth_gray_path, depth_color_path = save_depth_maps(depth_map, output_dir, base_name)
    
    processing_time = time.time() - start_time
    
    print(f"✅ Depth estimation completed in {processing_time:.2f} seconds")
    print(f"   Grayscale depth: {depth_gray_path}")
    print(f"   Color depth: {depth_color_path}")
    
    # Verify files exist and are readable
    if os.path.exists(depth_gray_path):
        size = os.path.getsize(depth_gray_path)
        print(f"✅ Grayscale depth file verified: {size} bytes")
    else:
        print(f"❌ Grayscale depth file not found: {depth_gray_path}")
    
    if os.path.exists(depth_color_path):
        size = os.path.getsize(depth_color_path)
        print(f"✅ Color depth file verified: {size} bytes")
    else:
        print(f"❌ Color depth file not found: {depth_color_path}")
    
    # Debug: List directory contents
    print(f"🔍 Final directory contents in {output_dir}:")
    try:
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            size = os.path.getsize(item_path) if os.path.isfile(item_path) else "DIR"
            print(f"   {item} ({size} bytes)" if size != "DIR" else f"   {item}/")
    except Exception as e:
        print(f"❌ Could not list directory: {e}")
    
    # Output paths for GitHub Actions
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f"depth_gray_path={depth_gray_path}\n")
        f.write(f"depth_color_path={depth_color_path}\n")
        f.write(f"processing_time={processing_time:.2f}\n")

if __name__ == "__main__":
    main()