#!/usr/bin/env python3
"""
Simple depth estimation simulation for testing the pipeline
Creates a synthetic depth map without requiring MiDaS download
"""

import argparse
import os
import cv2
import numpy as np
from PIL import Image

def create_synthetic_depth(image_path, output_path):
    """Create a synthetic depth map from an image"""
    try:
        # Load original image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot load image: {image_path}")
        
        print(f"Processing image: {image_path}")
        print(f"Image shape: {image.shape}")
        
        # Convert to grayscale for depth calculation only (preserve original colors)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Create synthetic depth based on brightness
        # Brighter areas = closer, darker areas = farther
        depth = gray.astype(np.float32) / 255.0
        
        # Add some radial gradient effect
        height, width = gray.shape
        center_x, center_y = width // 2, height // 2
        
        y, x = np.ogrid[:height, :width]
        distance_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        radial_factor = 1.0 - (distance_from_center / max_distance) * 0.5
        
        # Combine brightness and radial depth
        depth_combined = depth * 0.7 + radial_factor * 0.3
        depth_combined = np.clip(depth_combined, 0, 1)
        
        # Convert to 8-bit
        depth_8bit = (depth_combined * 255).astype(np.uint8)
        
        # Save grayscale version for PLY conversion
        gray_output = output_path.replace('.png', '_gray.png')
        cv2.imwrite(gray_output, depth_8bit)
        
        # Create colored version for visualization
        depth_colored = cv2.applyColorMap(depth_8bit, cv2.COLORMAP_PLASMA)
        cv2.imwrite(output_path, depth_colored)
        
        print(f"✅ Synthetic depth map created: {output_path}")
        print(f"✅ Grayscale depth map: {gray_output}")
        print(f"Depth range: [0, 255]")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating synthetic depth: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Simple depth estimation for testing')
    parser.add_argument('--input', '-i', required=True, help='Input image path')
    parser.add_argument('--output', '-o', required=True, help='Output depth map path')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"❌ Input image not found: {args.input}")
        return 1
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    success = create_synthetic_depth(args.input, args.output)
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())