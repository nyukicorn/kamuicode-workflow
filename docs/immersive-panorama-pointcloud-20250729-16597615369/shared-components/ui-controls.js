// UI Controls System for Three.js Viewers
// Shared component for control panel management and UI interactions

// UI control variables
let pointSize = 1.5;
let brightnessLevel = 0.2;  // Default brightness level (dim, so button shows "bright")
let glowIntensity = 0.0;    // Default no glow

// Modern control panel auto-hide system (YouTube/Netflix style)
function setupControlsAutoHide() {
    const controls = document.getElementById('controls');
    if (!controls) {
        console.warn('⚠️ Controls element not found - auto-hide will not work');
        return;
    }
    
    let hideTimeout;
    let isUserActive = true;
    
    // Show controls immediately on any user activity
    const showControlsOnActivity = () => {
        if (!isUserActive) {
            controls.classList.add('visible');
            isUserActive = true;
        }
        
        // Reset hide timer
        clearTimeout(hideTimeout);
        hideTimeout = setTimeout(() => {
            controls.classList.remove('visible');
            isUserActive = false;
        }, 4000); // Hide after 4 seconds of inactivity
    };
    
    // Monitor various user activities
    document.addEventListener('mousemove', showControlsOnActivity);
    document.addEventListener('mousedown', showControlsOnActivity);
    document.addEventListener('keydown', showControlsOnActivity);
    document.addEventListener('scroll', showControlsOnActivity);
    document.addEventListener('touchstart', showControlsOnActivity);
    document.addEventListener('touchmove', showControlsOnActivity);
    
    // Keep controls visible when hovering over them
    controls.addEventListener('mouseenter', () => {
        clearTimeout(hideTimeout);
        controls.classList.add('visible');
        isUserActive = true;
    });
    
    controls.addEventListener('mouseleave', () => {
        // Restart hide timer when leaving controls
        showControlsOnActivity();
    });
    
    // Initial state: show controls, then auto-hide after 5 seconds
    controls.classList.add('visible');
    hideTimeout = setTimeout(() => {
        controls.classList.remove('visible');
        isUserActive = false;
    }, 5000);
    
    console.log('🎛️ Modern auto-hide system initialized (YouTube/Netflix style)');
}

// Point size control
function updatePointSize(value, pointCloudObject) {
    pointSize = parseFloat(value);
    if (pointCloudObject && pointCloudObject.material) {
        pointCloudObject.material.size = pointSize;
        console.log(`📏 Point size updated to: ${pointSize}`);
    }
}

// Brightness control
function toggleBrightness(sceneObject, ambientLightObject, directionalLightObject, backgroundColorHex = '#1a1a1a') {
    const button = document.getElementById('brightnessToggle');
    
    // Enhanced brightness toggle with background change
    if (brightnessLevel <= 0.5) {
        // Make it bright - much brighter lighting + lighter background
        brightnessLevel = 1.2;
        if (sceneObject) {
            sceneObject.background = new THREE.Color('#404040'); // Dark gray instead of black
        }
        if (button) {
            button.innerHTML = '☀️ Light Mode ON';
            button.title = 'Currently in light mode (click to switch to dark)';
        }
    } else {
        // Make it dim - keep original dark appearance
        brightnessLevel = 0.3;
        if (sceneObject) {
            sceneObject.background = new THREE.Color(backgroundColorHex);
        }
        if (button) {
            button.innerHTML = '🌙 Dark Mode ON';
            button.title = 'Currently in dark mode (click to switch to light)';
        }
    }
    
    // Apply enhanced brightness change
    if (ambientLightObject) {
        ambientLightObject.intensity = brightnessLevel;
    }
    if (directionalLightObject) {
        directionalLightObject.intensity = brightnessLevel * 1.8; // More dramatic difference
    }
    
    console.log(`💡 Brightness toggled to: ${brightnessLevel > 0.5 ? 'Light' : 'Dark'} mode`);
}

// Glow intensity control
function updateGlowIntensity(value, pointCloudObject) {
    glowIntensity = parseFloat(value) / 100.0; // 0-100% to 0-1.0
    
    if (pointCloudObject && pointCloudObject.material) {
        // Create glow effect by making colors brighter and slightly larger
        const geometry = pointCloudObject.geometry;
        if (geometry.attributes.color) {
            const colors = geometry.attributes.color.array;
            const originalColors = pointCloudObject.userData.originalColors;
            
            // Store original colors if not already stored
            if (!originalColors) {
                pointCloudObject.userData.originalColors = new Float32Array(colors);
            }
            
            // Apply glow brightness
            const glowBrightness = 1.0 + glowIntensity * 3.0; // Up to 4.0x brightness
            for (let i = 0; i < colors.length; i++) {
                colors[i] = Math.min(1.0, pointCloudObject.userData.originalColors[i] * glowBrightness);
            }
            
            geometry.attributes.color.needsUpdate = true;
        }
        
        // Also slightly increase size for extra glow effect
        const sizeMultiplier = 1.0 + glowIntensity * 0.8; // Up to 80% size increase
        pointCloudObject.material.size = pointSize * sizeMultiplier;
        pointCloudObject.material.needsUpdate = true;
    }
    
    console.log(`✨ Glow intensity updated to: ${Math.round(glowIntensity * 100)}%`);
}

// Initialize UI system with lighting setup
function initializeUISystem(sceneObject, backgroundColorHex = '#1a1a1a') {
    // Lighting setup (use default brightness level)
    const ambientLight = new THREE.AmbientLight(0xffffff, brightnessLevel);
    sceneObject.add(ambientLight);
    
    // Additional lighting (directional light)
    const directionalLight = new THREE.DirectionalLight(0xffffff, brightnessLevel * 1.5);
    directionalLight.position.set(1, 1, 1);
    sceneObject.add(directionalLight);
    
    // Setup control panel auto-hide
    setupControlsAutoHide();
    
    console.log('🎛️ UI system initialized with lighting');
    
    return { ambientLight, directionalLight };
}

// Initialize button states
function initializeButtonStates() {
    // Initialize brightness button
    const brightnessButton = document.getElementById('brightnessToggle');
    if (brightnessButton) {
        brightnessButton.innerHTML = '🌙 Dark Mode ON';
        brightnessButton.title = 'Currently in dark mode (click to switch to light)';
    }
    
    // Initialize other button states
    const gravityButton = document.getElementById('gravityToggle');
    if (gravityButton) {
        gravityButton.innerHTML = '🚫 Gravity OFF';
        gravityButton.title = 'Gravity is OFF (click to enable)';
    }
    
    const audioButton = document.getElementById('audioReactiveToggle');
    if (audioButton) {
        audioButton.innerHTML = '🔇 Audio React OFF';
        audioButton.title = 'Audio reactive is OFF (click to enable)';
    }
    
    const micButton = document.getElementById('microphoneToggle');
    if (micButton) {
        micButton.innerHTML = '🎙️ Mic OFF';
        micButton.title = 'Microphone is OFF (click to enable)';
    }
    
    const audioModeButton = document.getElementById('audioModeToggle');
    if (audioModeButton) {
        audioModeButton.innerHTML = '🎵 Music Mode ON';
        audioModeButton.title = 'Currently in music mode (bass/mid/treble separation)';
    }
    
    const dynamicButton = document.getElementById('dynamicModeToggle');
    if (dynamicButton) {
        dynamicButton.innerHTML = '🚀 Dynamic OFF';
        dynamicButton.title = 'Dynamic enhancement is OFF';
    }
    
    console.log('🔘 Button states initialized');
}

// Update slider displays
function updateSliderDisplays() {
    // Point size slider
    const pointSizeSlider = document.getElementById('pointSizeSlider');
    const pointSizeValue = document.getElementById('pointSizeValue');
    if (pointSizeSlider && pointSizeValue) {
        pointSizeSlider.value = pointSize;
        pointSizeValue.textContent = pointSize.toFixed(1);
    }
    
    // Brightness/glow slider
    const glowSlider = document.getElementById('glowSlider');
    const glowValue = document.getElementById('glowValue');
    if (glowSlider && glowValue) {
        glowSlider.value = Math.round(glowIntensity * 100);
        glowValue.textContent = Math.round(glowIntensity * 100);
    }
    
    // Gravity sliders
    const gravityRangeSlider = document.getElementById('gravityRangeSlider');
    const gravityRangeValue = document.getElementById('gravityRangeValue');
    if (gravityRangeSlider && gravityRangeValue && typeof gravityRange !== 'undefined') {
        gravityRangeSlider.value = gravityRange;
        gravityRangeValue.textContent = gravityRange;
    }
    
    const gravityStrengthSlider = document.getElementById('gravityStrengthSlider');
    const gravityStrengthValue = document.getElementById('gravityStrengthValue');
    if (gravityStrengthSlider && gravityStrengthValue && typeof gravityStrength !== 'undefined') {
        gravityStrengthSlider.value = Math.round(gravityStrength * 100);
        gravityStrengthValue.textContent = Math.round(gravityStrength * 100);
    }
    
    console.log('🎚️ Slider displays updated');
}

// Update statistics display
function updateStatsDisplay(pointCloudObject) {
    const statsElement = document.getElementById('stats');
    if (statsElement && pointCloudObject) {
        const pointCount = pointCloudObject.geometry.attributes.position.count;
        statsElement.textContent = `Points: ${pointCount.toLocaleString()}`;
    }
}

// Hide loading indicator
function hideLoadingIndicator() {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

// Show loading indicator with custom text
function showLoadingIndicator(text = '🔄 Loading...') {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.textContent = text;
        loadingElement.style.display = 'block';
    }
}

// Update loading progress
function updateLoadingProgress(progress) {
    const percent = Math.round((progress.loaded / progress.total) * 100);
    showLoadingIndicator(`🔄 Loading: ${percent}%`);
}

// Setup responsive UI for mobile devices
function setupResponsiveUI() {
    const controls = document.getElementById('controls');
    if (!controls) return;
    
    // Add touch support for mobile
    if ('ontouchstart' in window) {
        controls.addEventListener('touchstart', () => {
            controls.classList.add('visible');
        });
        
        // Hide after longer delay on mobile
        let mobileHideTimeout;
        controls.addEventListener('touchend', () => {
            clearTimeout(mobileHideTimeout);
            mobileHideTimeout = setTimeout(() => {
                controls.classList.remove('visible');
            }, 5000); // 5 seconds on mobile
        });
    }
    
    console.log('📱 Responsive UI setup complete');
}

// Create info panel for debugging
function createInfoPanel() {
    const existingInfo = document.getElementById('info');
    if (existingInfo) return existingInfo;
    
    const infoPanel = document.createElement('div');
    infoPanel.id = 'info';
    infoPanel.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        max-width: 250px;
        z-index: 1000;
        display: none;
    `;
    
    document.body.appendChild(infoPanel);
    return infoPanel;
}

// Toggle info panel visibility
function toggleInfoPanel() {
    const infoPanel = document.getElementById('info');
    if (infoPanel) {
        infoPanel.style.display = infoPanel.style.display === 'none' ? 'block' : 'none';
    }
}

// Add keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (event) => {
        // Only handle shortcuts if not typing in an input
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }
        
        switch(event.key.toLowerCase()) {
            case 'g':
                if (typeof toggleMouseGravity === 'function') {
                    toggleMouseGravity();
                }
                break;
            case 'b':
                if (typeof toggleBrightness === 'function') {
                    toggleBrightness();
                }
                break;
            case 'a':
                if (typeof toggleAudioReactive === 'function') {
                    toggleAudioReactive();
                }
                break;
            case 'm':
                if (typeof toggleMicrophone === 'function') {
                    toggleMicrophone();
                }
                break;
            case 'r':
                if (typeof resetCamera === 'function') {
                    resetCamera();
                }
                break;
            case 'i':
                toggleInfoPanel();
                break;
            case 'h':
                // Show help
                alert('Keyboard shortcuts:\nG - Toggle gravity\nB - Toggle brightness\nA - Toggle audio reactive\nM - Toggle microphone\nR - Reset camera\nI - Toggle info panel');
                break;
        }
    });
    
    console.log('⌨️ Keyboard shortcuts initialized (H for help)');
}

// Initialize complete UI system
function initializeCompleteUISystem(sceneObject, backgroundColorHex = '#1a1a1a') {
    const lights = initializeUISystem(sceneObject, backgroundColorHex);
    initializeButtonStates();
    updateSliderDisplays();
    setupResponsiveUI();
    setupKeyboardShortcuts();
    createInfoPanel();
    
    console.log('🎛️ Complete UI system initialized');
    return lights;
}

// Export functions to global scope for HTML events
window.updatePointSize = updatePointSize;
window.updatePointSizeImpl = updatePointSize;  // Alias for viewer compatibility
window.toggleBrightness = toggleBrightness;
window.updateGlowIntensity = updateGlowIntensity;
window.updateGlowIntensityImpl = updateGlowIntensity;  // Alias for viewer compatibility