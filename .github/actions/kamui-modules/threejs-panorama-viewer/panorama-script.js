// 360° Panorama Viewer - Depth-Enhanced Spherical Particle Distribution
// Uses shared components for camera, UI, audio, and mouse interaction
// Implements PLY loading with depth information from pointcloud-panorama-generation

// Global variables (panorama specific) - DUAL SPHERE ARCHITECTURE
let innerSphereParticles = null; // Deep PLY pointcloud (radius ~200)
let outerSphereParticles = null; // Panorama image pointcloud (radius ~400)
let panoramaTexture = null;
let lights = null;
let innerSphereRadius = 100; // Much smaller for outer sphere focus
let outerSphereRadius = 600; // Large outer sphere for main experience

// Use shared audio variables from audio-reactive-system.js
// These variables are already declared in the shared component

// Panorama-specific effect intensities
let panoramaEffects = {
    sizeMultiplier: 1.0,
    brightnessMultiplier: 1.0,
    colorIntensity: 1.0,
    movementIntensity: 0.0
};

// Panorama configuration - 360度パノラマ用に最適化 - NANO-SCALE for true art
let particleSize = 0.08; // NANO particles (0.15→0.08) for ultra-fine pointcloud art
// autoRotate is already declared in camera-controls.js, just set the value
autoRotate = AUTO_ROTATE_PLACEHOLDER;
// rotationSpeed is already declared in camera-controls.js, just set the value
rotationSpeed = ROTATION_SPEED_PLACEHOLDER;
let particleDensity = 'PARTICLE_DENSITY_PLACEHOLDER'; // low/medium/high
let enableDepthVisualization = ENABLE_DEPTH_PLACEHOLDER;
let plyFilePath = 'PLY_FILE_PATH_PLACEHOLDER';

// Initialize the panorama viewer with shared components
function init() {
    console.log('🌐 Initializing Depth-Enhanced 360° Panorama Viewer');
    
    // Initialize camera system
    const containerElement = document.getElementById('container');
    const cameraData = initializeCameraSystem(containerElement, 'BACKGROUND_COLOR_PLACEHOLDER');
    
    // Store global references from camera system
    scene = cameraData.scene;
    camera = cameraData.camera;
    renderer = cameraData.renderer;
    controls = cameraData.controls;
    
    // Set initial camera position (inside the sphere) - 360度パノラマ用に最適化
    const initialRadius = CAM_RADIUS_PLACEHOLDER;
    setCameraPosition(0, 0, 0); // Center of the sphere
    
    // 二重球体用の初期カメラ位置
    const optimalViewingDistance = innerSphereRadius * 0.3; // 内側球体半径の30%の位置
    
    // Configure controls for dual sphere exploration - UNLIMITED MOVEMENT
    controls.enablePan = true;  // Enable panning for full 3D exploration
    controls.minDistance = 1;   // Very close inspection
    controls.maxDistance = outerSphereRadius * 2; // Allow far outside view (1200 units)
    
    // 360度パノラマ用の初期カメラ位置を最適化
    camera.position.set(0, 0, optimalViewingDistance);
    controls.update();
    
    // Set auto-rotate settings
    setAutoRotateSettings(autoRotate, rotationSpeed);
    
    // Initialize UI system with lighting
    lights = initializeCompleteUISystem(scene, 'BACKGROUND_COLOR_PLACEHOLDER');
    
    // Initialize audio if available
    if (typeof setupMusic === 'function') {
        try {
            setupMusic();
            console.log('🎵 Music system initialized');
        } catch (error) {
            console.warn('🎵 Music system initialization failed:', error);
        }
    } else {
        console.log('🎵 Music system not found, initializing basic audio support...');
        initializeBasicAudioSystem();
    }
    
    // Load panorama PLY file with depth information
    loadPanoramaPLY();
    
    console.log('OrbitControls configured for panoramic viewing');
    console.log('Camera positioned at center, looking outward');
    
    // Start animation loop
    animate();
    
    console.log('✅ Depth-Enhanced 360° Panorama Viewer initialization complete');
}

function loadPanoramaPLY() {
    showLoadingIndicator('🖼️ Loading depth-enhanced panorama PLY...');
    
    const loader = new THREE.PLYLoader();
    
    // Load PLY file from pointcloud-panorama-generation output
    loader.load(plyFilePath,
        function(geometry) {
            console.log('✅ Panorama PLY loaded successfully');
            console.log(`   Vertices: ${geometry.attributes.position.count.toLocaleString()}`);
            
            // Create particle system from PLY data
            createDepthEnhancedParticleSystem(geometry);
        },
        function(progress) {
            if (progress.total > 0) {
                const percent = Math.round((progress.loaded / progress.total) * 100);
                updateLoadingProgress(`Loading PLY: ${percent}%`);
            } else {
                updateLoadingProgress(`Loading PLY: ${(progress.loaded / 1024 / 1024).toFixed(1)} MB`);
            }
        },
        function(error) {
            console.error('❌ Error loading panorama PLY:', error);
            showLoadingIndicator('❌ Failed to load panorama PLY');
            
            // Fallback to image-based loading if PLY fails
            console.log('🔄 Falling back to image-based panorama loading...');
            loadPanoramaImageFallback();
        }
    );
}

function createDepthEnhancedParticleSystem(geometry) {
    console.log('🌐 Creating depth-enhanced spherical particle system...');
    
    // Verify geometry has required attributes
    if (!geometry.attributes.position) {
        console.error('❌ PLY file missing position data');
        return;
    }
    
    // Extract position and color data
    const positions = geometry.attributes.position;
    const colors = geometry.attributes.color;
    
    // Calculate bounding sphere for inner sphere (PLY data) but force smaller radius
    geometry.computeBoundingSphere();
    const originalRadius = geometry.boundingSphere ? geometry.boundingSphere.radius : 200;
    innerSphereRadius = 100; // FORCE smaller inner sphere for outer sphere focus
    console.log(`📏 Original PLY radius: ${originalRadius}, Forced inner radius: ${innerSphereRadius}`);
    
    // SCALE inner sphere particles to desired radius
    if (originalRadius > 0) {
        const scaleFactor = innerSphereRadius / originalRadius;
        const positionArray = positions.array;
        for (let i = 0; i < positionArray.length; i += 3) {
            positionArray[i] *= scaleFactor;     // x
            positionArray[i + 1] *= scaleFactor; // y  
            positionArray[i + 2] *= scaleFactor; // z
        }
        positions.needsUpdate = true;
        console.log(`🔧 Scaled inner sphere particles by factor: ${scaleFactor.toFixed(3)}`);
    }
    
    // FORCE particle count reduction for audio performance - MICROSCOPIC PARTICLES
    const currentParticleCount = positions.array.length / 3;
    const maxAudioFriendlyParticles = 200000; // 20万が音楽連動の限界（マイクロ粒子対応）
    
    if (currentParticleCount > maxAudioFriendlyParticles) {
        const reductionFactor = maxAudioFriendlyParticles / currentParticleCount;
        const step = Math.ceil(1 / reductionFactor);
        
        const newPositions = [];
        const newColors = [];
        const positionArray = positions.array;
        const colorArray = colors.array;
        
        for (let i = 0; i < positionArray.length; i += step * 3) {
            newPositions.push(positionArray[i], positionArray[i + 1], positionArray[i + 2]);
            newColors.push(colorArray[i], colorArray[i + 1], colorArray[i + 2]);
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(newPositions), 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(newColors), 3));
        
        console.log(`🚀 Particle decimation: ${currentParticleCount.toLocaleString()} -> ${(newPositions.length/3).toLocaleString()} (${(reductionFactor*100).toFixed(1)}%)`);
    }
    
    // ANTI-GRID: Add random scatter to eliminate grid-like arrangement
    const finalPositions = geometry.attributes.position.array;
    const scatterStrength = innerSphereRadius * 0.02; // 2% scatter for natural distribution
    
    for (let i = 0; i < finalPositions.length; i += 3) {
        // Add small random offset to break grid patterns
        finalPositions[i] += (Math.random() - 0.5) * scatterStrength;     // x
        finalPositions[i + 1] += (Math.random() - 0.5) * scatterStrength; // y  
        finalPositions[i + 2] += (Math.random() - 0.5) * scatterStrength; // z
    }
    
    geometry.attributes.position.needsUpdate = true;
    console.log(`🎲 Applied random scatter (${scatterStrength.toFixed(2)} units) to eliminate grid patterns`);
    
    // Camera constraints already set for dual sphere exploration
    
    // DUAL SPHERE: Create outer sphere from panorama image as pointcloud
    const imagePath = 'assets/panorama-image.png';
    const loader = new THREE.TextureLoader();
    loader.load(imagePath, 
        function(texture) {
            console.log('🌐 Creating outer sphere pointcloud from panorama image...');
            createOuterSpherePointcloud(texture);
        },
        undefined,
        function(error) {
            console.log('📝 Panorama image not found, creating outer sphere from fallback pattern');
            createOuterSphereFallback();
        }
    );
    
    // Add depth visualization if enabled
    if (enableDepthVisualization && colors) {
        enhanceDepthVisualization(positions, colors);
    }
    
    // Create inner sphere particle system - 内側球体（深度情報付き）- MUCH SMALLER PARTICLES
    innerSphereParticles = createParticleSystem(geometry, {
        size: particleSize * 0.4,  // Much smaller particles for finer detail (0.8x2.0=1.6 -> 0.4x2.0=0.8)
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.95,
        vertexColors: true,
        blending: THREE.AdditiveBlending
    });
    
    scene.add(innerSphereParticles);
    
    // Initialize mouse interaction with inner sphere
    initializeMouseInteraction(innerSphereParticles, camera);
    
    // Update UI with statistics
    updateStatsDisplay(innerSphereParticles);
    hideLoadingIndicator();
    
    console.log(`✅ Inner sphere created: ${positions.count.toLocaleString()} particles`);
    console.log(`Inner sphere radius: ${innerSphereRadius}`);
}

function enhanceDepthVisualization(positions, colors) {
    console.log('🎨 Enhancing depth visualization...');
    
    const posArray = positions.array;
    const colorArray = colors.array;
    const particleCount = positions.count;
    
    // Calculate depth range
    let minRadius = Infinity;
    let maxRadius = -Infinity;
    
    for (let i = 0; i < particleCount; i++) {
        const x = posArray[i * 3];
        const y = posArray[i * 3 + 1];
        const z = posArray[i * 3 + 2];
        const radius = Math.sqrt(x * x + y * y + z * z);
        
        minRadius = Math.min(minRadius, radius);
        maxRadius = Math.max(maxRadius, radius);
    }
    
    const depthRange = maxRadius - minRadius;
    console.log(`📊 Depth range: ${minRadius.toFixed(2)} to ${maxRadius.toFixed(2)} (range: ${depthRange.toFixed(2)})`);
    
    // Apply depth-based color enhancement
    for (let i = 0; i < particleCount; i++) {
        const x = posArray[i * 3];
        const y = posArray[i * 3 + 1];
        const z = posArray[i * 3 + 2];
        const radius = Math.sqrt(x * x + y * y + z * z);
        
        // Calculate normalized depth (0 = closest, 1 = farthest)
        const normalizedDepth = (radius - minRadius) / depthRange;
        
        // Enhance colors based on depth
        const depthFactor = 1.0 + normalizedDepth * 0.5; // Brighten distant particles
        
        colorArray[i * 3] = Math.min(1.0, colorArray[i * 3] * depthFactor);
        colorArray[i * 3 + 1] = Math.min(1.0, colorArray[i * 3 + 1] * depthFactor);
        colorArray[i * 3 + 2] = Math.min(1.0, colorArray[i * 3 + 2] * depthFactor);
    }
    
    colors.needsUpdate = true;
}

function loadPanoramaImageFallback() {
    console.log('🖼️ Loading panorama image as fallback...');
    
    const loader = new THREE.TextureLoader();
    
    // Multiple path attempts for GitHub Pages compatibility
    const possiblePaths = [
        'assets/panorama-image.png',  // Direct relative path
        './assets/panorama-image.png', // Explicit relative path
        window.location.pathname.replace(/\/[^\/]*$/, '/') + 'assets/panorama-image.png', // Dynamic base URL
        // GitHub Pages absolute path construction
        window.location.origin + window.location.pathname.replace(/\/[^\/]*$/, '/') + 'assets/panorama-image.png'
    ];
    
    console.log('🔍 Attempting to load image from multiple paths...');
    possiblePaths.forEach((path, index) => {
        console.log(`   Path ${index + 1}: ${path}`);
    });
    
    // Try loading from each path sequentially
    tryLoadFromPaths(loader, possiblePaths, 0);
}

function tryLoadFromPaths(loader, paths, index) {
    if (index >= paths.length) {
        console.error('❌ All image paths failed, creating test pattern');
        createTestSphericalPattern();
        return;
    }
    
    const currentPath = paths[index];
    console.log(`🔍 Trying path ${index + 1}/${paths.length}: ${currentPath}`);
    
    // Pre-check image existence with fetch to avoid CORS issues
    checkImageExistence(currentPath)
        .then(exists => {
            if (exists) {
                console.log(`✅ Image confirmed to exist at path ${index + 1}`);
                loadImageFromPath(loader, currentPath, index, paths);
            } else {
                console.warn(`⚠️ Image not found at path ${index + 1}, trying next...`);
                tryLoadFromPaths(loader, paths, index + 1);
            }
        })
        .catch(error => {
            console.warn(`⚠️ Error checking path ${index + 1}: ${error.message}`);
            // Still try to load in case it's a false negative
            loadImageFromPath(loader, currentPath, index, paths);
        });
}

function checkImageExistence(imagePath) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = imagePath;
        
        // Timeout after 3 seconds
        setTimeout(() => resolve(false), 3000);
    });
}

function loadImageFromPath(loader, currentPath, pathIndex, allPaths) {
    loader.load(currentPath,
        function(texture) {
            console.log(`✅ Panorama texture loaded from path ${pathIndex + 1}: ${currentPath}`);
            panoramaTexture = texture;
            
            // Create background panorama sphere
            createBackgroundPanoramaSphere(texture);
            
            // Create spherical particle distribution from image  
            createSphericalParticleSystemFromImage();
        },
        function(progress) {
            const percent = Math.round((progress.loaded / progress.total) * 100);
            updateLoadingProgress(`Loading panorama: ${percent}%`);
        },
        function(error) {
            console.warn(`⚠️ THREE.js TextureLoader failed for path ${pathIndex + 1}: ${error.message || error}`);
            // Try next path
            tryLoadFromPaths(loader, allPaths, pathIndex + 1);
        }
    );
}

function createSphericalParticleSystemFromImage() {
    console.log('🌐 Creating spherical particle system from image (fallback mode)...');
    
    // Determine particle count based on density setting - 高密度で全体を表現
    let particleCount;
    switch(particleDensity) {
        case 'low': particleCount = 200000; break;     // 20万パーティクル（軽量）
        case 'high': particleCount = 400000; break;   // 40万パーティクル（音楽連動対応）
        default: particleCount = 300000; // medium     // 30万パーティクル（バランス）
    }
    
    showLoadingIndicator(`🌐 Generating ${particleCount.toLocaleString()} particles...`);
    
    // Create canvas to analyze image pixels
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = panoramaTexture.image;
    
    // Set canvas size for analysis (balance between detail and performance)
    const analysisWidth = 512;
    const analysisHeight = 256;
    canvas.width = analysisWidth;
    canvas.height = analysisHeight;
    
    // Draw image to canvas for pixel analysis
    ctx.drawImage(img, 0, 0, analysisWidth, analysisHeight);
    const imageData = ctx.getImageData(0, 0, analysisWidth, analysisHeight);
    const pixels = imageData.data;
    
    // Create geometry for spherical particles
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    
    let particleIndex = 0;
    
    // Generate particles using spherical coordinates with simulated depth
    for (let i = 0; i < particleCount && particleIndex < particleCount; i++) {
        // Generate uniform distribution on sphere
        const u = Math.random();
        const v = Math.random();
        
        // Convert to spherical coordinates (phi: 0 to 2π, theta: 0 to π)
        const phi = u * 2 * Math.PI;          // Longitude (0 to 2π)
        const theta = Math.acos(2 * v - 1);   // Latitude (0 to π) - uniform distribution
        
        // Map spherical coordinates to image coordinates
        const imageX = Math.floor((phi / (2 * Math.PI)) * analysisWidth);
        const imageY = Math.floor((theta / Math.PI) * analysisHeight);
        
        // Get pixel color from image
        const pixelIndex = (imageY * analysisWidth + imageX) * 4;
        const r = pixels[pixelIndex] / 255;
        const g = pixels[pixelIndex + 1] / 255;
        const b = pixels[pixelIndex + 2] / 255;
        const alpha = pixels[pixelIndex + 3] / 255;
        
        // Skip nearly transparent pixels
        if (alpha < 0.1) continue;
        
        // Simulate depth based on brightness
        const brightness = (r + g + b) / 3;
        const depthVariation = 0.2; // 20% depth variation
        const radiusMultiplier = 1.0 + (brightness - 0.5) * depthVariation;
        const adjustedRadius = innerSphereRadius * radiusMultiplier;
        
        // Convert spherical to Cartesian coordinates with simulated depth
        const x = adjustedRadius * Math.sin(theta) * Math.cos(phi);
        const y = adjustedRadius * Math.cos(theta);
        const z = adjustedRadius * Math.sin(theta) * Math.sin(phi);
        
        // Store position
        positions[particleIndex * 3] = x;
        positions[particleIndex * 3 + 1] = y;
        positions[particleIndex * 3 + 2] = z;
        
        // Store color with brightness enhancement
        const enhancementFactor = 1.2 + brightness * 0.5;
        colors[particleIndex * 3] = Math.min(1.0, r * enhancementFactor);
        colors[particleIndex * 3 + 1] = Math.min(1.0, g * enhancementFactor);
        colors[particleIndex * 3 + 2] = Math.min(1.0, b * enhancementFactor);
        
        particleIndex++;
    }
    
    // Adjust arrays to actual particle count
    const actualPositions = new Float32Array(particleIndex * 3);
    const actualColors = new Float32Array(particleIndex * 3);
    
    for (let i = 0; i < particleIndex * 3; i++) {
        actualPositions[i] = positions[i];
        actualColors[i] = colors[i];
    }
    
    // Create Three.js geometry
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(actualPositions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(actualColors, 3));
    geometry.computeBoundingSphere();
    
    // Create inner sphere particle system for fallback
    innerSphereParticles = createParticleSystem(geometry, {
        size: particleSize,
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.9,
        vertexColors: true
    });
    
    scene.add(innerSphereParticles);
    
    // Initialize mouse interaction with inner sphere
    initializeMouseInteraction(innerSphereParticles, camera);
    
    // Update UI
    updateStatsDisplay(innerSphereParticles);
    hideLoadingIndicator();
    
    console.log(`✅ Spherical panorama created: ${particleIndex.toLocaleString()} particles`);
    console.log(`Inner sphere radius: ${innerSphereRadius}, Camera at center`);
}

function createTestSphericalPattern() {
    console.log('🧪 Creating test spherical pattern...');
    
    const particleCount = 20000;
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    
    // Create test pattern with depth variation
    for (let i = 0; i < particleCount; i++) {
        // Uniform distribution on sphere
        const u = Math.random();
        const v = Math.random();
        
        const phi = u * 2 * Math.PI;
        const theta = Math.acos(2 * v - 1);
        
        // Add depth variation based on latitude bands
        const latitudeBand = Math.floor((theta / Math.PI) * 6);
        const depthVariation = 0.3;
        const radiusMultiplier = 1.0 + (Math.sin(latitudeBand * Math.PI / 6) - 0.5) * depthVariation;
        const adjustedRadius = innerSphereRadius * radiusMultiplier;
        
        const x = adjustedRadius * Math.sin(theta) * Math.cos(phi);
        const y = adjustedRadius * Math.cos(theta);
        const z = adjustedRadius * Math.sin(theta) * Math.sin(phi);
        
        positions[i * 3] = x;
        positions[i * 3 + 1] = y;
        positions[i * 3 + 2] = z;
        
        // Create colored bands based on latitude with depth enhancement
        const depthColor = radiusMultiplier;
        switch(latitudeBand) {
            case 0: // Top
                colors[i * 3] = 1.0 * depthColor; 
                colors[i * 3 + 1] = 0.3 * depthColor; 
                colors[i * 3 + 2] = 0.3 * depthColor;
                break;
            case 1:
                colors[i * 3] = 1.0 * depthColor; 
                colors[i * 3 + 1] = 0.7 * depthColor; 
                colors[i * 3 + 2] = 0.3 * depthColor;
                break;
            case 2:
                colors[i * 3] = 0.3 * depthColor; 
                colors[i * 3 + 1] = 1.0 * depthColor; 
                colors[i * 3 + 2] = 0.3 * depthColor;
                break;
            case 3:
                colors[i * 3] = 0.3 * depthColor; 
                colors[i * 3 + 1] = 0.7 * depthColor; 
                colors[i * 3 + 2] = 1.0 * depthColor;
                break;
            case 4:
                colors[i * 3] = 0.7 * depthColor; 
                colors[i * 3 + 1] = 0.3 * depthColor; 
                colors[i * 3 + 2] = 1.0 * depthColor;
                break;
            default: // Bottom
                colors[i * 3] = 1.0 * depthColor; 
                colors[i * 3 + 1] = 0.3 * depthColor; 
                colors[i * 3 + 2] = 0.7 * depthColor;
                break;
        }
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.computeBoundingSphere();
    
    innerSphereParticles = createParticleSystem(geometry, {
        size: particleSize,
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.9,
        vertexColors: true
    });
    
    scene.add(innerSphereParticles);
    initializeMouseInteraction(innerSphereParticles, camera);
    updateStatsDisplay(innerSphereParticles);
    hideLoadingIndicator();
    
    console.log('✅ Test spherical pattern with depth variation created');
}

// Audio reactive effects run at full 60fps for maximum immersion

function animate() {
    requestAnimationFrame(animate);
    
    // Update camera controls (shared component)
    updateCameraControls();
    
    // Apply mouse gravity effect to both spheres
    if (innerSphereParticles) {
        applyMouseGravity(innerSphereParticles);
    }
    if (outerSphereParticles) {
        applyMouseGravity(outerSphereParticles);
    }
    
    // Apply audio-reactive effects to both spheres - 60fps for maximum immersion
    if ((audioReactiveEnabled || microphoneEnabled) && (innerSphereParticles || outerSphereParticles)) {
        applyAudioReactiveEffects();
        // Apply frequency-based color mixing
        applyFrequencyColorMixing();
    }
    
    // Update particle system effects for both spheres
    if (innerSphereParticles) {
        updateParticleSystem(innerSphereParticles, camera, lights.ambientLight, lights.directionalLight);
    }
    if (outerSphereParticles) {
        updateParticleSystem(outerSphereParticles, camera, lights.ambientLight, lights.directionalLight);
    }
    
    // Render scene (shared component)
    renderScene();
}

// Panorama-specific control functions that integrate with shared components
function resetCamera() {
    // Reset to center of sphere
    setCameraPosition(0, 0, 0);
    controls.target.set(0, 0, 0);
    controls.update();
    console.log('📷 Camera reset to panorama center');
}

function updateParticleSize(value) {
    particleSize = parseFloat(value);
    
    // Update inner sphere
    if (innerSphereParticles && innerSphereParticles.material) {
        const currentMultiplier = audioReactiveEnabled ? panoramaEffects.sizeMultiplier : 1.0;
        const effectiveSize = particleSize * currentMultiplier;
        
        // ADAPTIVE: Adjust multiplier based on particle count for optimal visibility
        const particleCount = innerSphereParticles.geometry.attributes.position.count;
        const adaptiveMultiplier = Math.max(2, 8 - (particleCount / 500000));
        
        const finalSize = Math.max(0.5, effectiveSize * adaptiveMultiplier * 0.4); // Much smaller for finer detail
        innerSphereParticles.material.size = finalSize;
        innerSphereParticles.material.needsUpdate = true;
        
        console.log(`📏 Inner sphere size: ${particleCount.toLocaleString()} particles → ${finalSize.toFixed(2)}`);
    }
    
    // Update outer sphere
    if (outerSphereParticles && outerSphereParticles.material) {
        const currentMultiplier = audioReactiveEnabled ? panoramaEffects.sizeMultiplier : 1.0;
        const effectiveSize = particleSize * currentMultiplier;
        
        const particleCount = outerSphereParticles.geometry.attributes.position.count;
        const adaptiveMultiplier = Math.max(2, 8 - (particleCount / 500000));
        
        const finalSize = Math.max(0.5, effectiveSize * adaptiveMultiplier * 0.6); // Smaller for finer detail
        outerSphereParticles.material.size = finalSize;
        outerSphereParticles.material.needsUpdate = true;
        
        console.log(`📏 Outer sphere size: ${particleCount.toLocaleString()} particles → ${finalSize.toFixed(2)}`);
    }
    
    // Force render update
    if (typeof renderer !== 'undefined') {
        renderer.render(scene, camera);
    }
}

function toggleBrightness() {
    window.toggleBrightness(scene, lights.ambientLight, lights.directionalLight, 'BACKGROUND_COLOR_PLACEHOLDER');
}

function updateGlowIntensity(value) {
    const glowValue = parseFloat(value) / 100; // Convert 0-200 to 0-2 (now supports 200% glow)
    
    // Update glow for both spheres
    [innerSphereParticles, outerSphereParticles].forEach((sphere, index) => {
        if (!sphere || !sphere.material) return;
        // Create emissive-like effect by adjusting material properties
        sphere.material.opacity = Math.min(1.0, 0.6 + glowValue * 0.4);
        sphere.material.blending = glowValue > 0.1 ? THREE.AdditiveBlending : THREE.NormalBlending;
        
        // Scale particles for glow effect
        const baseSize = particleSize;
        const currentMultiplier = audioReactiveEnabled ? panoramaEffects.sizeMultiplier : 1.0;
        const glowSizeMultiplier = 1.0 + glowValue * 0.8;
        const particleCount = sphere.geometry.attributes.position.count;
        const adaptiveMultiplier = Math.max(2, 8 - (particleCount / 500000));
        const sizeMultiplier = index === 0 ? 0.4 : 0.6; // Much smaller particles
        const finalSize = baseSize * currentMultiplier * glowSizeMultiplier * adaptiveMultiplier * sizeMultiplier;
        sphere.material.size = finalSize;
        
        // Update colors to simulate glow
        if (sphere.geometry.attributes.color) {
            const colors = sphere.geometry.attributes.color.array;
            const originalColors = sphere.geometry.userData.originalColors;
            
            // Store original colors if not already stored
            if (!originalColors) {
                sphere.geometry.userData.originalColors = new Float32Array(colors);
            }
            
            // Apply brightness with gamma correction
            const gamma = 1.0 / (0.6 + glowValue * 0.4);
            for (let i = 0; i < colors.length; i++) {
                const originalColor = originalColors ? originalColors[i] : colors[i];
                colors[i] = Math.pow(originalColor, gamma);
            }
            
            sphere.geometry.attributes.color.needsUpdate = true;
        }
        
        sphere.material.needsUpdate = true;
    });
    
    // Enhanced logging
    console.log(`✨ Glow intensity updated: ${(glowValue * 100).toFixed(0)}% → both spheres updated`);
    
    // Force render update
    if (typeof renderer !== 'undefined') {
        renderer.render(scene, camera);
    }
}

// Audio reactive integration
function resetToNormalState() {
    if ((innerSphereParticles || outerSphereParticles) && lights) {
        if (innerSphereParticles) {
            resetToNormalVisualState(innerSphereParticles, lights.ambientLight, lights.directionalLight);
        }
        if (outerSphereParticles) {
            resetToNormalVisualState(outerSphereParticles, lights.ambientLight, lights.directionalLight);
        }
    }
}

// Mouse interaction integration
function resetParticlePositions() {
    [innerSphereParticles, outerSphereParticles].forEach(sphere => {
        if (!sphere) return;
        
        // Use shared component function if available, otherwise use fallback
        if (typeof window.resetParticlePositions === 'function' && window.resetParticlePositions !== resetParticlePositions) {
            window.resetParticlePositions(sphere);
        } else {
            // Fallback: reset positions manually
            if (sphere.geometry.userData.originalPositions) {
                const positions = sphere.geometry.attributes.position.array;
                const originalPositions = sphere.geometry.userData.originalPositions;
                
                for (let i = 0; i < positions.length; i++) {
                    positions[i] = originalPositions[i];
                }
                
                sphere.geometry.attributes.position.needsUpdate = true;
            }
        }
        
        // Reset colors if available
        if (typeof resetParticleColors === 'function') {
            resetParticleColors(sphere);
        }
    });
}

// Music setup integration is handled in the HTML template

// Export functions to global scope for HTML events
window.toggleAutoRotate = toggleAutoRotate;
window.resetCamera = resetCamera;
window.updateParticleSize = updateParticleSize;
window.updateRotationSpeed = updateRotationSpeed;
window.toggleBrightness = toggleBrightness;
window.updateGlowIntensity = updateGlowIntensity;

// Re-export shared component functions
window.toggleMouseGravity = window.toggleMouseGravity || (() => console.warn('Mouse gravity function not loaded'));
window.toggleGravityMode = window.toggleGravityMode || (() => console.warn('Gravity mode function not loaded'));
window.updateGravityRange = window.updateGravityRange || (() => console.warn('Gravity range function not loaded'));
window.updateGravityStrength = window.updateGravityStrength || (() => console.warn('Gravity strength function not loaded'));
window.updateWaveIntensity = window.updateWaveIntensity || (() => console.warn('Wave intensity function not loaded'));
window.toggleAudioReactive = window.toggleAudioReactive || (() => console.warn('Audio reactive function not loaded'));
window.toggleMicrophone = window.toggleMicrophone || (() => console.warn('Microphone function not loaded'));
window.toggleAudioMode = window.toggleAudioMode || (() => console.warn('Audio mode function not loaded'));
window.toggleDynamicMode = window.toggleDynamicMode || (() => console.warn('Dynamic mode function not loaded'));

// Create background panorama sphere for immersive experience
// DUAL SPHERE: Create outer sphere pointcloud from panorama image
function createOuterSpherePointcloud(texture) {
    console.log('🌐 Creating outer sphere pointcloud from panorama image...');
    
    const img = texture.image;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Higher resolution for outer sphere
    const analysisWidth = 1024;
    const analysisHeight = 512;
    canvas.width = analysisWidth;
    canvas.height = analysisHeight;
    
    // Draw image to canvas for pixel analysis
    ctx.drawImage(img, 0, 0, analysisWidth, analysisHeight);
    const imageData = ctx.getImageData(0, 0, analysisWidth, analysisHeight);
    const pixels = imageData.data;
    
    // OPTIMIZED particle count for audio performance with microscopic particles
    const targetParticleCount = 150000; // 15万パーティクル（音楽連動最適化・マイクロ粒子対応）
    const totalPixels = analysisWidth * analysisHeight;
    const samplingRate = Math.min(1.0, targetParticleCount / totalPixels);
    
    const positions = [];
    const colors = [];
    
    console.log(`🎯 Outer sphere target: ${targetParticleCount.toLocaleString()} particles`);
    
    for (let y = 0; y < analysisHeight; y++) {
        for (let x = 0; x < analysisWidth; x++) {
            // Sample based on density
            if (Math.random() > samplingRate) continue;
            
            // Convert to normalized coordinates (0-1)
            const u = x / analysisWidth;
            const v = y / analysisHeight;
            
            // Convert to spherical coordinates (standard equirectangular)
            const phi = u * 2 * Math.PI;           // Longitude: 0 to 2π
            const theta = v * Math.PI;             // Latitude: 0 to π
            
            // Get pixel color
            const pixelIndex = (y * analysisWidth + x) * 4;
            const r = pixels[pixelIndex] / 255;
            const g = pixels[pixelIndex + 1] / 255;
            const b = pixels[pixelIndex + 2] / 255;
            const alpha = pixels[pixelIndex + 3] / 255;
            
            // Skip transparent pixels
            if (alpha < 0.1) continue;
            
            // DEPTH CALCULATION: Use brightness as pseudo-depth for spherical distribution
            const brightness = (r + g + b) / 3; // Average brightness as depth info
            const depthValue = brightness * 255; // Convert back to 0-255 range for depth calculation
            
            // Apply INVERTED spherical depth for cosmic/space scenes (bright=far, dark=near)
            let processedDepth = depthValue / 255.0; // Normalize to 0-1
            processedDepth = 1.0 - processedDepth; // INVERT: bright areas become distant
            if (processedDepth === 1.0) {
                processedDepth = 0.9; // Pure black areas = slightly closer
            } else if (processedDepth > 0.98) {
                processedDepth = 0.8; // Very dark = closer to viewer
            }
            
            // Calculate depth-based radius for outer sphere
            const outerBaseRadius = outerSphereRadius;
            const depthVariation = outerBaseRadius * 0.3; // 30% variation for outer sphere
            let adjustedRadius = outerBaseRadius + (processedDepth - 0.5) * depthVariation;
            
            // Scale to outer sphere range (keep farther from inner sphere)
            const outerMin = outerSphereRadius * 0.7; // 70% of outer radius (420)
            const outerMax = outerSphereRadius; // 100% of outer radius (600)
            const normalizedDepth = Math.max(0, Math.min(1, (adjustedRadius - (outerBaseRadius - depthVariation)) / (2 * depthVariation)));
            adjustedRadius = outerMin + normalizedDepth * (outerMax - outerMin);
            
            // Convert to Cartesian coordinates with depth-adjusted radius
            const sinTheta = Math.sin(theta);
            const cosTheta = Math.cos(theta);
            const cosPhi = Math.cos(phi);
            const sinPhi = Math.sin(phi);
            
            const x3d = adjustedRadius * sinTheta * cosPhi;
            const y3d = adjustedRadius * cosTheta;
            const z3d = adjustedRadius * sinTheta * sinPhi;
            
            positions.push(x3d, y3d, z3d);
            
            // ENHANCED colors for outer sphere - MUCH brighter and more vibrant
            const enhancementFactor = 2.0; // Doubled brightness boost
            const gammaCorrection = 0.8; // Increase contrast (lower gamma = more contrast)
            colors.push(
                Math.min(1.0, Math.pow(r, gammaCorrection) * enhancementFactor),
                Math.min(1.0, Math.pow(g, gammaCorrection) * enhancementFactor),
                Math.min(1.0, Math.pow(b, gammaCorrection) * enhancementFactor)
            );
        }
    }
    
    // Create geometry for outer sphere
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(positions), 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(colors), 3));
    geometry.computeBoundingSphere();
    
    // Create outer sphere particle system - BRIGHTER and more visible - MUCH SMALLER PARTICLES
    outerSphereParticles = createParticleSystem(geometry, {
        size: particleSize * 0.3,  // Much smaller particles for finer detail (0.8->0.3)
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.95,  // More opaque for better visibility
        vertexColors: true,
        blending: THREE.NormalBlending
    });
    
    scene.add(outerSphereParticles);
    
    console.log(`✅ Outer sphere created: ${positions.length / 3} particles`);
    console.log(`Outer sphere radius: ${outerSphereRadius}`);
}

// DUAL SPHERE: Fallback outer sphere creation
function createOuterSphereFallback() {
    console.log('🧪 Creating fallback outer sphere pointcloud...');
    
    const particleCount = 500000; // Increased for better fallback quality
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount; i++) {
        // Uniform distribution on outer sphere
        const u = Math.random();
        const v = Math.random();
        
        const phi = u * 2 * Math.PI;
        const theta = Math.acos(2 * v - 1);
        
        const x = outerSphereRadius * Math.sin(theta) * Math.cos(phi);
        const y = outerSphereRadius * Math.cos(theta);
        const z = outerSphereRadius * Math.sin(theta) * Math.sin(phi);
        
        positions[i * 3] = x;
        positions[i * 3 + 1] = y;
        positions[i * 3 + 2] = z;
        
        // Cosmic colors for fallback
        colors[i * 3] = 0.3 + Math.random() * 0.7;     // R
        colors[i * 3 + 1] = 0.2 + Math.random() * 0.6; // G  
        colors[i * 3 + 2] = 0.5 + Math.random() * 0.5; // B
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    outerSphereParticles = createParticleSystem(geometry, {
        size: particleSize * 0.3, // Much smaller for finer detail (0.8->0.3)
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.95, // More opaque for visibility
        vertexColors: true
    });
    
    scene.add(outerSphereParticles);
    
    console.log(`✅ Fallback outer sphere created: ${particleCount} particles`);
}

// Basic audio system initialization
let panoramaAudioContext = null;
let panoramaAudioElement = null;
let panoramaMusicPlaying = false;

function initializeBasicAudioSystem() {
    console.log('🎵 Setting up basic audio system...');
    
    // Find music file in the page - try multiple possible names
    const musicFiles = [
        'assets/background-music.wav', 
        'assets/background-music.mp3',
        'assets/music.wav',
        'assets/music.mp3',
        'assets/generated-music.wav',
        'assets/generated-music.mp3'
    ];
    
    for (const file of musicFiles) {
        const audio = new Audio(file);
        audio.onerror = () => console.log(`🎵 Music file not found: ${file}`);
        audio.oncanplay = () => {
            panoramaAudioElement = audio;
            panoramaAudioElement.loop = true;
            panoramaAudioElement.volume = 0.5;
            console.log(`✅ Music loaded: ${file}`);
        };
        audio.load();
        if (panoramaAudioElement) break;
    }
    
    // Initialize Web Audio API for reactive effects
    try {
        panoramaAudioContext = new (window.AudioContext || window.webkitAudioContext)();
        console.log('✅ Web Audio API initialized');
    } catch (error) {
        console.warn('🎵 Web Audio API not available:', error);
    }
}

// Music control functions
function toggleMusic() {
    if (panoramaAudioElement) {
        if (panoramaMusicPlaying) {
            panoramaAudioElement.pause();
            panoramaMusicPlaying = false;
            console.log('🎵 Music paused');
            // Update button text if exists
            const button = document.getElementById('musicToggle');
            if (button) button.textContent = '🎵 Music OFF';
        } else {
            panoramaAudioElement.play().then(() => {
                panoramaMusicPlaying = true;
                console.log('🎵 Music playing');
                // Update button text if exists
                const button = document.getElementById('musicToggle');
                if (button) button.textContent = '🎵 Music ON';
            }).catch(error => {
                console.warn('🎵 Music play failed:', error);
            });
        }
    } else if (typeof window.toggleMusicPlayback === 'function') {
        window.toggleMusicPlayback();
    } else {
        console.warn('🎵 Music system not available');
    }
}

function toggleAudioReactive() {
    // Use shared audio reactive system if available
    if (typeof window.toggleAudioReactive === 'function' && window.toggleAudioReactive !== toggleAudioReactive) {
        window.toggleAudioReactive();
        return;
    }
    
    audioReactiveEnabled = !audioReactiveEnabled;
    
    const button = document.getElementById('audioReactiveToggle');
    if (button) {
        button.textContent = audioReactiveEnabled ? '🔊 Audio React ON' : '🔇 Audio React OFF';
    }
    
    if (audioReactiveEnabled) {
        // Initialize audio context if not already done
        if (!audioContext) {
            try {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                console.log('✅ Audio context created');
            } catch (error) {
                console.error('❌ Failed to create audio context:', error);
                audioReactiveEnabled = false;
                return;
            }
        }
        
        // Setup music analyser if music is available
        if (panoramaAudioElement && !musicAnalyser) {
            try {
                const source = audioContext.createMediaElementSource(panoramaAudioElement);
                musicAnalyser = audioContext.createAnalyser();
                musicAnalyser.fftSize = 2048;
                musicAnalyser.smoothingTimeConstant = 0.8;
                
                source.connect(musicAnalyser);
                musicAnalyser.connect(audioContext.destination);
                
                musicDataArray = new Uint8Array(musicAnalyser.frequencyBinCount);
                console.log('✅ Music analyser connected');
            } catch (error) {
                console.warn('⚠️ Music analyser setup failed:', error);
            }
        }
        
        console.log('🎵 Audio reactive effects enabled');
    } else {
        // Reset visual effects when disabled
        resetAudioEffects();
        console.log('🔇 Audio reactive effects disabled');
    }
}

function toggleMicrophone() {
    if (typeof window.toggleMicrophone === 'function' && window.toggleMicrophone !== toggleMicrophone) {
        window.toggleMicrophone();
    } else {
        console.warn('🎤 Microphone system not available');
        // Basic microphone toggle fallback
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            console.log('🎤 Attempting to access microphone...');
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    console.log('🎤 Microphone access granted');
                    // Store stream for later use
                    window.microphoneStream = stream;
                })
                .catch(error => {
                    console.warn('🎤 Microphone access denied:', error);
                });
        }
    }
}

// Audio reactive effects functions
function analyzeAudio() {
    if (!audioReactiveEnabled) return;
    
    let dataArray = null;
    let analyser = null;
    
    if (microphoneEnabled && micAnalyser) {
        analyser = micAnalyser;
        dataArray = micDataArray;
    } else if (musicAnalyser && panoramaMusicPlaying) {
        analyser = musicAnalyser;
        dataArray = musicDataArray;
    }
    
    if (!analyser || !dataArray) return;
    
    // Get frequency data
    analyser.getByteFrequencyData(dataArray);
    
    // Calculate overall volume
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
    }
    const averageVolume = sum / dataArray.length / 255;
    currentVolumeLevel = currentVolumeLevel * volumeSmoothing + averageVolume * (1 - volumeSmoothing);
    
    // Analyze frequency bands
    const sampleRate = audioContext.sampleRate;
    const binCount = analyser.frequencyBinCount;
    const binFrequency = sampleRate / (binCount * 2);
    
    // Bass: 60-250Hz
    const bassStart = Math.floor(60 / binFrequency);
    const bassEnd = Math.floor(250 / binFrequency);
    let bassSum = 0;
    for (let i = bassStart; i < bassEnd; i++) {
        bassSum += dataArray[i];
    }
    frequencyBands.bass = bassSum / (bassEnd - bassStart) / 255;
    
    // Mid: 250-2000Hz
    const midStart = Math.floor(250 / binFrequency);
    const midEnd = Math.floor(2000 / binFrequency);
    let midSum = 0;
    for (let i = midStart; i < midEnd; i++) {
        midSum += dataArray[i];
    }
    frequencyBands.mid = midSum / (midEnd - midStart) / 255;
    
    // Treble: 2000-8000Hz
    const trebleStart = Math.floor(2000 / binFrequency);
    const trebleEnd = Math.floor(8000 / binFrequency);
    let trebleSum = 0;
    for (let i = trebleStart; i < trebleEnd; i++) {
        trebleSum += dataArray[i];
    }
    frequencyBands.treble = trebleSum / (trebleEnd - trebleStart) / 255;
}

function applyAudioReactiveEffects() {
    if ((!innerSphereParticles && !outerSphereParticles) || !audioReactiveEnabled) return;
    
    // Analyze audio
    analyzeAudio();
    
    // Calculate effect intensities - ENHANCED for more dramatic response
    const bassImpact = Math.pow(frequencyBands.bass, 1.2); // Reduced power for more sensitivity
    const midImpact = Math.pow(frequencyBands.mid, 0.8); // Add power curve for better response  
    const trebleImpact = Math.pow(frequencyBands.treble, 0.6); // More sensitive to treble
    const volumeImpact = Math.pow(currentVolumeLevel, 0.5); // Much more sensitive to volume changes
    
    // EXTREME: Effects go from minimal to massive (very dramatic changes)
    // This creates extremely dramatic "tiny dim → huge bright" effect
    panoramaEffects.sizeMultiplier = 0.1 + bassImpact * 2.4; // Size: 10% to 250% based on bass (MASSIVE RANGE)
    panoramaEffects.brightnessMultiplier = 0.05 + volumeImpact * 1.95; // Brightness: 5% to 200% based on volume (EXTREME RANGE)
    panoramaEffects.movementIntensity = 0.0 + trebleImpact * 1.5; // Movement: 0% to 150% based on treble (ENHANCED RANGE)
    
    // NEW: Frequency-based color mixing for musical visualization
    panoramaEffects.colorMix = {
        bassRed: bassImpact * 1.5,      // 🔴 Bass → Red/Orange (warm, heavy)
        midGreen: midImpact * 1.2,      // 🟢 Mid → Green/Yellow (melody, natural)  
        trebleBlue: trebleImpact * 1.8  // 🔵 Treble → Blue/Purple (sharp, cool)
    };
    
    // Add beat detection for dramatic pulses - now works within 0-1 range
    const currentBass = frequencyBands.bass;
    const bassChange = Math.abs(currentBass - (panoramaEffects.lastBass || 0));
    if (bassChange > 0.3) { // Strong bass change detected
        panoramaEffects.beatPulse = 1.5; // Moderate beat pulse (was 2.0)
    } else {
        panoramaEffects.beatPulse = Math.max(1.0, (panoramaEffects.beatPulse || 1.0) * 0.95); // Slower fade
    }
    panoramaEffects.lastBass = currentBass;
    
    // Apply size effect to both spheres - ENHANCED with beat pulse
    const baseMultiplier = audioReactiveEnabled ? panoramaEffects.sizeMultiplier : 1.0;
    const beatMultiplier = audioReactiveEnabled ? (panoramaEffects.beatPulse || 1.0) : 1.0;
    const totalMultiplier = baseMultiplier * beatMultiplier;
    const effectiveSize = particleSize * totalMultiplier;
    
    if (innerSphereParticles && innerSphereParticles.material) {
        const particleCount = innerSphereParticles.geometry.attributes.position.count;
        const adaptiveMultiplier = Math.max(2, 8 - (particleCount / 500000));
        const finalSize = Math.max(0.5, effectiveSize * adaptiveMultiplier * 0.4); // Much smaller for detail
        innerSphereParticles.material.size = finalSize;
        innerSphereParticles.material.needsUpdate = true;
    }
    
    if (outerSphereParticles && outerSphereParticles.material) {
        const particleCount = outerSphereParticles.geometry.attributes.position.count;
        const adaptiveMultiplier = Math.max(2, 8 - (particleCount / 500000));
        const finalSize = Math.max(0.5, effectiveSize * adaptiveMultiplier * 0.6); // Smaller for detail
        outerSphereParticles.material.size = finalSize;
        outerSphereParticles.material.needsUpdate = true;
    }
    
    // Apply color effects to both spheres
    const brightness = panoramaEffects.brightnessMultiplier;
    
    [innerSphereParticles, outerSphereParticles].forEach(sphere => {
        if (!sphere || !sphere.geometry.attributes.color) return;
        
        const colors = sphere.geometry.attributes.color.array;
        const originalColors = sphere.geometry.userData.originalColors;
        
        if (!originalColors) {
            sphere.geometry.userData.originalColors = new Float32Array(colors);
            return; // Skip first frame to ensure original colors are stored
        }
        
        for (let i = 0; i < colors.length; i += 3) {
            const originalColor = originalColors[i];
            const originalColorG = originalColors[i + 1];
            const originalColorB = originalColors[i + 2];
            
            // Apply brightness with gamma correction
            const gamma = 1.0 / (0.5 + brightness * 0.5);
            colors[i] = Math.pow(originalColor, gamma);
            colors[i + 1] = Math.pow(originalColorG, gamma);
            colors[i + 2] = Math.pow(originalColorB, gamma);
        }
        
        sphere.geometry.attributes.color.needsUpdate = true;
    });
    
    // Apply movement effect to both spheres (subtle position variations)
    if (panoramaEffects.movementIntensity > 0.1) {
        const time = Date.now() * 0.001;
        const movement = panoramaEffects.movementIntensity * 2.0;
        
        [innerSphereParticles, outerSphereParticles].forEach(sphere => {
            if (!sphere || !sphere.geometry.attributes.position) return;
            
            const positions = sphere.geometry.attributes.position.array;
            let originalPositions = sphere.geometry.userData.originalPositions;
            
            if (!originalPositions) {
                sphere.geometry.userData.originalPositions = new Float32Array(positions);
                return; // Skip first frame
            }
            
            for (let i = 0; i < positions.length; i += 3) {
                const offset = Math.sin(time * 2 + i * 0.01) * movement;
                positions[i] = originalPositions[i] + offset;
                positions[i + 1] = originalPositions[i + 1] + offset * 0.5;
                positions[i + 2] = originalPositions[i + 2] + offset * 0.7;
            }
            
            sphere.geometry.attributes.position.needsUpdate = true;
        });
    }
    
    // Enhanced debug logging for audio reactive testing
    if (Math.random() < 0.05) { // 5% chance to log for frequent feedback
        console.log(`🎵 AUDIO: vol=${(volumeImpact * 100).toFixed(1)}% bass=${(bassImpact * 100).toFixed(1)}% mid=${(midImpact * 100).toFixed(1)}% treble=${(trebleImpact * 100).toFixed(1)}%`);
        console.log(`🎨 EFFECTS: size=${panoramaEffects.sizeMultiplier.toFixed(2)}x bright=${panoramaEffects.brightnessMultiplier.toFixed(2)}x move=${panoramaEffects.movementIntensity.toFixed(2)}`);
        console.log(`🌈 COLORS: red=${panoramaEffects.colorMix.bassRed.toFixed(2)} green=${panoramaEffects.colorMix.midGreen.toFixed(2)} blue=${panoramaEffects.colorMix.trebleBlue.toFixed(2)}`);
    }
}

// NEW: Apply frequency-based color mixing to particles  
function applyFrequencyColorMixing() {
    if ((!innerSphereParticles && !outerSphereParticles) || !audioReactiveEnabled || !panoramaEffects.colorMix) return;
    
    const colorMix = panoramaEffects.colorMix;
    
    [innerSphereParticles, outerSphereParticles].forEach(sphere => {
        if (!sphere) return;
        
        const geometry = sphere.geometry;
        const colors = geometry.attributes.color.array;
        const originalColors = geometry.userData.originalColors;
    
        // Store original colors if not already stored
        if (!originalColors) {
            geometry.userData.originalColors = new Float32Array(colors);
            return; // Skip first frame to ensure original colors are stored
        }
        
        // Apply frequency-based color mixing
        for (let i = 0; i < colors.length; i += 3) {
            const origR = originalColors[i];
            const origG = originalColors[i + 1]; 
            const origB = originalColors[i + 2];
            
            // Calculate light intensity based on frequency strengths
            const bassLight = colorMix.bassRed * 0.8;
            const midLight = colorMix.midGreen * 0.6;
            const trebleLight = colorMix.trebleBlue * 0.7;
            
            // ADDITIVE BLENDING: Original color + Musical light
            colors[i] = Math.min(1.0, origR + bassLight * 0.9);
            colors[i + 1] = Math.min(1.0, origG + midLight * 0.8);
            colors[i + 2] = Math.min(1.0, origB + trebleLight * 1.0);
            
            // Cross-illumination and sparkle effects
            colors[i + 1] = Math.min(1.0, colors[i + 1] + bassLight * 0.2);
            colors[i + 2] = Math.min(1.0, colors[i + 2] + bassLight * 0.1);
            
            const sparkle = trebleLight * 0.15;
            colors[i] = Math.min(1.0, colors[i] + sparkle);
            colors[i + 1] = Math.min(1.0, colors[i + 1] + sparkle);
            colors[i + 2] = Math.min(1.0, colors[i + 2] + sparkle * 1.5);
        }
        
        geometry.attributes.color.needsUpdate = true;
    });
}

function resetAudioEffects() {
    // Reset effect intensities
    panoramaEffects.sizeMultiplier = 1.0;
    panoramaEffects.brightnessMultiplier = 1.0;
    panoramaEffects.colorIntensity = 0.0;
    panoramaEffects.movementIntensity = 0.0;
    
    // Reset both spheres properties
    const currentSliderValue = document.getElementById('particleSize') ? 
        parseFloat(document.getElementById('particleSize').value) : particleSize;
    
    [innerSphereParticles, outerSphereParticles].forEach((sphere, index) => {
        if (!sphere) return;
        
        if (sphere.material) {
            const particleCount = sphere.geometry.attributes.position.count;
            const adaptiveMultiplier = Math.max(2, 8 - (particleCount / 500000));
            const sizeMultiplier = index === 0 ? 0.4 : 0.6; // Much smaller particles
            const finalSize = Math.max(1.0, currentSliderValue * adaptiveMultiplier * sizeMultiplier);
            sphere.material.size = finalSize;
            sphere.material.needsUpdate = true;
        }
        
        // Reset colors
        if (sphere.geometry.attributes.color && sphere.geometry.userData.originalColors) {
            const colors = sphere.geometry.attributes.color.array;
            const originalColors = sphere.geometry.userData.originalColors;
            
            for (let i = 0; i < colors.length; i++) {
                colors[i] = originalColors[i];
            }
            
            sphere.geometry.attributes.color.needsUpdate = true;
        }
        
        // Reset positions
        if (sphere.geometry.attributes.position && sphere.geometry.userData.originalPositions) {
            const positions = sphere.geometry.attributes.position.array;
            const originalPositions = sphere.geometry.userData.originalPositions;
            
            for (let i = 0; i < positions.length; i++) {
                positions[i] = originalPositions[i];
            }
            
            sphere.geometry.attributes.position.needsUpdate = true;
        }
    });
}

// Export all interactive functions to global scope for HTML template
window.toggleMusic = toggleMusic;
window.toggleAudioReactive = toggleAudioReactive;
window.toggleMicrophone = toggleMicrophone;
window.updatePointSize = updateParticleSize;

// Export slider functions (CRITICAL FIX)
window.updateParticleSize = updateParticleSize;
window.updateGlowIntensity = updateGlowIntensity;

// Export other control functions
window.resetCamera = resetCamera;
window.toggleBrightness = toggleBrightness;

// Debug: Test slider functions on initialization
console.log('🔧 Testing slider functions availability...');
setTimeout(() => {
    console.log('🔧 updateParticleSize available:', typeof window.updateParticleSize);
    console.log('🔧 updateGlowIntensity available:', typeof window.updateGlowIntensity);
    
    // Test the functions
    console.log('🔧 Testing particle size change...');
    if (typeof window.updateParticleSize === 'function') {
        window.updateParticleSize(10.0); // Test with MAXIMUM size (adaptive multiplier based on particle count)
    }
}, 2000);

if (typeof setupMusic !== 'undefined') {
    window.setupMusic = setupMusic;
}

// Start the panorama application
init();