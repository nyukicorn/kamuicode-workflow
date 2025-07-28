// 360° Panorama Viewer - Spherical Particle Distribution
// Uses shared components for camera, UI, audio, and mouse interaction
// Implements plane segmentation → spherical particle placement approach

// Global variables (panorama specific)
let panoramaParticles = null;
let panoramaTexture = null;
let lights = null;
let sphereRadius = 200;

// Panorama configuration
let particleSize = 2.0;
let autoRotate = AUTO_ROTATE_PLACEHOLDER;
let rotationSpeed = ROTATION_SPEED_PLACEHOLDER;
let particleDensity = 'PARTICLE_DENSITY_PLACEHOLDER'; // low/medium/high

// Initialize the panorama viewer with shared components
function init() {
    console.log('🌐 Initializing 360° Panorama Viewer with shared components');
    
    // Initialize camera system
    const containerElement = document.getElementById('container');
    const cameraData = initializeCameraSystem(containerElement, 'BACKGROUND_COLOR_PLACEHOLDER');
    
    // Store global references from camera system
    scene = cameraData.scene;
    camera = cameraData.camera;
    renderer = cameraData.renderer;
    controls = cameraData.controls;
    
    // Set initial camera position (inside the sphere)
    const initialRadius = CAM_RADIUS_PLACEHOLDER;
    setCameraPosition(0, 0, 0); // Center of the sphere
    
    // Configure controls for panoramic experience
    controls.enablePan = false; // Disable panning for true panoramic experience
    controls.minDistance = 5;   // Minimum zoom in
    controls.maxDistance = initialRadius - 20; // Maximum zoom out (stay inside sphere)
    
    // Set auto-rotate settings
    setAutoRotateSettings(autoRotate, rotationSpeed);
    
    // Initialize UI system with lighting
    lights = initializeCompleteUISystem(scene, 'BACKGROUND_COLOR_PLACEHOLDER');
    
    // Initialize audio if available
    MUSIC_INIT_PLACEHOLDER
    
    // Load panorama image and create spherical particle distribution
    loadPanoramaImage();
    
    console.log('OrbitControls configured for panoramic viewing');
    console.log('Camera positioned at center, looking outward');
    
    // Start animation loop
    animate();
    
    console.log('✅ 360° Panorama Viewer initialization complete');
}

function loadPanoramaImage() {
    showLoadingIndicator('🖼️ Loading panorama image...');
    
    const loader = new THREE.TextureLoader();
    
    loader.load('assets/panorama-image.jpg', 
        function(texture) {
            console.log('✅ Panorama texture loaded');
            panoramaTexture = texture;
            
            // Create spherical particle distribution from image
            createSphericalParticleSystem();
        },
        function(progress) {
            const percent = Math.round((progress.loaded / progress.total) * 100);
            updateLoadingProgress(`Loading panorama: ${percent}%`);
        },
        function(error) {
            console.error('❌ Error loading panorama image:', error);
            showLoadingIndicator('❌ Failed to load panorama image');
            
            // Create test spherical pattern as fallback
            createTestSphericalPattern();
        }
    );
}

function createSphericalParticleSystem() {
    console.log('🌐 Creating spherical particle system from image...');
    
    // Determine particle count based on density setting
    let particleCount;
    switch(particleDensity) {
        case 'low': particleCount = 10000; break;
        case 'high': particleCount = 50000; break;
        default: particleCount = 25000; // medium
    }
    
    showLoadingIndicator(`🌐 Generating ${particleCount.toLocaleString()} particles...`);
    
    // Create canvas to analyze image pixels
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = panoramaTexture.image;
    
    // Set canvas size for analysis (balance between detail and performance)
    const analysisWidth = 400;
    const analysisHeight = 200;
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
    
    // Generate particles using spherical coordinates
    for (let i = 0; i < particleCount && particleIndex < particleCount; i++) {
        // Generate uniform distribution on sphere using rejection sampling
        const u = Math.random();
        const v = Math.random();
        
        // Convert to spherical coordinates (phi: 0 to 2π, theta: 0 to π)
        const phi = u * 2 * Math.PI;          // Longitude (0 to 2π)
        const theta = Math.acos(2 * v - 1);   // Latitude (0 to π) - uniform distribution
        
        // Convert spherical to Cartesian coordinates
        const x = sphereRadius * Math.sin(theta) * Math.cos(phi);
        const y = sphereRadius * Math.cos(theta);
        const z = sphereRadius * Math.sin(theta) * Math.sin(phi);
        
        // Map spherical coordinates to image coordinates
        const imageX = Math.floor((phi / (2 * Math.PI)) * analysisWidth);
        const imageY = Math.floor((theta / Math.PI) * analysisHeight);
        
        // Get pixel color from image
        const pixelIndex = (imageY * analysisWidth + imageX) * 4;
        const r = pixels[pixelIndex] / 255;
        const g = pixels[pixelIndex + 1] / 255;
        const b = pixels[pixelIndex + 2] / 255;
        const alpha = pixels[pixelIndex + 3] / 255;
        
        // Skip nearly transparent pixels to create interesting patterns
        if (alpha < 0.1) continue;
        
        // Add some brightness enhancement for better visibility
        const brightness = (r + g + b) / 3;
        const enhancementFactor = 1.2 + brightness * 0.5;
        
        // Store position
        positions[particleIndex * 3] = x;
        positions[particleIndex * 3 + 1] = y;
        positions[particleIndex * 3 + 2] = z;
        
        // Store enhanced color
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
    
    // Create test pattern with multiple colored bands
    for (let i = 0; i < particleCount; i++) {
        // Uniform distribution on sphere
        const u = Math.random();
        const v = Math.random();
        
        const phi = u * 2 * Math.PI;
        const theta = Math.acos(2 * v - 1);
        
        const x = sphereRadius * Math.sin(theta) * Math.cos(phi);
        const y = sphereRadius * Math.cos(theta);
        const z = sphereRadius * Math.sin(theta) * Math.sin(phi);
        
        positions[i * 3] = x;
        positions[i * 3 + 1] = y;
        positions[i * 3 + 2] = z;
        
        // Create colored bands based on latitude
        const latitudeBand = Math.floor((theta / Math.PI) * 6);
        switch(latitudeBand) {
            case 0: // Top
                colors[i * 3] = 1.0; colors[i * 3 + 1] = 0.3; colors[i * 3 + 2] = 0.3;
                break;
            case 1:
                colors[i * 3] = 1.0; colors[i * 3 + 1] = 0.7; colors[i * 3 + 2] = 0.3;
                break;
            case 2:
                colors[i * 3] = 0.3; colors[i * 3 + 1] = 1.0; colors[i * 3 + 2] = 0.3;
                break;
            case 3:
                colors[i * 3] = 0.3; colors[i * 3 + 1] = 0.7; colors[i * 3 + 2] = 1.0;
                break;
            case 4:
                colors[i * 3] = 0.7; colors[i * 3 + 1] = 0.3; colors[i * 3 + 2] = 1.0;
                break;
            default: // Bottom
                colors[i * 3] = 1.0; colors[i * 3 + 1] = 0.3; colors[i * 3 + 2] = 0.7;
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
    
    console.log('✅ Test spherical pattern created');
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
    window.updateGlowIntensity(value, panoramaParticles);
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

// Music setup integration (called by template)
MUSIC_FUNCTIONS_PLACEHOLDER

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

MUSIC_WINDOW_PLACEHOLDER

// Start the panorama application
init();