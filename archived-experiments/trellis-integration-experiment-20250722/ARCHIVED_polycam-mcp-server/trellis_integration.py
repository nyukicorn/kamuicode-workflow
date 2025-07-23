#!/usr/bin/env python3
"""
TRELLIS integration for Polycam MCP Server
Handles actual 3D model generation using TRELLIS
"""

import os
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Union
from PIL import Image
import requests
from io import BytesIO

# TRELLIS imports (will be available after installation)
try:
    # Set environment variables before importing
    os.environ['SPCONV_ALGO'] = 'native'
    
    from trellis.pipelines import TrellisImageTo3DPipeline
    from trellis.utils import render_utils, postprocessing_utils
    TRELLIS_AVAILABLE = True
except ImportError:
    TRELLIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class TrellisGenerator:
    """TRELLIS 3D model generator"""
    
    def __init__(self):
        self.pipeline = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize TRELLIS pipeline"""
        if not TRELLIS_AVAILABLE:
            raise RuntimeError("TRELLIS is not installed. Please install TRELLIS first.")
        
        if self.initialized:
            return
            
        try:
            logger.info("Initializing TRELLIS pipeline...")
            # Load pipeline - this may take several minutes on first run
            self.pipeline = TrellisImageTo3DPipeline.from_pretrained("JeffreyXiang/TRELLIS-image-large")
            self.pipeline.cuda()
            self.initialized = True
            logger.info("TRELLIS pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TRELLIS: {e}")
            raise
    
    async def generate_from_text(self, prompt: str, output_path: str, output_format: str = "glb", **kwargs) -> str:
        """
        Generate 3D model from text prompt
        Note: TRELLIS primarily supports image-to-3D, so this would need additional text-to-image step
        """
        # For now, this is a placeholder - TRELLIS is primarily image-to-3D
        # We would need to integrate with text-to-image first, then image-to-3D
        raise NotImplementedError("Text-to-3D requires text-to-image preprocessing step")
    
    async def generate_from_image(
        self, 
        image_path_or_url: str, 
        output_path: str, 
        output_format: str = "glb",
        seed: int = 1,
        steps: int = 12,
        cfg_strength: float = 7.5,
        simplify: float = 0.95,
        texture_size: int = 1024
    ) -> str:
        """Generate 3D model from image"""
        
        await self.initialize()
        
        try:
            # Load image
            image = await self._load_image(image_path_or_url)
            
            logger.info(f"Generating 3D model from image using TRELLIS...")
            
            # Run TRELLIS pipeline
            outputs = self.pipeline.run(
                image,
                seed=seed,
                sparse_structure_sampler_params={
                    "steps": steps,
                    "cfg_strength": cfg_strength,
                },
                slat_sampler_params={
                    "steps": steps,
                    "cfg_strength": 3.0,
                }
            )
            
            # Save output based on format
            if output_format.lower() == "glb":
                glb = postprocessing_utils.to_glb(
                    outputs['gaussian'][0],
                    outputs['mesh'][0],
                    simplify=simplify,
                    texture_size=texture_size,
                )
                glb.export(output_path)
                logger.info(f"GLB file saved to: {output_path}")
                
            elif output_format.lower() == "ply":
                outputs['gaussian'][0].save_ply(output_path)
                logger.info(f"PLY file saved to: {output_path}")
                
            elif output_format.lower() == "mesh":
                # Save mesh in OBJ format
                mesh = outputs['mesh'][0]
                # TODO: Implement mesh export to OBJ
                # For now, fallback to GLB
                glb = postprocessing_utils.to_glb(
                    outputs['gaussian'][0],
                    outputs['mesh'][0],
                    simplify=simplify,
                    texture_size=texture_size,
                )
                glb_path = output_path.replace('.obj', '.glb')
                glb.export(glb_path)
                logger.info(f"Mesh saved as GLB to: {glb_path}")
                output_path = glb_path
            
            return output_path
            
        except Exception as e:
            logger.error(f"TRELLIS generation failed: {e}")
            raise
    
    async def _load_image(self, image_path_or_url: str) -> Image.Image:
        """Load image from path or URL"""
        try:
            if image_path_or_url.startswith(('http://', 'https://')):
                # Download from URL
                response = requests.get(image_path_or_url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            else:
                # Load from local file
                image = Image.open(image_path_or_url)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            return image
            
        except Exception as e:
            logger.error(f"Failed to load image from {image_path_or_url}: {e}")
            raise

# Global instance
_trellis_generator = None

def get_trellis_generator() -> TrellisGenerator:
    """Get global TRELLIS generator instance"""
    global _trellis_generator
    if _trellis_generator is None:
        _trellis_generator = TrellisGenerator()
    return _trellis_generator

async def generate_3d_model(
    input_type: str,
    input_data: str,
    output_path: str,
    output_format: str = "glb",
    **kwargs
) -> str:
    """
    Generate 3D model using TRELLIS
    
    Args:
        input_type: 'text' or 'image'
        input_data: text prompt or image path/URL
        output_path: where to save the output file
        output_format: 'glb', 'ply', or 'mesh'
        **kwargs: additional parameters
    
    Returns:
        Path to generated file
    """
    generator = get_trellis_generator()
    
    if input_type == 'image':
        return await generator.generate_from_image(
            input_data, output_path, output_format, **kwargs
        )
    elif input_type == 'text':
        return await generator.generate_from_text(
            input_data, output_path, output_format, **kwargs
        )
    else:
        raise ValueError(f"Unsupported input_type: {input_type}")

def is_trellis_available() -> bool:
    """Check if TRELLIS is available"""
    return TRELLIS_AVAILABLE