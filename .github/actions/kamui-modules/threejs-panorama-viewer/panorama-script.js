// 360° Panorama Viewer - Depth-Enhanced Spherical Particle Distribution
// Uses shared components for camera, UI, audio, and mouse interaction
// Implements PLY loading with depth information from pointcloud-panorama-generation

// Global variables (panorama specific)
let panoramaParticles = null;
let panoramaTexture = null;
let lights = null;
let sphereRadius = 200;

// Panorama configuration - 360度パノラマ用に最適化
let particleSize = 3.5;
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
    
    // Calculate sphere bounds for camera adjustment
    geometry.computeBoundingSphere();
    if (geometry.boundingSphere) {
        sphereRadius = geometry.boundingSphere.radius;
        console.log(`📏 Detected sphere radius: ${sphereRadius.toFixed(2)}`);
        
        // Adjust camera constraints based on actual sphere size
        controls.maxDistance = sphereRadius - 20;
    }
    
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
    
    // Determine particle count based on density setting - 限界テスト用に100万粒子
    let particleCount;
    switch(particleDensity) {
        case 'low': particleCount = 200000; break;    // 限界テスト用にさらに増加
        case 'high': particleCount = 1000000; break;  // 限界テスト：100万粒子
        default: particleCount = 500000; // medium    // 限界テスト用にさらに増加
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

function animate() {
    requestAnimationFrame(animate);
    
    // Update camera controls (shared component)
    updateCameraControls();
    
    // Apply mouse gravity effect (shared component)
    if (panoramaParticles) {
        applyMouseGravity(panoramaParticles);
    }
    
    // Apply audio-reactive effects (shared component)
    if ((audioReactiveEnabled || microphoneEnabled) && panoramaParticles) {
        applyAudioReactiveEffects();
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
    window.updatePointSize(value, panoramaParticles);
}

function toggleBrightness() {
    window.toggleBrightness(scene, lights.ambientLight, lights.directionalLight, 'BACKGROUND_COLOR_PLACEHOLDER');
}

function updateGlowIntensity(value) {
    if (typeof window.updateGlowIntensity === 'function' && window.updateGlowIntensity !== updateGlowIntensity) {
        window.updateGlowIntensity(value, panoramaParticles);
    } else {
        // Fallback: direct particle material update
        if (panoramaParticles && panoramaParticles.material) {
            panoramaParticles.material.opacity = Math.max(0.1, Math.min(1.0, value));
            panoramaParticles.material.needsUpdate = true;
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
        window.resetParticlePositions(panoramaParticles);
        resetParticleColors(panoramaParticles);
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
    
    // Find music file in the page
    const musicFiles = ['assets/background-music.wav', 'assets/background-music.mp3'];
    
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
    if (typeof window.toggleAudioReactive === 'function') {
        window.toggleAudioReactive();
    } else {
        console.warn('🎵 Audio reactive system not available');
    }
}

function toggleMicrophone() {
    if (typeof window.toggleMicrophone === 'function') {
        window.toggleMicrophone();
    } else {
        console.warn('🎤 Microphone system not available');
    }
}

// Export music functions to global scope for HTML template
window.toggleMusic = toggleMusic;
window.toggleAudioReactive = toggleAudioReactive;
window.toggleMicrophone = toggleMicrophone;

if (typeof setupMusic !== 'undefined') {
    window.setupMusic = setupMusic;
}

// Start the panorama application
init();