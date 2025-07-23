#!/usr/bin/env node
/**
 * Depth map to PLY pointcloud converter
 * Converts MiDaS depth maps to PLY format for Three.js visualization
 */

const fs = require('fs').promises;
const path = require('path');
const { createReadStream } = require('fs');
const { PNG } = require('pngjs');

class DepthToPLYConverter {
    constructor() {
        this.defaultOptions = {
            pointSpacing: 1,        // Distance between points
            depthScale: 100,        // Depth scaling factor
            invertDepth: true,      // Invert depth values
            useOriginalColors: true, // Use original image colors
            maxPoints: 100000       // Maximum points to prevent memory issues
        };
    }

    /**
     * Load PNG image as pixel data
     */
    async loadPNG(imagePath) {
        return new Promise((resolve, reject) => {
            const stream = createReadStream(imagePath).pipe(new PNG());
            
            stream.on('parsed', function() {
                resolve({
                    width: this.width,
                    height: this.height,
                    data: this.data
                });
            });
            
            stream.on('error', reject);
        });
    }

    /**
     * Convert depth map to point cloud data
     */
    async convertDepthToPoints(depthPath, originalImagePath = null, options = {}) {
        const opts = { ...this.defaultOptions, ...options };
        
        console.log(`📖 Loading depth map: ${depthPath}`);
        
        // Load depth map (grayscale)
        let depthData;
        try {
            // Try to load grayscale version first
            const grayPath = depthPath.replace('.png', '_gray.png');
            const grayExists = await fs.access(grayPath).then(() => true).catch(() => false);
            
            if (grayExists) {
                console.log(`📖 Using grayscale depth map: ${grayPath}`);
                depthData = await this.loadPNG(grayPath);
            } else {
                console.log(`📖 Using colored depth map: ${depthPath}`);
                depthData = await this.loadPNG(depthPath);
                // Convert to grayscale if colored
                if (depthData.data.length === depthData.width * depthData.height * 4) {
                    depthData = this.convertToGrayscale(depthData);
                }
            }
        } catch (error) {
            throw new Error(`Failed to load depth map: ${error.message}`);
        }

        // Load original image for colors (optional)
        let colorData = null;
        if (originalImagePath && opts.useOriginalColors) {
            try {
                console.log(`🎨 Loading original image for colors: ${originalImagePath}`);
                colorData = await this.loadPNG(originalImagePath);
                
                // Resize color data to match depth map if necessary
                if (colorData.width !== depthData.width || colorData.height !== depthData.height) {
                    console.log(`🔄 Resizing color image from ${colorData.width}x${colorData.height} to ${depthData.width}x${depthData.height}`);
                    colorData = this.resizeImageData(colorData, depthData.width, depthData.height);
                }
            } catch (error) {
                console.warn(`⚠️ Could not load original image, using depth-based colors: ${error.message}`);
                colorData = null;
            }
        }

        console.log(`🔢 Processing ${depthData.width}x${depthData.height} depth map`);
        
        const points = [];
        const { width, height } = depthData;
        const spacing = opts.pointSpacing;
        
        // Calculate sampling rate to limit points
        let sampleRate = Math.max(1, Math.ceil(Math.sqrt((width * height) / opts.maxPoints)));
        console.log(`📊 Sample rate: ${sampleRate} (targeting max ${opts.maxPoints} points)`);

        for (let y = 0; y < height; y += sampleRate) {
            for (let x = 0; x < width; x += sampleRate) {
                const idx = (y * width + x) * 4;
                
                // Get depth value (using red channel for grayscale)
                const depthValue = depthData.data[idx] / 255.0;
                
                // Skip completely black pixels (no depth)
                if (depthValue < 0.01) continue;

                // Convert to 3D coordinates
                const worldX = (x - width / 2) * spacing;
                const worldY = -(y - height / 2) * spacing; // Flip Y axis
                const worldZ = opts.invertDepth ? 
                    (1.0 - depthValue) * opts.depthScale : 
                    depthValue * opts.depthScale;

                // Get color
                let r, g, b;
                if (colorData) {
                    // Use original image colors
                    const colorIdx = (y * width + x) * 4;
                    r = colorData.data[colorIdx];
                    g = colorData.data[colorIdx + 1];
                    b = colorData.data[colorIdx + 2];
                } else {
                    // Use depth-based coloring
                    const intensity = Math.floor(depthValue * 255);
                    r = intensity;
                    g = intensity;
                    b = intensity;
                }

                points.push({
                    x: worldX,
                    y: worldY,
                    z: worldZ,
                    r: r,
                    g: g,
                    b: b
                });
            }
        }

        console.log(`✅ Generated ${points.length} points`);
        return points;
    }

    /**
     * Convert colored image data to grayscale
     */
    convertToGrayscale(imageData) {
        const { width, height, data } = imageData;
        const grayData = new Uint8Array(width * height * 4);
        
        for (let i = 0; i < data.length; i += 4) {
            const gray = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
            const outIdx = i;
            grayData[outIdx] = gray;     // R
            grayData[outIdx + 1] = gray; // G
            grayData[outIdx + 2] = gray; // B
            grayData[outIdx + 3] = 255;  // A
        }
        
        return {
            width,
            height,
            data: grayData
        };
    }

    /**
     * Simple nearest neighbor resize
     */
    resizeImageData(imageData, newWidth, newHeight) {
        const { width, height, data } = imageData;
        const newData = new Uint8Array(newWidth * newHeight * 4);
        
        for (let y = 0; y < newHeight; y++) {
            for (let x = 0; x < newWidth; x++) {
                const srcX = Math.floor((x / newWidth) * width);
                const srcY = Math.floor((y / newHeight) * height);
                
                const srcIdx = (srcY * width + srcX) * 4;
                const dstIdx = (y * newWidth + x) * 4;
                
                newData[dstIdx] = data[srcIdx];         // R
                newData[dstIdx + 1] = data[srcIdx + 1]; // G
                newData[dstIdx + 2] = data[srcIdx + 2]; // B
                newData[dstIdx + 3] = data[srcIdx + 3]; // A
            }
        }
        
        return {
            width: newWidth,
            height: newHeight,
            data: newData
        };
    }

    /**
     * Generate PLY file content
     */
    generatePLY(points) {
        const header = [
            'ply',
            'format ascii 1.0',
            `element vertex ${points.length}`,
            'property float x',
            'property float y', 
            'property float z',
            'property uchar red',
            'property uchar green',
            'property uchar blue',
            'end_header'
        ].join('\n');

        const vertices = points.map(p => 
            `${p.x.toFixed(6)} ${p.y.toFixed(6)} ${p.z.toFixed(6)} ${p.r} ${p.g} ${p.b}`
        ).join('\n');

        return header + '\n' + vertices;
    }

    /**
     * Convert depth map to PLY file
     */
    async convert(depthPath, outputPath, originalImagePath = null, options = {}) {
        try {
            console.log(`🚀 Starting depth-to-PLY conversion`);
            console.log(`   Input: ${depthPath}`);
            console.log(`   Output: ${outputPath}`);
            if (originalImagePath) {
                console.log(`   Colors: ${originalImagePath}`);
            }

            // Convert depth to points
            const points = await this.convertDepthToPoints(depthPath, originalImagePath, options);
            
            if (points.length === 0) {
                throw new Error('No valid points generated from depth map');
            }

            // Generate PLY content
            const plyContent = this.generatePLY(points);
            
            // Ensure output directory exists
            await fs.mkdir(path.dirname(outputPath), { recursive: true });
            
            // Write PLY file
            await fs.writeFile(outputPath, plyContent, 'utf8');
            
            console.log(`✅ PLY file saved: ${outputPath}`);
            console.log(`📊 File size: ${(plyContent.length / 1024).toFixed(1)} KB`);
            console.log(`📊 Point count: ${points.length}`);
            
            return {
                success: true,
                pointCount: points.length,
                fileSize: plyContent.length,
                outputPath
            };
            
        } catch (error) {
            console.error(`❌ Conversion failed: ${error.message}`);
            throw error;
        }
    }
}

// CLI interface
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 4) {
        console.log(`
Usage: node depth2ply.js --input <depth_map> --output <ply_file> [--original-image <image>] [options]

Options:
  --input             Input depth map path (PNG)
  --output            Output PLY file path
  --original-image    Original image for colors (optional)
  --point-spacing     Distance between points (default: 1)
  --depth-scale       Depth scaling factor (default: 100)
  --max-points        Maximum points (default: 100000)
  --no-invert-depth   Don't invert depth values
  --no-colors         Don't use original image colors

Example:
  node depth2ply.js --input depth.png --output pointcloud.ply --original-image photo.png
        `);
        process.exit(1);
    }

    // Parse arguments
    const options = {};
    let depthPath, outputPath, originalImagePath;
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--input':
                depthPath = args[++i];
                break;
            case '--output':
                outputPath = args[++i];
                break;
            case '--original-image':
                originalImagePath = args[++i];
                break;
            case '--point-spacing':
                options.pointSpacing = parseFloat(args[++i]);
                break;
            case '--depth-scale':
                options.depthScale = parseFloat(args[++i]);
                break;
            case '--max-points':
                options.maxPoints = parseInt(args[++i]);
                break;
            case '--no-invert-depth':
                options.invertDepth = false;
                break;
            case '--no-colors':
                options.useOriginalColors = false;
                break;
        }
    }

    if (!depthPath || !outputPath) {
        console.error('❌ Missing required arguments: --input and --output');
        process.exit(1);
    }

    try {
        const converter = new DepthToPLYConverter();
        await converter.convert(depthPath, outputPath, originalImagePath, options);
        process.exit(0);
    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
        process.exit(1);
    }
}

// Export for module use
module.exports = DepthToPLYConverter;

// Run CLI if called directly
if (require.main === module) {
    main();
}