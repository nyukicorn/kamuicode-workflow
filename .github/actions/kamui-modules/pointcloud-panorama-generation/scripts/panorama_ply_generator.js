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
            'low': 25000,      // 360度パノラマ用に増加
            'medium': 50000,   // 360度パノラマ用に増加
            'high': 100000     // 360度パノラマ用に大幅増加
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
        
        // Convert normalized coordinates to spherical
        const phi = u * 2 * Math.PI;           // Longitude: 0 to 2π
        const theta = v * Math.PI;             // Latitude: 0 to π
        
        // Process depth value with validation
        let processedDepth = depthValue / 255.0; // Normalize to 0-1
        if (!isFinite(processedDepth)) {
            processedDepth = 0.5; // Safe default
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
        
        // Pole compression to reduce distortion
        if (this.options.enablePoleCompression) {
            const poleWeight = Math.sin(theta); // 0 at poles, 1 at equator
            if (isFinite(poleWeight)) {
                const compressionFactor = 0.9 + poleWeight * 0.1;
                adjustedRadius *= compressionFactor;
            }
        }
        
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
        const startTime = Date.now();
        
        // Sample pixels based on density requirements
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                // Skip pixels based on sampling rate
                if (Math.random() > samplingRate) continue;
                
                // Get normalized coordinates (0-1)
                const u = x / width;
                const v = y / height;
                
                // Get depth value (use red channel for grayscale)
                const depthIdx = (y * width + x) * 4;
                const depthValue = depthData.data[depthIdx];
                
                // Skip very dark/transparent areas
                if (depthValue < 5) continue;
                
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
                
                // Skip transparent pixels
                if (a < 128) continue;
                
                points.push({
                    x: spherePos.x,
                    y: spherePos.y,
                    z: spherePos.z,
                    r: r,
                    g: g,
                    b: b
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