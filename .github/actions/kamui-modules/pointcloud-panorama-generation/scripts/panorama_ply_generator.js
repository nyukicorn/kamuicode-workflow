#!/usr/bin/env node

const fs = require('fs');
const { PNG } = require('pngjs');
const path = require('path');

class PanoramaPLYGenerator {
    constructor(options = {}) {
        this.options = {
            sphereRadius: parseFloat(options.sphereRadius) || 200,
            depthVariation: parseFloat(options.depthVariation) || 0.4,
            enablePoleCompression: options.enablePoleCompression === 'true',
            depthInversion: options.depthInversion === 'true',
            particleDensity: options.particleDensity || 'medium',
            ...options
        };
        
        console.log('🎯 PLY Generator Configuration:');
        console.log(`   Sphere radius: ${this.options.sphereRadius}`);
        console.log(`   Depth variation: ${this.options.depthVariation}`);
        console.log(`   Pole compression: ${this.options.enablePoleCompression}`);
        console.log(`   Depth inversion: ${this.options.depthInversion}`);
        console.log(`   Particle density: ${this.options.particleDensity}`);
    }
    
    async loadPNG(filePath) {
        return new Promise((resolve, reject) => {
            fs.createReadStream(filePath)
                .pipe(new PNG())
                .on('parsed', function() {
                    resolve({
                        width: this.width,
                        height: this.height,
                        data: this.data
                    });
                })
                .on('error', reject);
        });
    }
    
    getParticleCount(density) {
        const counts = {
            'low': 500000,      // 50万パーティクル（低品質でも全体を表現）
            'medium': 1500000,  // 150万パーティクル（バランス）  
            'high': 3000000     // 300万パーティクル（高密度で完全な表現）
        };
        return counts[density] || counts['medium'];
    }
    
    equirectangularToSphere(u, v, depthValue, baseRadius) {
        // Validate inputs and set safe defaults
        if (!isFinite(u) || !isFinite(v) || !isFinite(depthValue) || !isFinite(baseRadius)) {
            console.warn(`⚠️ Invalid input detected: u=${u}, v=${v}, depth=${depthValue}, radius=${baseRadius}`);
            u = Math.max(0, Math.min(1, u || 0));
            v = Math.max(0, Math.min(1, v || 0));
            depthValue = isFinite(depthValue) ? depthValue : 128;
            baseRadius = isFinite(baseRadius) ? baseRadius : 200;
        }
        
        // Convert normalized coordinates to spherical (standard equirectangular)
        const phi = u * 2 * Math.PI;           // Longitude: 0 to 2π
        const theta = v * Math.PI;             // Latitude: 0 to π
        
        // Process depth value with validation - ENHANCED to include all pixels
        let processedDepth = depthValue / 255.0; // Normalize to 0-1
        if (!isFinite(processedDepth)) {
            processedDepth = 0.5; // Safe default
        }
        
        // Accept all depth values including 0 (black areas) - treat as distant background
        if (processedDepth === 0) {
            processedDepth = 0.9; // Black areas become distant background
        } else if (processedDepth < 0.02) { // Very dark areas
            processedDepth = 0.8; // Treat as distant background
        }
        if (this.options.depthInversion) {
            processedDepth = 1.0 - processedDepth;
        }
        
        // Depth-based radius adjustment with validation
        const depthFactor = processedDepth;
        const radiusVariation = baseRadius * this.options.depthVariation;
        let adjustedRadius = baseRadius + (depthFactor - 0.5) * radiusVariation;
        
        // Ensure radius is valid
        if (!isFinite(adjustedRadius) || adjustedRadius <= 0) {
            adjustedRadius = baseRadius;
        }
        
        // DISABLED: Pole compression causes particle clustering issues
        // Instead of compressing, we'll distribute particles more evenly
        if (this.options.enablePoleCompression) {
            // Reversed logic: expand poles instead of compress for better distribution
            const poleWeight = Math.sin(theta); // 0 at poles, 1 at equator
            if (isFinite(poleWeight)) {
                const expansionFactor = 1.1 - poleWeight * 0.1; // Expand poles (1.1 at poles, 1.0 at equator)
                adjustedRadius *= expansionFactor;
            }
        }
        
        // CRITICAL FIX: Scale radius range to fit within sphere while preserving depth variation
        // Current calculation can produce values from 160 to 240, we need to scale to fit 50-190
        
        // First, normalize the current range (160-240) to (0-1)
        const originalMin = baseRadius - radiusVariation; // 160
        const originalMax = baseRadius + radiusVariation; // 240
        const normalizedDepth = (adjustedRadius - originalMin) / (originalMax - originalMin);
        
        // Then scale to desired range (50-190)
        const targetMin = 50;
        const targetMax = 190;
        adjustedRadius = targetMin + normalizedDepth * (targetMax - targetMin);
        
        // Safety clamp (should not be needed but just in case)
        adjustedRadius = Math.max(targetMin, Math.min(targetMax, adjustedRadius));
        
        // Convert to Cartesian coordinates with validation
        const sinTheta = Math.sin(theta);
        const cosTheta = Math.cos(theta);
        const cosPhi = Math.cos(phi);
        const sinPhi = Math.sin(phi);
        
        const coords = {
            x: adjustedRadius * sinTheta * cosPhi,
            y: adjustedRadius * cosTheta,
            z: adjustedRadius * sinTheta * sinPhi
        };
        
        // Final validation of coordinates
        if (!isFinite(coords.x) || !isFinite(coords.y) || !isFinite(coords.z)) {
            console.warn(`⚠️ Invalid coordinates generated, using defaults`);
            return {
                x: baseRadius * Math.sin(Math.PI * 0.5) * Math.cos(0),
                y: baseRadius * Math.cos(Math.PI * 0.5),
                z: baseRadius * Math.sin(Math.PI * 0.5) * Math.sin(0)
            };
        }
        
        return coords;
    }
    
    async convertPanoramaToSphere(depthPath, imagePath) {
        console.log('📖 Loading panorama data...');
        
        // Load depth and image data
        const depthData = await this.loadPNG(depthPath);
        const imageData = await this.loadPNG(imagePath);
        
        console.log(`📐 Image dimensions: ${imageData.width}x${imageData.height}`);
        console.log(`📐 Depth dimensions: ${depthData.width}x${depthData.height}`);
        
        const points = [];
        const { width, height } = depthData;
        
        // Determine sampling strategy based on particle density
        const targetParticleCount = this.getParticleCount(this.options.particleDensity);
        const totalPixels = width * height;
        const samplingRate = Math.min(1.0, targetParticleCount / totalPixels);
        
        console.log(`🎯 Target particles: ${targetParticleCount.toLocaleString()}`);
        console.log(`📊 Sampling rate: ${(samplingRate * 100).toFixed(1)}%`);
        
        let processedPixels = 0;
        let skippedByColor = 0;
        let skippedByTransparency = 0;
        let colorfulPixelsFound = 0;
        const startTime = Date.now();
        
        // Sample pixels based on density requirements - ENHANCED for maximum particle count
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                // For high density, use deterministic sampling instead of random for more predictable results
                if (this.options.particleDensity === 'high') {
                    // Use every pixel for high density (ignore sampling rate)
                } else {
                    // Skip pixels based on sampling rate for lower densities
                    if (Math.random() > samplingRate) continue;
                }
                
                // Get normalized coordinates (0-1)
                const u = x / width;
                const v = y / height;
                
                // Get depth value (use red channel for grayscale)
                const depthIdx = (y * width + x) * 4;
                const depthValue = depthData.data[depthIdx];
                
                // Skip only completely black areas (but allow sky/light areas)
                // Note: Removed this condition to include more particles
                // if (depthValue < 1) continue;
                
                // Convert to spherical coordinates with depth
                const spherePos = this.equirectangularToSphere(
                    u, v, depthValue, this.options.sphereRadius
                );
                
                // Get color from original image (handle different resolutions)
                const imageX = Math.floor(u * imageData.width);
                const imageY = Math.floor(v * imageData.height);
                const colorIdx = (imageY * imageData.width + imageX) * 4;
                
                const r = imageData.data[colorIdx] || 128;
                const g = imageData.data[colorIdx + 1] || 128;
                const b = imageData.data[colorIdx + 2] || 128;
                const a = imageData.data[colorIdx + 3] || 255;
                
                // ULTIMATE: Include ALL areas as particles - no transparency filtering
                // Skip only completely invisible pixels (a = 0), keep everything else including semi-transparent
                if (a < 1) {
                    skippedByTransparency++;
                    continue; // MAXIMUM inclusivity - only skip completely invisible pixels
                }
                
                // COLOR-BASED SAMPLING: Force particle creation for colored areas regardless of depth
                // This ensures sky, aurora, and other colored but depth-less areas get particles
                const colorSum = r + g + b;
                const hasSignificantColor = colorSum > 50; // Any visible color (raised threshold)
                
                // Debug sky area (top 30% of image) - ENHANCED debugging
                if (v < 0.3) {
                    if (hasSignificantColor) {
                        colorfulPixelsFound++;
                    }
                    // Sample logging for first few sky pixels
                    if (colorfulPixelsFound < 10) {
                        console.log(`🌌 Sky pixel [${x},${y}] (${(v*100).toFixed(1)}%): RGB(${r},${g},${b})=${colorSum} depth=${depthValue} hasColor=${hasSignificantColor}`);
                    }
                }
                
                // CRITICAL FIX: If there's color, ALWAYS create particle regardless of depth
                // This is especially important for sky, aurora, and gradient areas
                if (hasSignificantColor) {
                    // Has color = force particle creation
                    // Continue to particle creation
                } else if (depthValue < 5) {
                    // No color AND no depth = skip
                    skippedByColor++;
                    continue;
                }
                
                // ENHANCED: For dark areas (space/sky/background), create beautiful star field
                let finalR = r, finalG = g, finalB = b;
                
                // Calculate darkness level (0 = pure black, 1 = bright)
                const brightness = (r + g + b) / (3 * 255);
                const isDark = brightness < 0.15; // Much more inclusive threshold (was pure black only)
                
                if (isDark) {
                    // Create varied space effects based on darkness level
                    const starChance = Math.random();
                    const spaceDepth = 1 - brightness; // Darker = deeper space
                    
                    if (starChance < 0.02) {
                        // 2% chance: Bright stars
                        finalR = 200 + Math.random() * 55;
                        finalG = 200 + Math.random() * 55;
                        finalB = 180 + Math.random() * 75;
                    } else if (starChance < 0.05) {
                        // 3% chance: Medium stars  
                        finalR = 120 + Math.random() * 80;
                        finalG = 120 + Math.random() * 80;
                        finalB = 140 + Math.random() * 80;
                    } else if (starChance < 0.15) {
                        // 10% chance: Dim stars
                        finalR = 40 + Math.random() * 40;
                        finalG = 40 + Math.random() * 40;
                        finalB = 60 + Math.random() * 60;
                    } else {
                        // Rest: Deep space gradient with subtle nebula colors
                        const nebulaEffect = Math.random() * spaceDepth;
                        finalR = Math.max(r, Math.floor(8 + nebulaEffect * 15));   // Subtle red nebula
                        finalG = Math.max(g, Math.floor(12 + nebulaEffect * 20));  // Space blue-green
                        finalB = Math.max(b, Math.floor(25 + nebulaEffect * 40)); // Deep space blue
                    }
                } else {
                    // ENHANCE: Boost colors for natural areas (ocean, forests) for better visibility
                    if (g > r && g > b && g > 30) {
                        // Green areas (forests) - enhance green
                        finalG = Math.min(255, g * 1.3);
                        finalR = Math.max(r, 20);
                        finalB = Math.max(b, 15);
                    } else if (b > r && b > g && b > 20) {
                        // Blue areas (oceans) - enhance blue
                        finalB = Math.min(255, b * 1.4);
                        finalR = Math.max(r, 10);
                        finalG = Math.max(g, 25);
                    }
                }
                
                points.push({
                    x: spherePos.x,
                    y: spherePos.y,
                    z: spherePos.z,
                    r: finalR,
                    g: finalG,
                    b: finalB
                });
                
                processedPixels++;
            }
            
            // Progress update every 10%
            if (y % Math.floor(height / 10) === 0) {
                const progress = (y / height * 100).toFixed(0);
                console.log(`📊 Processing: ${progress}% (${points.length.toLocaleString()} particles)`);
            }
        }
        
        const processingTime = (Date.now() - startTime) / 1000;
        console.log(`✅ Sphere conversion completed in ${processingTime.toFixed(2)}s`);
        console.log(`🎯 Generated ${points.length.toLocaleString()} particles`);
        console.log(`📊 Debug: Skipped by transparency: ${skippedByTransparency}, by color: ${skippedByColor}`);
        console.log(`🌌 Sky area: Found ${colorfulPixelsFound} colorful pixels in top 30%`);
        
        return points;
    }
    
    generatePLYContent(points) {
        console.log('📝 Generating PLY file content...');
        
        let plyContent = '';
        
        // PLY header
        plyContent += 'ply\n';
        plyContent += 'format ascii 1.0\n';
        plyContent += `element vertex ${points.length}\n`;
        plyContent += 'property float x\n';
        plyContent += 'property float y\n';
        plyContent += 'property float z\n';
        plyContent += 'property uchar red\n';
        plyContent += 'property uchar green\n';
        plyContent += 'property uchar blue\n';
        plyContent += 'end_header\n';
        
        // Vertex data
        for (const point of points) {
            plyContent += `${point.x.toFixed(6)} ${point.y.toFixed(6)} ${point.z.toFixed(6)} ${point.r} ${point.g} ${point.b}\n`;
        }
        
        return plyContent;
    }
    
    async savePLY(points, outputPath) {
        const plyContent = this.generatePLYContent(points);
        
        return new Promise((resolve, reject) => {
            fs.writeFile(outputPath, plyContent, (err) => {
                if (err) reject(err);
                else {
                    console.log(`💾 PLY file saved: ${outputPath}`);
                    console.log(`📊 File size: ${(plyContent.length / 1024 / 1024).toFixed(2)} MB`);
                    resolve(outputPath);
                }
            });
        });
    }
}

async function main() {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.error('Usage: node panorama_ply_generator.js <depth_image> <panorama_image> [options...]');
        process.exit(1);
    }
    
    const [depthPath, imagePath, ...optionArgs] = args;
    
    // Parse options
    const options = {};
    for (let i = 0; i < optionArgs.length; i += 2) {
        const key = optionArgs[i].replace('--', '');
        const value = optionArgs[i + 1];
        options[key] = value;
    }
    
    console.log('🌐 Starting Panorama PLY Generation...');
    console.log(`   Depth image: ${depthPath}`);
    console.log(`   Panorama image: ${imagePath}`);
    
    try {
        const generator = new PanoramaPLYGenerator(options);
        
        // Convert panorama to sphere
        const points = await generator.convertPanoramaToSphere(depthPath, imagePath);
        
        // Generate output path
        const baseName = path.basename(imagePath, path.extname(imagePath));
        const outputPath = path.join(options.outputDir || '.', `${baseName}_panorama_sphere.ply`);
        
        // Save PLY file
        await generator.savePLY(points, outputPath);
        
        // Output results for GitHub Actions with debugging
        console.log(`📤 Output path: ${outputPath}`);
        console.log(`📤 GITHUB_OUTPUT env: ${process.env.GITHUB_OUTPUT || 'NOT SET'}`);
        
        if (process.env.GITHUB_OUTPUT) {
            fs.appendFileSync(process.env.GITHUB_OUTPUT, `panorama_ply_path=${outputPath}\n`);
            fs.appendFileSync(process.env.GITHUB_OUTPUT, `particle_count=${points.length}\n`);
            fs.appendFileSync(process.env.GITHUB_OUTPUT, `sphere_radius=${generator.options.sphereRadius}\n`);
            
            const sphereInfo = {
                radius: generator.options.sphereRadius,
                depthVariation: generator.options.depthVariation,
                particleCount: points.length,
                poleCompression: generator.options.enablePoleCompression,
                depthInversion: generator.options.depthInversion
            };
            
            fs.appendFileSync(process.env.GITHUB_OUTPUT, `sphere_info=${JSON.stringify(sphereInfo)}\n`);
            console.log('✅ Output values written to GITHUB_OUTPUT');
        } else {
            console.error('⚠️ WARNING: GITHUB_OUTPUT environment variable not set');
        }
        
        console.log('✅ Panorama PLY generation completed successfully!');
        
    } catch (error) {
        console.error('❌ Error during PLY generation:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { PanoramaPLYGenerator };