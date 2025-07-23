#!/usr/bin/env python3
"""
MiDaS depth estimation script for 2D to 3D pointcloud generation pipeline
Supports CPU inference with memory optimization for GitHub Actions
"""

import argparse
import os
import sys
import logging
from pathlib import Path

import torch
import cv2
import numpy as np
from PIL import Image
import urllib.request
import urllib.error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MiDaSDepthEstimator:
    """MiDaS depth estimation with CPU optimization"""
    
    def __init__(self, model_name='midas_v21_small'):
        self.model_name = model_name
        self.device = 'cpu'  # Force CPU for GitHub Actions compatibility
        self.model = None
        self.transform = None
        
        # Model URLs and configurations
        self.model_configs = {
            'midas_v21_small': {
                'url': 'https://github.com/isl-org/MiDaS/releases/download/v2_1/midas_v21_small_256.pt',
                'input_size': 256,
                'memory_efficient': True
            },
            'midas_v21': {
                'url': 'https://github.com/isl-org/MiDaS/releases/download/v2_1/midas_v21_384.pt', 
                'input_size': 384,
                'memory_efficient': False
            }
        }
    
    def download_model(self, model_path):
        """Download MiDaS model if not exists"""
        if os.path.exists(model_path):
            logger.info(f"Model already exists: {model_path}")
            return True
            
        try:
            config = self.model_configs[self.model_name]
            logger.info(f"Downloading {self.model_name} from {config['url']}")
            
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Create opener that handles redirects properly
            opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
            urllib.request.install_opener(opener)
            
            # Add headers to mimic browser request
            req = urllib.request.Request(
                config['url'],
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            
            # Download with proper redirect handling
            with urllib.request.urlopen(req) as response, open(model_path, 'wb') as out_file:
                out_file.write(response.read())
            
            # Verify file was downloaded
            if os.path.getsize(model_path) < 1000:  # Less than 1KB suggests failed download
                raise RuntimeError(f"Downloaded file is too small: {os.path.getsize(model_path)} bytes")
            
            logger.info(f"Model downloaded successfully: {model_path} ({os.path.getsize(model_path)} bytes)")
            return True
            
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP Error {e.code}: {e.reason}")
            return False
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            return False
    
    def load_model(self):
        """Load MiDaS model"""
        try:
            # Ensure models directory exists
            models_dir = Path.home() / '.cache' / 'midas'
            models_dir.mkdir(parents=True, exist_ok=True)
            
            model_path = models_dir / f"{self.model_name}.pt"
            
            # Download model if needed
            if not self.download_model(model_path):
                raise RuntimeError(f"Failed to download model: {self.model_name}")
            
            # Load model
            logger.info(f"Loading model: {model_path}")
            self.model = torch.jit.load(model_path, map_location=self.device)
            self.model.eval()
            
            # Setup transform
            config = self.model_configs[self.model_name]
            self.input_size = config['input_size']
            
            logger.info(f"Model loaded successfully on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def preprocess_image(self, image_path):
        """Preprocess input image for MiDaS"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Cannot load image: {image_path}")
            
            original_height, original_width = image.shape[:2]
            logger.info(f"Original image size: {original_width}x{original_height}")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize while maintaining aspect ratio
            target_size = self.input_size
            aspect_ratio = original_width / original_height
            
            if aspect_ratio > 1:  # Landscape
                new_width = target_size
                new_height = int(target_size / aspect_ratio)
            else:  # Portrait or square
                new_height = target_size
                new_width = int(target_size * aspect_ratio)
            
            # Ensure dimensions are multiples of 32 for model compatibility
            new_width = (new_width // 32) * 32
            new_height = (new_height // 32) * 32
            
            image_resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Normalize to [0, 1]
            image_normalized = image_resized.astype(np.float32) / 255.0
            
            # Convert to tensor and add batch dimension
            input_tensor = torch.from_numpy(image_normalized).permute(2, 0, 1).unsqueeze(0)
            
            logger.info(f"Preprocessed image shape: {input_tensor.shape}")
            
            return input_tensor, (original_width, original_height), (new_width, new_height)
            
        except Exception as e:
            logger.error(f"Failed to preprocess image: {e}")
            return None, None, None
    
    def estimate_depth(self, image_path, output_path):
        """Estimate depth from image"""
        try:
            # Load model if not loaded
            if self.model is None:
                if not self.load_model():
                    return False
            
            # Preprocess image
            input_tensor, original_size, processed_size = self.preprocess_image(image_path)
            if input_tensor is None:
                return False
            
            logger.info("Running depth estimation...")
            
            # Inference
            with torch.no_grad():
                depth_tensor = self.model(input_tensor)
            
            # Post-process depth map
            depth = depth_tensor.squeeze().cpu().numpy()
            
            # Resize to original image dimensions
            depth_resized = cv2.resize(depth, original_size, interpolation=cv2.INTER_LANCZOS4)
            
            # Normalize depth values to [0, 255] for visualization
            depth_normalized = cv2.normalize(depth_resized, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            
            # Apply colormap for better visualization (optional)
            depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_PLASMA)
            
            # Save depth map
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save as grayscale for PLY conversion
            depth_gray_path = output_path.replace('.png', '_gray.png')
            cv2.imwrite(depth_gray_path, depth_normalized)
            
            # Save as colored for visualization
            cv2.imwrite(output_path, depth_colored)
            
            logger.info(f"Depth map saved: {output_path}")
            logger.info(f"Grayscale depth saved: {depth_gray_path}")
            
            # Log depth statistics
            logger.info(f"Depth range: [{depth_resized.min():.3f}, {depth_resized.max():.3f}]")
            logger.info(f"Depth mean: {depth_resized.mean():.3f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to estimate depth: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='MiDaS depth estimation for pointcloud generation')
    parser.add_argument('--input', '-i', required=True, help='Input image path')
    parser.add_argument('--output', '-o', required=True, help='Output depth map path')
    parser.add_argument('--model', '-m', default='midas_v21_small', 
                       choices=['midas_v21_small', 'midas_v21'],
                       help='MiDaS model to use')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate inputs
    if not os.path.exists(args.input):
        logger.error(f"Input image not found: {args.input}")
        sys.exit(1)
    
    # Initialize depth estimator
    estimator = MiDaSDepthEstimator(args.model)
    
    # Run depth estimation
    logger.info(f"Starting depth estimation: {args.input} -> {args.output}")
    success = estimator.estimate_depth(args.input, args.output)
    
    if success:
        logger.info("✅ Depth estimation completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Depth estimation failed")
        sys.exit(1)

if __name__ == '__main__':
    main()