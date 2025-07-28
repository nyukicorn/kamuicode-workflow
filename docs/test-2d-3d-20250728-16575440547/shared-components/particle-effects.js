// Particle Effects System for Three.js Viewers
// Shared component for 3D appearance, depth effects, and visual enhancements

// Initialize 3D appearance enhancement
function enhance3DAppearance(geometry) {
    const positions = geometry.attributes.position;
    const colors = geometry.attributes.color;
    const positionArray = positions.array;
    const colorArray = colors.array;
    
    // Store original colors for later depth calculations
    if (!geometry.userData) geometry.userData = {};
    geometry.userData.originalColors = new Float32Array(colorArray);
    
    // Don't apply any initial depth effects here - let dynamic updates handle it
    // This ensures depth is always calculated from current camera position
    
    colors.needsUpdate = true;
    console.log('🎆 3D appearance system initialized - dynamic depth will be applied in real-time');
}

// Update dynamic 3D effects based on camera position
function updateDynamic3DEffects(pointCloudObject, cameraObject) {
    if (!pointCloudObject || !cameraObject) return;
    
    const positions = pointCloudObject.geometry.attributes.position;
    const colors = pointCloudObject.geometry.attributes.color;
    const positionArray = positions.array;
    const colorArray = colors.array;
    const originalColors = pointCloudObject.geometry.userData.originalColors;
    
    if (!originalColors) return;
    
    const cameraPosition = cameraObject.position;
    const material = pointCloudObject.material;
    
    // Calculate proper depth range based on camera distance
    let minCameraDistance = Infinity;
    let maxCameraDistance = -Infinity;
    
    // Sample particles to find actual min/max camera distances
    for (let i = 0; i < positionArray.length; i += 60) {
        const x = positionArray[i];
        const y = positionArray[i + 1];
        const z = positionArray[i + 2];
        
        const cameraDistance = Math.sqrt(
            (x - cameraPosition.x) ** 2 + 
            (y - cameraPosition.y) ** 2 + 
            (z - cameraPosition.z) ** 2
        );
        
        minCameraDistance = Math.min(minCameraDistance, cameraDistance);
        maxCameraDistance = Math.max(maxCameraDistance, cameraDistance);
    }
    
    const depthRange = maxCameraDistance - minCameraDistance;
    
    // Apply true camera-based depth effects to every particle (improved sampling)
    for (let i = 0; i < positionArray.length; i += 30) { // Process every 10th particle
        const x = positionArray[i];
        const y = positionArray[i + 1];
        const z = positionArray[i + 2];
        
        // Calculate actual distance from camera (true 3D depth)
        const cameraDistance = Math.sqrt(
            (x - cameraPosition.x) ** 2 + 
            (y - cameraPosition.y) ** 2 + 
            (z - cameraPosition.z) ** 2
        );
        
        // Normalize distance for depth factor (0 = closest, 1 = farthest)
        const normalizedDepth = depthRange > 0 ? 
            Math.max(0, Math.min(1, (cameraDistance - minCameraDistance) / depthRange)) : 0;
        
        // Natural depth intensity (closer = brighter, farther = darker)
        const depthIntensity = 0.3 + (0.7 * (1 - normalizedDepth)); // 0.3 to 1.0 range
        
        // Apply natural color darkening (no artificial color tints)
        const colorIndex = i;
        if (colorIndex + 2 < colorArray.length) {
            colorArray[colorIndex] = originalColors[colorIndex] * depthIntensity;         // R
            colorArray[colorIndex + 1] = originalColors[colorIndex + 1] * depthIntensity; // G  
            colorArray[colorIndex + 2] = originalColors[colorIndex + 2] * depthIntensity; // B
        }
    }
    
    // Dynamic size based on average viewing distance
    const avgCameraDistance = (minCameraDistance + maxCameraDistance) / 2;
    const basepointSize = typeof pointSize !== 'undefined' ? pointSize : 1.5;
    const sizeMultiplier = Math.max(0.4, Math.min(3.0, 150 / avgCameraDistance));
    material.size = basepointSize * sizeMultiplier;
    
    // Subtle opacity for extreme depth (very conservative)
    const globalOpacity = Math.max(0.8, Math.min(1.0, 1.0 - (avgCameraDistance / (maxCameraDistance * 1.5)) * 0.2));
    material.opacity = globalOpacity;
    
    colors.needsUpdate = true;
    material.needsUpdate = true;
}

// Apply visual effects (size, brightness, color) - integrates with audio system
function applyVisualEffects(pointCloudObject, ambientLightObject, directionalLightObject) {
    if (!pointCloudObject) return;
    
    // Get current effects from audio system if available
    const effects = typeof currentEffects !== 'undefined' ? currentEffects : {
        sizeMultiplier: 1.0,
        brightnessMultiplier: 1.0,
        colorIntensity: 1.0
    };
    
    // Get base values
    const basepointSize = typeof pointSize !== 'undefined' ? pointSize : 1.5;
    const baseBrightnessLevel = typeof brightnessLevel !== 'undefined' ? brightnessLevel : 0.3;
    
    // 1. Size effect
    pointCloudObject.material.size = basepointSize * effects.sizeMultiplier;
    
    // 2. Brightness effect
    if (ambientLightObject) {
        ambientLightObject.intensity = baseBrightnessLevel * effects.brightnessMultiplier;
    }
    if (directionalLightObject) {
        directionalLightObject.intensity = baseBrightnessLevel * 1.5 * effects.brightnessMultiplier;
    }
    
    // 3. Enhanced color intensity effect with better performance
    if (pointCloudObject.geometry.attributes.color) {
        const colors = pointCloudObject.geometry.attributes.color;
        const originalColors = pointCloudObject.geometry.userData.originalColors;
        
        if (originalColors) {
            const colorArray = colors.array;
            const step = Math.max(12, Math.floor(colorArray.length / 1000)); // Adaptive step size
            
            for (let i = 0; i < colorArray.length; i += step) {
                if (i + 2 < colorArray.length) {
                    colorArray[i] = Math.min(1.0, originalColors[i] * effects.colorIntensity);
                    colorArray[i + 1] = Math.min(1.0, originalColors[i + 1] * effects.colorIntensity);
                    colorArray[i + 2] = Math.min(1.0, originalColors[i + 2] * effects.colorIntensity);
                }
            }
            colors.needsUpdate = true;
        }
    }
}

// Reset particles to original state
function resetParticleColors(pointCloudObject) {
    if (!pointCloudObject) return;
    
    // Reset colors to original enhanced state
    const colors = pointCloudObject.geometry.attributes.color;
    const originalColors = pointCloudObject.geometry.userData.originalColors;
    if (originalColors) {
        colors.array.set(originalColors);
        colors.needsUpdate = true;
    }
    
    console.log('🔄 Particle colors reset to original state');
}

// Reset all visual effects to normal state
function resetToNormalVisualState(pointCloudObject, ambientLightObject, directionalLightObject) {
    if (!pointCloudObject) return;
    
    console.log('🔄 Resetting visual effects to normal state');
    
    // Reset particle size to default
    const basepointSize = typeof pointSize !== 'undefined' ? pointSize : 1.5;
    pointCloudObject.material.size = basepointSize;
    
    // Reset lighting to default levels
    const baseBrightnessLevel = typeof brightnessLevel !== 'undefined' ? brightnessLevel : 0.3;
    if (ambientLightObject) {
        ambientLightObject.intensity = baseBrightnessLevel;
    }
    if (directionalLightObject) {
        directionalLightObject.intensity = baseBrightnessLevel * 1.5;
    }
    
    // Reset colors to original
    resetParticleColors(pointCloudObject);
    
    console.log('✅ Visual effects reset complete');
}

// Create particle system from geometry
function createParticleSystem(geometry, materialOptions = {}) {
    // Default material options
    const defaultOptions = {
        vertexColors: true,
        size: 1.5,
        sizeAttenuation: true,
        transparent: true,
        opacity: 1.0
    };
    
    const options = { ...defaultOptions, ...materialOptions };
    
    // Create point cloud material
    const material = new THREE.PointsMaterial(options);
    
    // Create point cloud
    const pointCloud = new THREE.Points(geometry, material);
    
    // Initialize 3D appearance
    enhance3DAppearance(geometry);
    
    console.log('🎆 Particle system created with', geometry.attributes.position.count, 'particles');
    
    return pointCloud;
}

// Update particle system in animation loop
function updateParticleSystem(pointCloudObject, cameraObject, ambientLightObject, directionalLightObject) {
    if (!pointCloudObject || !cameraObject) return;
    
    // Update dynamic 3D effects based on new positions
    updateDynamic3DEffects(pointCloudObject, cameraObject);
    
    // Apply visual effects if audio system is active
    if (typeof currentEffects !== 'undefined' && 
        (typeof audioReactiveEnabled === 'undefined' || audioReactiveEnabled || 
         typeof microphoneEnabled === 'undefined' || microphoneEnabled)) {
        applyVisualEffects(pointCloudObject, ambientLightObject, directionalLightObject);
    }
}

// Create panorama particle system for 360-degree images
function createPanoramaParticleSystem(imageUrl, resolution = { width: 512, height: 256 }) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        
        img.onload = function() {
            // Create canvas to read pixel data
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = resolution.width;
            canvas.height = resolution.height;
            
            // Draw and sample image
            ctx.drawImage(img, 0, 0, resolution.width, resolution.height);
            const imageData = ctx.getImageData(0, 0, resolution.width, resolution.height);
            const data = imageData.data;
            
            const particleCount = resolution.width * resolution.height;
            const positions = new Float32Array(particleCount * 3);
            const colors = new Float32Array(particleCount * 3);
            
            let particleIndex = 0;
            const radius = 100; // Sphere radius
            
            // Convert 2D image to 3D sphere using equirectangular projection (Method B)
            for (let y = 0; y < resolution.height; y++) {
                for (let x = 0; x < resolution.width; x++) {
                    const pixelIndex = (y * resolution.width + x) * 4;
                    
                    // Skip transparent pixels
                    if (data[pixelIndex + 3] < 128) continue;
                    
                    // Convert to UV coordinates (0-1)
                    const u = x / resolution.width;
                    const v = y / resolution.height;
                    
                    // Convert UV to spherical coordinates (Method B: Flat projection)
                    const phi = (u * 2 - 1) * Math.PI;      // Longitude: -π to π
                    const theta = (v - 0.5) * Math.PI;      // Latitude: -π/2 to π/2
                    
                    // Convert to 3D coordinates
                    const cosTheta = Math.cos(theta);
                    positions[particleIndex * 3] = radius * cosTheta * Math.cos(phi);     // X
                    positions[particleIndex * 3 + 1] = radius * Math.sin(theta);         // Y
                    positions[particleIndex * 3 + 2] = radius * cosTheta * Math.sin(phi); // Z
                    
                    // Set particle color from image
                    colors[particleIndex * 3] = data[pixelIndex] / 255;         // R
                    colors[particleIndex * 3 + 1] = data[pixelIndex + 1] / 255; // G
                    colors[particleIndex * 3 + 2] = data[pixelIndex + 2] / 255; // B
                    
                    particleIndex++;
                }
            }
            
            // Trim arrays to actual particle count
            const actualPositions = new Float32Array(particleIndex * 3);
            const actualColors = new Float32Array(particleIndex * 3);
            actualPositions.set(positions.subarray(0, particleIndex * 3));
            actualColors.set(colors.subarray(0, particleIndex * 3));
            
            // Create geometry
            const geometry = new THREE.BufferGeometry();
            geometry.setAttribute('position', new THREE.BufferAttribute(actualPositions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(actualColors, 3));
            geometry.computeBoundingBox();
            geometry.center();
            
            // Create particle system
            const particleSystem = createParticleSystem(geometry, {
                size: 2.0, // Slightly larger for panorama
                sizeAttenuation: true
            });
            
            console.log(`🌐 Panorama particle system created: ${particleIndex} particles from ${resolution.width}x${resolution.height} image`);
            resolve(particleSystem);
        };
        
        img.onerror = () => {
            reject(new Error('Failed to load panorama image'));
        };
        
        img.src = imageUrl;
    });
}

// Optimize particle system for performance
function optimizeParticleSystem(pointCloudObject, maxParticles = 10000) {
    if (!pointCloudObject || !pointCloudObject.geometry) return pointCloudObject;
    
    const geometry = pointCloudObject.geometry;
    const currentCount = geometry.attributes.position.count;
    
    if (currentCount <= maxParticles) {
        console.log(`🚀 Particle system already optimized: ${currentCount} particles`);
        return pointCloudObject;
    }
    
    // Calculate decimation step
    const step = Math.ceil(currentCount / maxParticles);
    const newCount = Math.floor(currentCount / step);
    
    // Decimate positions
    const oldPositions = geometry.attributes.position.array;
    const newPositions = new Float32Array(newCount * 3);
    for (let i = 0, j = 0; i < currentCount; i += step, j++) {
        newPositions[j * 3] = oldPositions[i * 3];
        newPositions[j * 3 + 1] = oldPositions[i * 3 + 1];
        newPositions[j * 3 + 2] = oldPositions[i * 3 + 2];
    }
    
    // Decimate colors if they exist
    let newColors = null;
    if (geometry.attributes.color) {
        const oldColors = geometry.attributes.color.array;
        newColors = new Float32Array(newCount * 3);
        for (let i = 0, j = 0; i < currentCount; i += step, j++) {
            newColors[j * 3] = oldColors[i * 3];
            newColors[j * 3 + 1] = oldColors[i * 3 + 1];
            newColors[j * 3 + 2] = oldColors[i * 3 + 2];
        }
    }
    
    // Create new optimized geometry
    const newGeometry = new THREE.BufferGeometry();
    newGeometry.setAttribute('position', new THREE.BufferAttribute(newPositions, 3));
    if (newColors) {
        newGeometry.setAttribute('color', new THREE.BufferAttribute(newColors, 3));
        newGeometry.userData.originalColors = new Float32Array(newColors);
    }
    
    // Replace geometry
    pointCloudObject.geometry.dispose();
    pointCloudObject.geometry = newGeometry;
    
    console.log(`🚀 Particle system optimized: ${currentCount} → ${newCount} particles (${step}x decimation)`);
    return pointCloudObject;
}

// Performance monitoring
function monitorParticlePerformance(pointCloudObject) {
    if (!pointCloudObject) return null;
    
    const particleCount = pointCloudObject.geometry.attributes.position.count;
    const memoryUsage = {
        positions: pointCloudObject.geometry.attributes.position.array.byteLength,
        colors: pointCloudObject.geometry.attributes.color ? pointCloudObject.geometry.attributes.color.array.byteLength : 0,
        total: 0
    };
    memoryUsage.total = memoryUsage.positions + memoryUsage.colors;
    
    const performance = {
        particleCount,
        memoryUsage,
        memoryMB: (memoryUsage.total / 1024 / 1024).toFixed(2),
        estimatedFPS: particleCount > 50000 ? '< 30' : particleCount > 20000 ? '30-45' : '60+'
    };
    
    return performance;
}