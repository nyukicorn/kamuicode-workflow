// 360° Panorama Viewer - Depth-Enhanced Spherical Particle Distribution
// Uses shared components for camera, UI, audio, and mouse interaction
// Implements PLY loading with depth information from pointcloud-panorama-generation

// Global variables (panorama specific)
let panoramaParticles = null;
let panoramaTexture = null;
let lights = null;
let sphereRadius = 200;

// Use shared audio variables from audio-reactive-system.js
// These variables are already declared in the shared component

// Panorama-specific effect intensities
let panoramaEffects = {
    sizeMultiplier: 1.0,
    brightnessMultiplier: 1.0,
    colorIntensity: 1.0,
    movementIntensity: 0.0
};

// Panorama configuration - 360度パノラマ用に最適化 - ENHANCED for visibility
let particleSize = 5.0; // Increased from 3.5 to 5.0 for better initial visibility
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
    
    // 360度パノラマ用にカメラ制約を調整
    const optimalViewingDistance = sphereRadius * 0.3; // 球体半径の30%の位置
    
    // Configure controls for panoramic experience
    controls.enablePan = false; // Disable panning for true panoramic experience
    controls.minDistance = 5;   // Minimum zoom in
    controls.maxDistance = sphereRadius - 20; // Maximum zoom out (stay inside sphere)
    
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
    
    // CRITICAL FIX: Use fixed sphere radius instead of boundingSphere calculation
    // PLY particles are already constrained to radius 200, but boundingSphere 
    // calculation returns incorrect huge values causing coordinate scaling issues
    sphereRadius = 200;
    console.log(`📏 Using fixed sphere radius: ${sphereRadius} (boundingSphere calculation disabled)`);
    
    // Adjust camera constraints based on fixed sphere size
    controls.maxDistance = sphereRadius - 20; // 180
    
    // Add depth visualization if enabled
    if (enableDepthVisualization && colors) {
        enhanceDepthVisualization(positions, colors);
    }
    
    // Create particle system using shared component - 360度パノラマ用に最適化
    panoramaParticles = createParticleSystem(geometry, {
        size: particleSize,
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.95,  // 不透明度を上げて見やすく
        vertexColors: true,
        blending: THREE.AdditiveBlending
    });
    
    scene.add(panoramaParticles);
    
    // Initialize mouse interaction with the panorama
    initializeMouseInteraction(panoramaParticles, camera);
    
    // Update UI with statistics
    updateStatsDisplay(panoramaParticles);
    hideLoadingIndicator();
    
    console.log(`✅ Depth-enhanced panorama created: ${positions.count.toLocaleString()} particles`);
    console.log(`Sphere radius: ${sphereRadius}, Camera at center`);
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
        case 'low': particleCount = 500000; break;     // 50万パーティクル
        case 'high': particleCount = 3000000; break;   // 300万パーティクル
        default: particleCount = 1500000; // medium    // 150万パーティクル
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
        const adjustedRadius = sphereRadius * radiusMultiplier;
        
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
    
    // Create particle system using shared component
    panoramaParticles = createParticleSystem(geometry, {
        size: particleSize,
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.9,
        vertexColors: true
    });
    
    scene.add(panoramaParticles);
    
    // Initialize mouse interaction with the panorama
    initializeMouseInteraction(panoramaParticles, camera);
    
    // Update UI
    updateStatsDisplay(panoramaParticles);
    hideLoadingIndicator();
    
    console.log(`✅ Spherical panorama created: ${particleIndex.toLocaleString()} particles`);
    console.log(`Sphere radius: ${sphereRadius}, Camera at center`);
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
        const adjustedRadius = sphereRadius * radiusMultiplier;
        
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
    
    panoramaParticles = createParticleSystem(geometry, {
        size: particleSize,
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.9,
        vertexColors: true
    });
    
    scene.add(panoramaParticles);
    initializeMouseInteraction(panoramaParticles, camera);
    updateStatsDisplay(panoramaParticles);
    hideLoadingIndicator();
    
    console.log('✅ Test spherical pattern with depth variation created');
}

// Audio reactive effects run at full 60fps for maximum immersion

function animate() {
    requestAnimationFrame(animate);
    
    // Update camera controls (shared component)
    updateCameraControls();
    
    // Apply mouse gravity effect (shared component)
    if (panoramaParticles) {
        applyMouseGravity(panoramaParticles);
    }
    
    // Apply audio-reactive effects (shared component) - 60fps for maximum immersion
    if ((audioReactiveEnabled || microphoneEnabled) && panoramaParticles) {
        applyAudioReactiveEffects();
        // Apply frequency-based color mixing
        applyFrequencyColorMixing();
    }
    
    // Update particle system effects (shared component)
    if (panoramaParticles) {
        updateParticleSystem(panoramaParticles, camera, lights.ambientLight, lights.directionalLight);
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
    if (panoramaParticles && panoramaParticles.material) {
        // Apply size with current audio effect multiplier - ENHANCED for dramatic visibility
        const currentMultiplier = audioReactiveEnabled ? panoramaEffects.sizeMultiplier : 1.0;
        const effectiveSize = particleSize * currentMultiplier;
        
        // ADAPTIVE: Adjust multiplier based on particle count for optimal visibility
        const particleCount = panoramaParticles.geometry.attributes.position.count;
        const adaptiveMultiplier = Math.max(10, 40 - (particleCount / 100000));
        // 100万→30倍、200万→20倍、300万→10倍、400万→10倍（最小値）
        
        // Ensure minimum visible size and apply adaptive scaling
        const finalSize = Math.max(1.0, effectiveSize * adaptiveMultiplier);
        panoramaParticles.material.size = finalSize;
        panoramaParticles.material.needsUpdate = true;
        
        console.log(`📏 Adaptive particle size: ${particleCount.toLocaleString()} particles → ${adaptiveMultiplier}x multiplier`);
        
        // FORCE the material to update immediately
        panoramaParticles.material.uniformsNeedUpdate = true;
        
        console.log(`✨ Particle size updated: ${particleSize} → effective: ${effectiveSize} → final: ${finalSize}`);
        
        // Force render update multiple times
        if (typeof renderer !== 'undefined') {
            renderer.render(scene, camera);
            // Force immediate second render
            requestAnimationFrame(() => {
                renderer.render(scene, camera);
            });
        }
    }
}

function toggleBrightness() {
    window.toggleBrightness(scene, lights.ambientLight, lights.directionalLight, 'BACKGROUND_COLOR_PLACEHOLDER');
}

function updateGlowIntensity(value) {
    const glowValue = parseFloat(value) / 100; // Convert 0-200 to 0-2 (now supports 200% glow)
    
    if (panoramaParticles && panoramaParticles.material) {
        // Update material properties for glow effect - EXTREME for visibility
        const baseBrightness = 1.0;
        const glowBrightness = baseBrightness + (glowValue * 2.0); // Max 3.0x brightness - DRAMATIC glow effect
        
        // Create emissive-like effect by adjusting material properties
        panoramaParticles.material.opacity = Math.min(1.0, 0.6 + glowValue * 0.4); // ENHANCED dramatic opacity change
        panoramaParticles.material.blending = glowValue > 0.1 ? THREE.AdditiveBlending : THREE.NormalBlending; // MUCH lower threshold for instant glow
        
        // Scale particles moderately for glow effect - BALANCED for visibility
        const baseSize = particleSize;
        const currentMultiplier = audioReactiveEnabled ? panoramaEffects.sizeMultiplier : 1.0;
        const glowSizeMultiplier = 1.0 + glowValue * 1.2; // Moderate size effect (reduced from 3x)
        const finalSize = baseSize * currentMultiplier * glowSizeMultiplier * 4.0; // 4x base multiplier for dense particles
        panoramaParticles.material.size = finalSize;
        
        // Update colors to simulate glow
        if (panoramaParticles.geometry.attributes.color) {
            const colors = panoramaParticles.geometry.attributes.color.array;
            const originalColors = panoramaParticles.geometry.userData.originalColors;
            
            // Store original colors if not already stored
            if (!originalColors) {
                panoramaParticles.geometry.userData.originalColors = new Float32Array(colors);
            }
            
            // Apply brightness with gamma correction - prevent white washout
            const gamma = 1.0 / (0.6 + glowValue * 0.4); // Dynamic gamma from 1.67 to 1.0
            for (let i = 0; i < colors.length; i++) {
                const originalColor = originalColors ? originalColors[i] : colors[i];
                colors[i] = Math.pow(originalColor, gamma);
            }
            
            panoramaParticles.geometry.attributes.color.needsUpdate = true;
        }
        
        panoramaParticles.material.needsUpdate = true;
        
        // Enhanced logging with more details
        console.log(`✨ Glow intensity updated: ${(glowValue * 100).toFixed(0)}% → size: ${finalSize.toFixed(2)} brightness: ${glowBrightness.toFixed(2)}x`);
        
        // Force render update
        if (typeof renderer !== 'undefined') {
            renderer.render(scene, camera);
        }
    }
}

// Audio reactive integration
function resetToNormalState() {
    if (panoramaParticles && lights) {
        resetToNormalVisualState(panoramaParticles, lights.ambientLight, lights.directionalLight);
    }
}

// Mouse interaction integration
function resetParticlePositions() {
    if (panoramaParticles) {
        // Use shared component function if available, otherwise use fallback
        if (typeof window.resetParticlePositions === 'function' && window.resetParticlePositions !== resetParticlePositions) {
            window.resetParticlePositions(panoramaParticles);
        } else {
            // Fallback: reset positions manually
            if (panoramaParticles.geometry.userData.originalPositions) {
                const positions = panoramaParticles.geometry.attributes.position.array;
                const originalPositions = panoramaParticles.geometry.userData.originalPositions;
                
                for (let i = 0; i < positions.length; i++) {
                    positions[i] = originalPositions[i];
                }
                
                panoramaParticles.geometry.attributes.position.needsUpdate = true;
            }
        }
        
        // Reset colors if available
        if (typeof resetParticleColors === 'function') {
            resetParticleColors(panoramaParticles);
        }
    }
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
function createBackgroundPanoramaSphere(texture) {
    console.log('🌐 Creating background panorama sphere...');
    
    // Create sphere geometry (large radius, facing inward)
    const sphereGeometry = new THREE.SphereGeometry(sphereRadius * 2, 64, 32);
    
    // Create material with panorama texture
    const sphereMaterial = new THREE.MeshBasicMaterial({
        map: texture,
        side: THREE.BackSide // Important: render on inside faces
    });
    
    // Create the background sphere mesh
    const backgroundSphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
    backgroundSphere.name = 'backgroundPanorama';
    
    // Add to scene
    scene.add(backgroundSphere);
    
    console.log('✅ Background panorama sphere created');
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
    if (!panoramaParticles || !audioReactiveEnabled) return;
    
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
    
    // Apply size effect - ENHANCED with beat pulse for dramatic music response
    if (panoramaParticles.material) {
        const baseMultiplier = audioReactiveEnabled ? panoramaEffects.sizeMultiplier : 1.0;
        const beatMultiplier = audioReactiveEnabled ? (panoramaEffects.beatPulse || 1.0) : 1.0;
        const totalMultiplier = baseMultiplier * beatMultiplier;
        const effectiveSize = particleSize * totalMultiplier;
        // Use adaptive multiplier for audio reactive effects too
        const particleCount = panoramaParticles.geometry.attributes.position.count;
        const adaptiveMultiplier = Math.max(10, 40 - (particleCount / 100000));
        const finalSize = Math.max(1.0, effectiveSize * adaptiveMultiplier); // Same adaptive multiplier as slider
        panoramaParticles.material.size = finalSize;
        panoramaParticles.material.needsUpdate = true;
    }
    
    // Apply color effects
    if (panoramaParticles.geometry.attributes.color) {
        const colors = panoramaParticles.geometry.attributes.color.array;
        const originalColors = panoramaParticles.geometry.userData.originalColors;
        
        if (!originalColors) {
            panoramaParticles.geometry.userData.originalColors = new Float32Array(colors);
        }
        
        const brightness = panoramaEffects.brightnessMultiplier;
        const colorShift = panoramaEffects.colorIntensity;
        
        for (let i = 0; i < colors.length; i += 3) {
            // Apply subtle enhancement that preserves original colors - BALANCED approach
            const originalColor = originalColors ? originalColors[i] : colors[i];
            const originalColorG = originalColors ? originalColors[i + 1] : colors[i + 1];
            const originalColorB = originalColors ? originalColors[i + 2] : colors[i + 2];
            
            // Apply brightness with color preservation - prevent white washout
            // Use gamma correction instead of simple multiplication
            const gamma = 1.0 / (0.5 + brightness * 0.5); // Dynamic gamma from 2.0 to 0.67
            colors[i] = Math.pow(originalColor, gamma);     // R - Gamma correction
            colors[i + 1] = Math.pow(originalColorG, gamma); // G - Gamma correction  
            colors[i + 2] = Math.pow(originalColorB, gamma); // B - Gamma correction
        }
        
        panoramaParticles.geometry.attributes.color.needsUpdate = true;
    }
    
    // Apply movement effect (subtle position variations)
    if (panoramaEffects.movementIntensity > 0.1 && panoramaParticles.geometry.attributes.position) {
        const positions = panoramaParticles.geometry.attributes.position.array;
        let originalPositions = panoramaParticles.geometry.userData.originalPositions;
        
        if (!originalPositions) {
            panoramaParticles.geometry.userData.originalPositions = new Float32Array(positions);
            originalPositions = panoramaParticles.geometry.userData.originalPositions;
        }
        
        const time = Date.now() * 0.001;
        const movement = panoramaEffects.movementIntensity * 2.0;
        
        // Ensure originalPositions is properly initialized
        if (!originalPositions || originalPositions.length === 0) {
            console.warn('⚠️ originalPositions not initialized properly, skipping movement effect');
            return;
        }
        
        for (let i = 0; i < positions.length; i += 3) {
            const offset = Math.sin(time * 2 + i * 0.01) * movement;
            positions[i] = originalPositions[i] + offset;
            positions[i + 1] = originalPositions[i + 1] + offset * 0.5;
            positions[i + 2] = originalPositions[i + 2] + offset * 0.7;
        }
        
        panoramaParticles.geometry.attributes.position.needsUpdate = true;
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
    if (!panoramaParticles || !audioReactiveEnabled || !panoramaEffects.colorMix) return;
    
    const geometry = panoramaParticles.geometry;
    const colors = geometry.attributes.color.array;
    const originalColors = geometry.userData.originalColors;
    
    // Store original colors if not already stored
    if (!originalColors) {
        geometry.userData.originalColors = new Float32Array(colors);
        return; // Skip first frame to ensure original colors are stored
    }
    
    const colorMix = panoramaEffects.colorMix;
    
    // Apply frequency-based color mixing
    for (let i = 0; i < colors.length; i += 3) {
        const origR = originalColors[i];
        const origG = originalColors[i + 1]; 
        const origB = originalColors[i + 2];
        
        // ADDITIVE BLEND: Music adds light to original colors (like stage lighting)
        // This preserves original beauty while adding musical illumination
        
        // Calculate light intensity based on frequency strengths
        // 🔴 Bass adds warm red/orange light (sunset effect)
        const bassLight = colorMix.bassRed * 0.8; // Strong warm light
        
        // 🟢 Mid adds natural green/yellow light (life energy)  
        const midLight = colorMix.midGreen * 0.6; // Moderate natural light
        
        // 🔵 Treble adds cool blue/purple light (moonlight effect)
        const trebleLight = colorMix.trebleBlue * 0.7; // Cool ethereal light
        
        // ADDITIVE BLENDING: Original color + Musical light
        // This creates a "music illuminates the scene" effect
        colors[i] = Math.min(1.0, origR + bassLight * 0.9);      // Red: Original + warm bass light
        colors[i + 1] = Math.min(1.0, origG + midLight * 0.8);   // Green: Original + natural mid light
        colors[i + 2] = Math.min(1.0, origB + trebleLight * 1.0); // Blue: Original + cool treble light
        
        // Cross-illumination for more interesting color mixing
        // Bass also slightly warms greens and blues
        colors[i + 1] = Math.min(1.0, colors[i + 1] + bassLight * 0.2);  // Warm up greens
        colors[i + 2] = Math.min(1.0, colors[i + 2] + bassLight * 0.1);  // Slightly warm blues
        
        // Treble adds sparkle to all channels for shimmer effect
        const sparkle = trebleLight * 0.15;
        colors[i] = Math.min(1.0, colors[i] + sparkle);
        colors[i + 1] = Math.min(1.0, colors[i + 1] + sparkle);
        colors[i + 2] = Math.min(1.0, colors[i + 2] + sparkle * 1.5); // Extra blue sparkle
    }
    
    geometry.attributes.color.needsUpdate = true;
}

function resetAudioEffects() {
    // Reset effect intensities
    panoramaEffects.sizeMultiplier = 1.0;
    panoramaEffects.brightnessMultiplier = 1.0;
    panoramaEffects.colorIntensity = 0.0;
    panoramaEffects.movementIntensity = 0.0;
    
    // Reset particle properties
    if (panoramaParticles) {
        if (panoramaParticles.material) {
            // Use current slider value, not the multiplied value
            // FIXED: Apply the same 8x multiplier as everywhere else
            const currentSliderValue = document.getElementById('particleSize') ? 
                parseFloat(document.getElementById('particleSize').value) : particleSize;
            // Apply adaptive multiplier based on particle count
            const particleCount = panoramaParticles.geometry.attributes.position.count;
            const adaptiveMultiplier = Math.max(10, 40 - (particleCount / 100000));
            const finalSize = Math.max(1.0, currentSliderValue * adaptiveMultiplier); // Apply adaptive multiplier
            panoramaParticles.material.size = finalSize;
            panoramaParticles.material.needsUpdate = true;
        }
        
        // Reset colors
        if (panoramaParticles.geometry.attributes.color && panoramaParticles.geometry.userData.originalColors) {
            const colors = panoramaParticles.geometry.attributes.color.array;
            const originalColors = panoramaParticles.geometry.userData.originalColors;
            
            for (let i = 0; i < colors.length; i++) {
                colors[i] = originalColors[i];
            }
            
            panoramaParticles.geometry.attributes.color.needsUpdate = true;
        }
        
        // Reset positions
        if (panoramaParticles.geometry.attributes.position && panoramaParticles.geometry.userData.originalPositions) {
            const positions = panoramaParticles.geometry.attributes.position.array;
            const originalPositions = panoramaParticles.geometry.userData.originalPositions;
            
            for (let i = 0; i < positions.length; i++) {
                positions[i] = originalPositions[i];
            }
            
            panoramaParticles.geometry.attributes.position.needsUpdate = true;
        }
    }
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