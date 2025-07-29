// Refactored Point Cloud Viewer - Uses Shared Components
// Main script for PLY point cloud visualization with shared JS modules

// Global variables (point cloud specific)
let pointCloud = null;
let autoRotate = false;
let rotationSpeed = 1.0;
let lights = null;

// Initialize the viewer with shared components
function init() {
    console.log('🚀 Initializing Point Cloud Viewer with shared components');
    
    // Initialize camera system
    const containerElement = document.getElementById('container');
    const cameraData = initializeCameraSystem(containerElement, '#1a1a2e');
    
    // Store global references from camera system
    scene = cameraData.scene;
    camera = cameraData.camera;
    renderer = cameraData.renderer;
    controls = cameraData.controls;
    
    // Set initial camera position and auto-rotate settings
    setCameraPosition(0, 0, 100);
    setAutoRotateSettings(autoRotate, rotationSpeed);
    
    // Initialize UI system with lighting
    lights = initializeCompleteUISystem(scene, '#1a1a2e');
    
    // Initialize audio if available
    
    
    // Load PLY file
    loadPointCloud();
    
    // Debug info for rotation center
    console.log('OrbitControls initialized with autoRotate:', autoRotate);
    console.log('Rotation will be around Y-axis through controls.target');
    
    // Start animation loop
    animate();
    
    console.log('✅ Point Cloud Viewer initialization complete');
}

function loadPointCloud() {
    const loader = new THREE.PLYLoader();
    
    showLoadingIndicator('🔄 Loading point cloud...');
    
    loader.load('assets/pointcloud.ply', function(geometry) {
        geometry.computeBoundingBox();
        geometry.center();
        
        // Create particle system using shared component
        pointCloud = createParticleSystem(geometry, {
            size: pointSize,
            sizeAttenuation: true,
            transparent: true,
            opacity: 1.0
        });
        
        scene.add(pointCloud);
        
        // Auto-fit camera using shared function
        fitCameraToObject(pointCloud);
        
        // Initialize mouse interaction with the point cloud
        initializeMouseInteraction(pointCloud, camera);
        
        // Update UI
        updateStatsDisplay(pointCloud);
        hideLoadingIndicator();
        
        console.log('✅ Point cloud loaded:', geometry.attributes.position.count, 'points');
        console.log('Rotation center set to:', controls.target);
        console.log('Camera position:', camera.position);
    }, 
    function(progress) {
        updateLoadingProgress(progress);
    },
    function(error) {
        console.error('❌ Error loading PLY file:', error);
        showLoadingIndicator('❌ Failed to load point cloud');
    });
}

function animate() {
    requestAnimationFrame(animate);
    
    // Update camera controls (shared component)
    updateCameraControls();
    
    // Apply mouse gravity effect (shared component)
    if (pointCloud) {
        applyMouseGravity(pointCloud);
    }
    
    // Apply audio-reactive effects (shared component)
    if ((audioReactiveEnabled || microphoneEnabled) && pointCloud) {
        applyAudioReactiveEffects();
    }
    
    // Update particle system effects (shared component)
    if (pointCloud) {
        updateParticleSystem(pointCloud, camera, lights.ambientLight, lights.directionalLight);
    }
    
    // Render scene (shared component)
    renderScene();
}

// Point cloud specific control functions that integrate with shared components
function resetCamera() {
    if (pointCloud) {
        resetCameraToObject(pointCloud);
    } else {
        // Use shared reset function for default behavior
        window.resetCamera();
    }
}

function updatePointSize(value) {
    window.updatePointSize(value, pointCloud);
}

function toggleBrightness() {
    window.toggleBrightness(scene, lights.ambientLight, lights.directionalLight, '#1a1a2e');
}

function updateGlowIntensity(value) {
    window.updateGlowIntensity(value, pointCloud);
}

// Audio reactive integration
function resetToNormalState() {
    if (pointCloud && lights) {
        resetToNormalVisualState(pointCloud, lights.ambientLight, lights.directionalLight);
    }
    // Also reset audio system
    if (typeof resetToNormalAudioState === 'function') {
        resetToNormalAudioState();
    }
}

// Mouse interaction integration
function resetParticlePositions() {
    if (pointCloud) {
        window.resetParticlePositions(pointCloud);
        // Also reset colors
        resetParticleColors(pointCloud);
    }
}

// Music setup integration (called by template)


// Export functions to global scope for HTML events (integrate with shared components)
window.toggleAutoRotate = toggleAutoRotate;
window.resetCamera = resetCamera;
window.updatePointSize = updatePointSize;
window.updateRotationSpeed = updateRotationSpeed;
window.toggleBrightness = toggleBrightness;
window.updateGlowIntensity = updateGlowIntensity;

// Re-export shared component functions that might be called from HTML
window.toggleMouseGravity = window.toggleMouseGravity || (() => console.warn('Mouse gravity function not loaded'));
window.toggleGravityMode = window.toggleGravityMode || (() => console.warn('Gravity mode function not loaded'));
window.updateGravityRange = window.updateGravityRange || (() => console.warn('Gravity range function not loaded'));
window.updateGravityStrength = window.updateGravityStrength || (() => console.warn('Gravity strength function not loaded'));
window.updateWaveIntensity = window.updateWaveIntensity || (() => console.warn('Wave intensity function not loaded'));
window.toggleAudioReactive = window.toggleAudioReactive || (() => console.warn('Audio reactive function not loaded'));
window.toggleMicrophone = window.toggleMicrophone || (() => console.warn('Microphone function not loaded'));
window.toggleAudioMode = window.toggleAudioMode || (() => console.warn('Audio mode function not loaded'));
window.toggleDynamicMode = window.toggleDynamicMode || (() => console.warn('Dynamic mode function not loaded'));



// Start the application
init();