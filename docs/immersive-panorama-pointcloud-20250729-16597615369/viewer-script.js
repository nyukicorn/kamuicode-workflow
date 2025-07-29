// Refactored Point Cloud Viewer - Uses Shared Components
// Main script for PLY point cloud visualization with shared JS modules

// Global variables (point cloud specific)
let pointCloud = null;
let viewerAutoRotate = false;
// rotationSpeed is managed by shared-components/camera-controls.js
let lights = null;

// Initialize the viewer with shared components
function init() {
    console.log('🚀 Initializing Point Cloud Viewer with shared components');
    
    // Initialize camera system
    const containerElement = document.getElementById('container');
    const cameraData = initializeCameraSystem(containerElement, '#0a0a2a');
    
    // Store global references from camera system
    scene = cameraData.scene;
    camera = cameraData.camera;
    renderer = cameraData.renderer;
    controls = cameraData.controls;
    
    // Set initial camera position and auto-rotate settings
    setCameraPosition(0, 0, 50);
    setAutoRotateSettings(viewerAutoRotate, 0.8);
    
    // Initialize UI system with lighting
    lights = initializeCompleteUISystem(scene, '#0a0a2a');
    
    // Initialize audio if available
    setupMusic();
    
    // Load PLY file
    loadPointCloud();
    
    // Debug info for rotation center
    console.log('OrbitControls initialized with autoRotate:', viewerAutoRotate);
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
    // Call UI controls implementation to avoid recursion
    if (window.updatePointSizeImpl) {
        window.updatePointSizeImpl(value, pointCloud);
    } else {
        console.warn('updatePointSizeImpl not loaded');
    }
}

function toggleBrightness() {
    window.toggleBrightness(scene, lights.ambientLight, lights.directionalLight, '#0a0a2a');
}

function updateGlowIntensity(value) {
    // Call UI controls implementation to avoid recursion
    if (window.updateGlowIntensityImpl) {
        window.updateGlowIntensityImpl(value, pointCloud);
    } else {
        console.warn('updateGlowIntensityImpl not loaded');
    }
}

// Audio reactive integration
function resetToNormalState() {
    if (pointCloud && lights) {
        resetToNormalVisualState(pointCloud, lights.ambientLight, lights.directionalLight);
    }
    // Also reset audio system
    if (typeof resetAudioToNormalState === 'function') {
        resetAudioToNormalState();
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
function setupMusic() {
    const playButton = document.getElementById('musicToggle');
    let audio = null;
    
    playButton.addEventListener('click', () => {
        if (!audio) {
            audio = new Audio('assets/generated-music.wav');
            audioElement = audio; // Set global reference
            audio.loop = true;
            audio.volume = 0.7;
            audio.crossOrigin = 'anonymous';
            
            // Enhanced error handling
            audio.addEventListener('error', (e) => {
                console.error('Audio loading error:', e);
                console.error('Audio src:', audio.src);
                console.error('Audio error:', audio.error);
                playButton.textContent = '❌ No Music File';
            });
            
            audio.addEventListener('loadeddata', () => {
                console.log('Audio loaded successfully from:', audio.src);
            });
        }
        
        if (audio.paused) {
            audio.play().then(() => {
                playButton.textContent = '🎵 Music ON';
                playButton.classList.add('playing');
                // Setup audio analysis for music
                setupMusicAnalysis(audio);
                musicPlaying = true;
            }).catch(error => {
                console.error('Music playback error:', error);
                console.error('Error name:', error.name);
                console.error('Error message:', error.message);
                if (error.name === 'NotAllowedError') {
                    playButton.textContent = '⚠️ Click First';
                } else {
                    playButton.textContent = '❌ No Music File';
                }
            });
        } else {
            audio.pause();
            playButton.textContent = '🎵 Music OFF';
            playButton.classList.remove('playing');
            musicPlaying = false;
        }
    });
}

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