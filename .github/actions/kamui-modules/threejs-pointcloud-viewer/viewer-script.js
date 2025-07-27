// Global variables
let scene, camera, renderer, controls;
let pointCloud = null;
let autoRotate = AUTO_ROTATE_PLACEHOLDER;
let rotationSpeed = ANIMATION_SPEED_PLACEHOLDER;
let pointSize = 1.5;
let audioElement = null;
let musicPlaying = false;

// Audio analysis variables
let audioContext = null;
let microphoneSource = null;
let musicAnalyser = null;
let micAnalyser = null;
let musicDataArray = null;
let micDataArray = null;
let audioReactiveEnabled = false;
let microphoneEnabled = false;
let currentVolumeLevel = 0;
let volumeSmoothing = 0.3; // Improved responsiveness (was 0.8)

// Frequency band analysis with enhanced settings
let frequencyBands = {
    bass: 0,      // 60-250Hz (adjusted for better bass detection)
    mid: 0,       // 250-2000Hz
    treble: 0     // 2000-8000Hz (extended for better clarity)
};
let audioMode = 'music'; // 'music' or 'voice'
let dynamicModeEnabled = false; // Independent dynamic mode toggle

// Enhanced audio analysis system
let adaptiveSystem = {
    // Dynamic thresholds based on audio history
    frequencyThresholds: {
        bass: 0.08,   // Lowered for better microphone sensitivity
        mid: 0.06,    // Lowered for better microphone sensitivity  
        treble: 0.04  // Lowered for better microphone sensitivity
    },
    volumeThreshold: 0.08, // Lowered for better microphone sensitivity
    // Human auditory perception weights
    perceptualWeight: { 
        bass: 0.8,   // Lower weight as humans are less sensitive to bass
        mid: 1.2,    // Higher weight for speech/melody range
        treble: 1.0  // Standard weight
    },
    // Audio history for adaptive thresholds
    history: {
        bass: [],
        mid: [], 
        treble: [],
        volume: [],
        maxHistoryLength: 120 // 2 seconds at 60fps
    }
};

// Effect decay system for natural fade-out
let effectDecay = {
    size: 0.95,       // 5% decay per frame
    brightness: 0.92, // 8% decay per frame  
    color: 0.90,      // 10% decay per frame
    movement: 0.88    // 12% decay per frame
};

// Current effect intensities for decay tracking
let currentEffects = {
    sizeMultiplier: 1.0,
    brightnessMultiplier: 1.0,
    colorIntensity: 1.0,
    movementIntensity: 0.0
};

// Lighting and appearance
let ambientLight, directionalLight, brightnessLevel, glowIntensity;  // Declare without initialization

// Initialize appearance variables
ambientLight = null;  // Initialize to avoid TDZ
directionalLight = null;  // Initialize to avoid TDZ
brightnessLevel = 0.2;  // Default brightness level (dim, so button shows "bright")
glowIntensity = 0.0;  // Default no glow

// Mouse interaction variables
let mousePosition = new THREE.Vector2();
let mouseWorldPosition = new THREE.Vector3();
let originalPositions = null;
let mouseGravityEnabled = false;  // Default OFF for cleaner initial experience
let gravityStrength = 0.3;  // Increased default strength for bigger movement
let gravityRange = 100;     // Default range
let waveIntensity = 0.0;    // Disable wave by default for better performance
let particleVelocities = null; // Store particle velocities for wave effect

// Gravity mode variables
let gravityMode = 'circle';  // 'circle', 'flow', or 'magnet'
let mouseTrail = [];         // Store recent mouse positions for flow mode
const MAX_TRAIL_LENGTH = 15; // Number of positions to remember
const MIN_MAGNET_DISTANCE = 8; // Minimum distance for magnet mode (particles within this don't move)

// Initialize the viewer
function init() {
    // Scene setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color('BACKGROUND_COLOR_PLACEHOLDER');
    
    // Lighting setup (use default brightness level)
    ambientLight = new THREE.AmbientLight(0xffffff, brightnessLevel);
    scene.add(ambientLight);
    
    // Camera setup
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
    camera.position.set(CAM_X_PLACEHOLDER, CAM_Y_PLACEHOLDER, CAM_Z_PLACEHOLDER);
    
    // Renderer setup
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    document.getElementById('container').appendChild(renderer.domElement);
    
    // Controls setup
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = autoRotate;
    controls.autoRotateSpeed = rotationSpeed;
    
    // Lock vertical rotation to prevent flipping
    controls.minPolarAngle = 0; // 0 degrees
    controls.maxPolarAngle = Math.PI; // 180 degrees
    
    // Ensure zoom is always enabled
    controls.enableZoom = true;
    controls.enablePan = true;
    controls.enableRotate = true;
    
    // Additional lighting (directional light)
    directionalLight = new THREE.DirectionalLight(0xffffff, brightnessLevel * 1.5);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // Initialize audio if available
    MUSIC_INIT_PLACEHOLDER
    
    // Load PLY file
    loadPointCloud();
    
    // Debug info for rotation center
    console.log('OrbitControls initialized with autoRotate:', autoRotate);
    console.log('Rotation will be around Y-axis through controls.target');
    
    // Start animation loop
    animate();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Keyboard controls
    document.addEventListener('keydown', onKeyDown);
    
    // Double-click to toggle rotation (don't prevent default to preserve zoom)
    renderer.domElement.addEventListener('dblclick', (event) => {
        // Don't prevent default - let OrbitControls handle zoom
        toggleAutoRotate();
    });
    
    // Setup control panel auto-hide
    setupControlsAutoHide();
    
    // Setup mouse interaction
    setupMouseInteraction();
}

function loadPointCloud() {
    const loader = new THREE.PLYLoader();
    
    loader.load('assets/PLY_FILENAME_PLACEHOLDER', function(geometry) {
        geometry.computeBoundingBox();
        geometry.center();
        
        // Enhance 3D appearance with depth-based effects
        enhance3DAppearance(geometry);
        
        // Create point cloud material
        const material = new THREE.PointsMaterial({
            vertexColors: true,
            size: pointSize,
            sizeAttenuation: true,
            transparent: true,  // Enable transparency for depth effects
            opacity: 1.0
        });
        
        // Create point cloud
        pointCloud = new THREE.Points(geometry, material);
        scene.add(pointCloud);
        
        // Update info
        const pointCount = geometry.attributes.position.count;
        document.getElementById('stats').textContent = `Points: ${pointCount.toLocaleString()}`;
        document.getElementById('loading').style.display = 'none';
        
        // Auto-fit camera
        fitCameraToObject(pointCloud);
        
        // Store original positions for mouse interaction
        storeOriginalPositions();
        
        console.log('✅ Point cloud loaded:', pointCount, 'points');
        console.log('Rotation center set to:', controls.target);
        console.log('Camera position:', camera.position);
    }, 
    function(progress) {
        const percent = Math.round((progress.loaded / progress.total) * 100);
        document.getElementById('loading').textContent = `🔄 Loading: ${percent}%`;
    },
    function(error) {
        console.error('❌ Error loading PLY file:', error);
        document.getElementById('loading').textContent = '❌ Failed to load point cloud';
    });
}

function fitCameraToObject(object) {
    const box = new THREE.Box3().setFromObject(object);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    
    const maxSize = Math.max(size.x, size.y, size.z);
    const fitHeightDistance = maxSize / (2 * Math.atan(Math.PI * camera.fov / 360));
    const fitWidthDistance = fitHeightDistance / camera.aspect;
    const distance = Math.max(fitHeightDistance, fitWidthDistance) * 1.5;
    
    camera.near = distance / 100;
    camera.far = distance * 100;
    camera.updateProjectionMatrix();
    
    controls.target.copy(center);
    controls.update();
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    
    // Apply mouse gravity effect
    if (mouseGravityEnabled && pointCloud && originalPositions) {
        applyMouseGravity();
    }
    
    // Apply audio-reactive effects
    if ((audioReactiveEnabled || microphoneEnabled) && pointCloud) {
        applyAudioReactiveEffects();
    }
    
    renderer.render(scene, camera);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function onKeyDown(event) {
    const moveSpeed = 10;
    switch(event.code) {
        case 'KeyW':
            camera.position.add(camera.getWorldDirection(new THREE.Vector3()).multiplyScalar(moveSpeed));
            break;
        case 'KeyS':
            camera.position.add(camera.getWorldDirection(new THREE.Vector3()).multiplyScalar(-moveSpeed));
            break;
        case 'KeyA':
            camera.position.add(new THREE.Vector3().crossVectors(camera.up, camera.getWorldDirection(new THREE.Vector3())).multiplyScalar(moveSpeed));
            break;
        case 'KeyD':
            camera.position.add(new THREE.Vector3().crossVectors(camera.getWorldDirection(new THREE.Vector3()), camera.up).multiplyScalar(moveSpeed));
            break;
    }
}

// Control functions
function toggleAutoRotate() {
    autoRotate = !autoRotate;
    controls.autoRotate = autoRotate;
}

function resetCamera() {
    if (pointCloud) {
        fitCameraToObject(pointCloud);
        // Ensure rotation is around the object center
        const box = new THREE.Box3().setFromObject(pointCloud);
        const center = box.getCenter(new THREE.Vector3());
        controls.target.copy(center);
        controls.update();
    }
}

function updatePointSize(value) {
    pointSize = parseFloat(value);
    if (pointCloud) {
        pointCloud.material.size = pointSize;
    }
}

function updateRotationSpeed(value) {
    rotationSpeed = parseFloat(value);
    controls.autoRotateSpeed = rotationSpeed;
}

function toggleBrightness() {
    const button = document.getElementById('brightnessToggle');
    
    // Enhanced brightness toggle with background change
    if (brightnessLevel <= 0.5) {
        // Make it bright - much brighter lighting + lighter background
        brightnessLevel = 1.2;
        scene.background = new THREE.Color('#404040'); // Dark gray instead of black
        button.innerHTML = '☀️ Light Mode ON';
        button.title = 'Currently in light mode (click to switch to dark)';
    } else {
        // Make it dim - keep original dark appearance
        brightnessLevel = 0.3;
        scene.background = new THREE.Color('BACKGROUND_COLOR_PLACEHOLDER');
        button.innerHTML = '🌙 Dark Mode ON';
        button.title = 'Currently in dark mode (click to switch to light)';
    }
    
    // Apply enhanced brightness change
    ambientLight.intensity = brightnessLevel;
    directionalLight.intensity = brightnessLevel * 1.8; // More dramatic difference
}

function updateGlowIntensity(value) {
    glowIntensity = parseFloat(value) / 100.0; // 0-100% to 0-1.0
    
    if (pointCloud && pointCloud.material) {
        // Create glow effect by making colors brighter and slightly larger
        const geometry = pointCloud.geometry;
        if (geometry.attributes.color) {
            const colors = geometry.attributes.color.array;
            const originalColors = pointCloud.userData.originalColors;
            
            // Store original colors if not already stored
            if (!originalColors) {
                pointCloud.userData.originalColors = new Float32Array(colors);
            }
            
            // Apply glow brightness
            const glowBrightness = 1.0 + glowIntensity * 1.5; // Up to 2.5x brightness
            for (let i = 0; i < colors.length; i++) {
                colors[i] = Math.min(1.0, pointCloud.userData.originalColors[i] * glowBrightness);
            }
            
            geometry.attributes.color.needsUpdate = true;
        }
        
        // Also slightly increase size for extra glow effect
        const sizeMultiplier = 1.0 + glowIntensity * 0.3; // Up to 30% size increase
        pointCloud.material.size = pointSize * sizeMultiplier;
        pointCloud.material.needsUpdate = true;
    }
}

function setupControlsAutoHide() {
    const controls = document.getElementById('controls');
    let hideTimeout;
    
    // Show controls when mouse enters the left side of screen or controls
    const showControls = () => {
        controls.classList.add('visible');
        clearTimeout(hideTimeout);
    };
    
    // Hide controls after a delay
    const scheduleHide = () => {
        clearTimeout(hideTimeout);
        hideTimeout = setTimeout(() => {
            controls.classList.remove('visible');
        }, 3000); // Hide after 3 seconds
    };
    
    // Show when hovering over controls
    controls.addEventListener('mouseenter', showControls);
    controls.addEventListener('mouseleave', scheduleHide);
    
    // Initial hide after 5 seconds
    setTimeout(() => {
        scheduleHide();
    }, 5000);
}

function setupMouseInteraction() {
    const controls = document.getElementById('controls');
    
    // Track mouse position for 3D interaction
    document.addEventListener('mousemove', (event) => {
        // Handle control visibility
        if (event.clientX < 300) {
            controls.classList.add('visible');
        }
        
        // Normalize mouse coordinates to [-1, 1]
        mousePosition.x = (event.clientX / window.innerWidth) * 2 - 1;
        mousePosition.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        // Convert to world coordinates
        updateMouseWorldPosition();
        
        // Update mouse trail for flow mode
        if (gravityMode === 'flow') {
            updateMouseTrail();
        }
        
        // Debug log occasionally
        if (Math.random() < 0.01) {
            const modeIcon = gravityMode === 'flow' ? '🌊' : gravityMode === 'magnet' ? '🧲' : '🎯';
            console.log(`${modeIcon} Mouse: screen(${event.clientX}, ${event.clientY}) mode: ${gravityMode}`);
        }
    });
}

function updateMouseWorldPosition() {
    if (!camera || !pointCloud) return;
    
    // Create a raycaster to get 3D mouse position
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(mousePosition, camera);
    
    // Try to intersect with the point cloud geometry
    const intersects = raycaster.intersectObject(pointCloud);
    
    if (intersects.length > 0) {
        // Use intersection point if available
        mouseWorldPosition.copy(intersects[0].point);
    } else {
        // Fallback: project onto a plane at a fixed distance
        const distance = 100; // Fixed distance for more predictable behavior
        mouseWorldPosition.copy(raycaster.ray.origin)
            .add(raycaster.ray.direction.multiplyScalar(distance));
    }
}

function updateMouseTrail() {
    // Add current position to trail
    mouseTrail.push({
        x: mouseWorldPosition.x,
        y: mouseWorldPosition.y,
        z: mouseWorldPosition.z,
        strength: 1.0  // Full strength for newest position
    });
    
    // Limit trail length
    if (mouseTrail.length > MAX_TRAIL_LENGTH) {
        mouseTrail.shift();
    }
    
    // Fade older positions
    for (let i = 0; i < mouseTrail.length - 1; i++) {
        mouseTrail[i].strength = (i + 1) / mouseTrail.length;
    }
}

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

function storeOriginalPositions() {
    if (!pointCloud) return;
    
    const positions = pointCloud.geometry.attributes.position;
    originalPositions = new Float32Array(positions.array.length);
    originalPositions.set(positions.array);
    
    // Initialize particle velocities for wave effect
    particleVelocities = new Float32Array(positions.array.length);
    particleVelocities.fill(0);
    
    console.log('📍 Original positions and velocities stored for mouse interaction');
}

function applyMouseGravity() {
    const positions = pointCloud.geometry.attributes.position;
    const positionArray = positions.array;
    
    // Use dynamic values from sliders
    const currentStrength = gravityStrength;
    const maxDistance = gravityRange;
    
    let affectedParticles = 0;
    const dampening = 0.95; // Velocity dampening factor
    
    if (gravityMode === 'circle') {
        // Original circle mode - single point of attraction
        for (let i = 0; i < positionArray.length; i += 3) {
            const originalX = originalPositions[i];
            const originalY = originalPositions[i + 1];
            const originalZ = originalPositions[i + 2];
            
            // Calculate distance to mouse
            const dx = mouseWorldPosition.x - originalX;
            const dy = mouseWorldPosition.y - originalY;
            const dz = mouseWorldPosition.z - originalZ;
            const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
            
            if (distance < maxDistance && distance > 0) {
                affectedParticles++;
                
                // Apply stronger gravity effect for bigger movement
                const force = currentStrength * (maxDistance - distance) / maxDistance;
                const amplifiedForce = force * 3.0;
                
                // Add velocity
                particleVelocities[i] += dx * amplifiedForce * 0.2;
                particleVelocities[i + 1] += dy * amplifiedForce * 0.2;
                particleVelocities[i + 2] += dz * amplifiedForce * 0.2;
            }
        }
    } else if (gravityMode === 'flow' && mouseTrail.length > 0) {
        // Flow mode - multiple points of attraction along mouse path
        for (let i = 0; i < positionArray.length; i += 3) {
            const originalX = originalPositions[i];
            const originalY = originalPositions[i + 1];
            const originalZ = originalPositions[i + 2];
            
            let totalForceX = 0;
            let totalForceY = 0;
            let totalForceZ = 0;
            let hasEffect = false;
            
            // Check influence from each trail point
            for (const trailPoint of mouseTrail) {
                const dx = trailPoint.x - originalX;
                const dy = trailPoint.y - originalY;
                const dz = trailPoint.z - originalZ;
                const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
                
                if (distance < maxDistance && distance > 0) {
                    hasEffect = true;
                    
                    // Apply force with trail point strength
                    const force = currentStrength * (maxDistance - distance) / maxDistance * trailPoint.strength;
                    const amplifiedForce = force * 2.5; // Slightly less than circle mode
                    
                    totalForceX += dx * amplifiedForce * 0.15;
                    totalForceY += dy * amplifiedForce * 0.15;
                    totalForceZ += dz * amplifiedForce * 0.15;
                }
            }
            
            if (hasEffect) {
                affectedParticles++;
                
                // Apply combined force from all trail points
                particleVelocities[i] += totalForceX;
                particleVelocities[i + 1] += totalForceY;
                particleVelocities[i + 2] += totalForceZ;
            }
        }
    } else if (gravityMode === 'magnet') {
        // Magnet mode - particles are attracted to mouse like a real magnet
        for (let i = 0; i < positionArray.length; i += 3) {
            const originalX = originalPositions[i];
            const originalY = originalPositions[i + 1];
            const originalZ = originalPositions[i + 2];
            
            // Calculate distance to mouse
            const dx = mouseWorldPosition.x - originalX;
            const dy = mouseWorldPosition.y - originalY;
            const dz = mouseWorldPosition.z - originalZ;
            const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
            
            // Only apply force if particle is far enough from mouse (magnet behavior)
            if (distance > MIN_MAGNET_DISTANCE && distance < maxDistance) {
                affectedParticles++;
                
                // Normalize direction vector (consistent pull direction regardless of distance)
                const dirX = dx / distance;
                const dirY = dy / distance;
                const dirZ = dz / distance;
                
                // Magnetic force with realistic falloff (inverse square law, but capped for usability)
                const falloff = Math.max(0.1, (maxDistance - distance) / maxDistance);
                const magneticForce = currentStrength * falloff * 1.5; // Slightly stronger than circle mode
                
                // Apply normalized force (particles move toward mouse, don't overshoot)
                particleVelocities[i] += dirX * magneticForce * 0.15;
                particleVelocities[i + 1] += dirY * magneticForce * 0.15;
                particleVelocities[i + 2] += dirZ * magneticForce * 0.15;
            }
        }
    }
    
    // Second pass: Optimized wave propagation with sampling
    if (waveIntensity > 0) {
        const neighborDistance = 25; // Distance to consider particles as neighbors
        const waveStrength = waveIntensity * 0.03;
        const maxSampleSize = Math.min(2000, Math.floor(positionArray.length / 30)); // Limit sampling
        const sampleStep = Math.max(1, Math.floor(positionArray.length / (maxSampleSize * 3)));
        
        // Only process a subset of particles for wave propagation
        for (let i = 0; i < positionArray.length; i += sampleStep * 3) {
            // Skip if this particle has no velocity
            if (Math.abs(particleVelocities[i]) < 0.001 && 
                Math.abs(particleVelocities[i + 1]) < 0.001 && 
                Math.abs(particleVelocities[i + 2]) < 0.001) {
                continue;
            }
            
            let neighborInfluenceX = 0;
            let neighborInfluenceY = 0;
            let neighborInfluenceZ = 0;
            let neighborCount = 0;
            const maxNeighbors = 50; // Limit neighbors to check
            
            // Check nearby particles with early termination
            for (let j = 0; j < positionArray.length && neighborCount < maxNeighbors; j += 6) { // Skip every other particle
                if (i === j) continue;
                
                const dx = positionArray[j] - positionArray[i];
                const dy = positionArray[j + 1] - positionArray[i + 1];
                const dz = positionArray[j + 2] - positionArray[i + 2];
                
                // Quick distance check without sqrt for performance
                const distanceSquared = dx * dx + dy * dy + dz * dz;
                const neighborDistanceSquared = neighborDistance * neighborDistance;
                
                if (distanceSquared < neighborDistanceSquared && distanceSquared > 0.01) {
                    const distance = Math.sqrt(distanceSquared);
                    const influence = (neighborDistance - distance) / neighborDistance;
                    
                    neighborInfluenceX += particleVelocities[j] * influence;
                    neighborInfluenceY += particleVelocities[j + 1] * influence;
                    neighborInfluenceZ += particleVelocities[j + 2] * influence;
                    neighborCount++;
                }
            }
            
            // Apply wave propagation to nearby particles
            if (neighborCount > 0) {
                const avgInfluenceX = (neighborInfluenceX / neighborCount) * waveStrength;
                const avgInfluenceY = (neighborInfluenceY / neighborCount) * waveStrength;
                const avgInfluenceZ = (neighborInfluenceZ / neighborCount) * waveStrength;
                
                // Apply to current particle and some neighbors
                for (let k = Math.max(0, i - 9); k <= Math.min(positionArray.length - 3, i + 9); k += 3) {
                    particleVelocities[k] += avgInfluenceX * 0.3;
                    particleVelocities[k + 1] += avgInfluenceY * 0.3;
                    particleVelocities[k + 2] += avgInfluenceZ * 0.3;
                }
            }
        }
    }
    
    // Third pass: Apply velocities and handle return to original position
    for (let i = 0; i < positionArray.length; i += 3) {
        const originalX = originalPositions[i];
        const originalY = originalPositions[i + 1];
        const originalZ = originalPositions[i + 2];
        
        // Apply velocity
        positionArray[i] += particleVelocities[i];
        positionArray[i + 1] += particleVelocities[i + 1];
        positionArray[i + 2] += particleVelocities[i + 2];
        
        // Dampen velocity
        particleVelocities[i] *= dampening;
        particleVelocities[i + 1] *= dampening;
        particleVelocities[i + 2] *= dampening;
        
        // Add gentler spring force back to original position (slower return for longer visibility)
        const returnStrength = 0.015; // Reduced for slower return
        const returnForceX = (originalX - positionArray[i]) * returnStrength;
        const returnForceY = (originalY - positionArray[i + 1]) * returnStrength;
        const returnForceZ = (originalZ - positionArray[i + 2]) * returnStrength;
        
        particleVelocities[i] += returnForceX;
        particleVelocities[i + 1] += returnForceY;
        particleVelocities[i + 2] += returnForceZ;
    }
    
    // Update dynamic 3D effects based on new positions
    updateDynamic3DEffects();
    
    // Debug log every 120 frames (reduce logging frequency)
    if (Math.random() < 0.008) {
        console.log(`🌊 Wave gravity: ${affectedParticles} particles directly affected, wave intensity: ${waveIntensity.toFixed(2)}`);
    }
    
    positions.needsUpdate = true;
}

function toggleMouseGravity() {
    mouseGravityEnabled = !mouseGravityEnabled;
    const button = document.getElementById('gravityToggle');
    
    if (mouseGravityEnabled) {
        button.innerHTML = '🧲 Gravity ON';
        button.title = 'Gravity is ON (click to disable)';
        console.log('🧲 Mouse gravity enabled');
    } else {
        button.innerHTML = '🚫 Gravity OFF';
        button.title = 'Gravity is OFF (click to enable)';
        console.log('❌ Mouse gravity disabled');
        
        // Reset particles to original positions when disabled
        resetParticlePositions();
    }
}

function toggleGravityMode() {
    // Cycle through three modes: circle -> flow -> magnet -> circle
    if (gravityMode === 'circle') {
        gravityMode = 'flow';
    } else if (gravityMode === 'flow') {
        gravityMode = 'magnet';
    } else {
        gravityMode = 'circle';
    }
    
    const button = document.getElementById('gravityModeToggle');
    
    if (gravityMode === 'circle') {
        button.innerHTML = '🎯 Circle';
        button.title = 'Circle mode - particles attracted to current mouse position';
        mouseTrail = []; // Clear trail
        console.log('🎯 Switched to Circle gravity mode');
    } else if (gravityMode === 'flow') {
        button.innerHTML = '🌊 Flow';
        button.title = 'Flow mode - particles follow mouse movement path creating flowing effects';
        console.log('🌊 Switched to Flow gravity mode');
    } else if (gravityMode === 'magnet') {
        button.innerHTML = '🧲 Magnet';
        button.title = 'Magnet mode - particles gather toward mouse like iron filings to a magnet';
        mouseTrail = []; // Clear trail
        console.log('🧲 Switched to Magnet gravity mode');
    }
}

function updateDynamic3DEffects() {
    if (!pointCloud || !camera) return;
    
    const positions = pointCloud.geometry.attributes.position;
    const colors = pointCloud.geometry.attributes.color;
    const positionArray = positions.array;
    const colorArray = colors.array;
    const originalColors = pointCloud.geometry.userData.originalColors;
    
    if (!originalColors) return;
    
    const cameraPosition = camera.position;
    const material = pointCloud.material;
    
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
    const sizeMultiplier = Math.max(0.4, Math.min(3.0, 150 / avgCameraDistance));
    material.size = pointSize * sizeMultiplier;
    
    // Subtle opacity for extreme depth (very conservative)
    const globalOpacity = Math.max(0.8, Math.min(1.0, 1.0 - (avgCameraDistance / (maxCameraDistance * 1.5)) * 0.2));
    material.opacity = globalOpacity;
    
    colors.needsUpdate = true;
    material.needsUpdate = true;
}

function resetParticlePositions() {
    if (!pointCloud || !originalPositions) return;
    
    const positions = pointCloud.geometry.attributes.position;
    positions.array.set(originalPositions);
    
    // Reset velocities
    if (particleVelocities) {
        particleVelocities.fill(0);
    }
    
    // Reset colors to original enhanced state
    const colors = pointCloud.geometry.attributes.color;
    const originalColors = pointCloud.geometry.userData.originalColors;
    if (originalColors) {
        colors.array.set(originalColors);
        colors.needsUpdate = true;
    }
    
    positions.needsUpdate = true;
    
    console.log('🔄 Particles, velocities, and colors reset to original state');
}

// Audio analysis functions
function initializeAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        console.log('🎵 Audio context initialized');
    }
    return audioContext;
}

// Initialize external audio (microphone/BlackHole) automatically
function initializeExternalAudio() {
    // Wait a moment for page to fully load, then try to setup microphone
    setTimeout(() => {
        setupMicrophoneAnalysis().then(success => {
            if (success) {
                console.log('🎧 External audio initialized - Ready for BlackHole/external music!');
                
                // Update button to show microphone is active
                const micButton = document.getElementById('microphoneToggle');
                if (micButton) {
                    micButton.innerHTML = '🎤 External Audio ON';
                    micButton.title = 'External audio is ON (BlackHole/microphone input active)';
                }
                
                // Update audio reactive button
                const audioButton = document.getElementById('audioReactiveToggle');
                if (audioButton) {
                    audioButton.innerHTML = '🎵 Audio React ON';
                    audioButton.title = 'Audio reactive is ON - particles will respond to external music';
                }
            } else {
                console.log('💡 To use external music: Allow microphone access and select BlackHole as input device');
            }
        });
    }, 1000); // 1 second delay to ensure page is ready
}

function setupMusicAnalysis(audioElement) {
    if (!audioElement || musicAnalyser) return;
    
    try {
        const context = initializeAudioContext();
        const source = context.createMediaElementSource(audioElement);
        musicAnalyser = context.createAnalyser();
        musicAnalyser.fftSize = 256;
        musicDataArray = new Uint8Array(musicAnalyser.frequencyBinCount);
        
        source.connect(musicAnalyser);
        musicAnalyser.connect(context.destination);
        
        console.log('🎵 Music analysis setup complete');
    } catch (error) {
        console.error('❌ Music analysis setup failed:', error);
    }
}

function setupMicrophoneAnalysis() {
    if (micAnalyser) return Promise.resolve();
    
    return navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            const context = initializeAudioContext();
            microphoneSource = context.createMediaStreamSource(stream);
            micAnalyser = context.createAnalyser();
            micAnalyser.fftSize = 256;
            micDataArray = new Uint8Array(micAnalyser.frequencyBinCount);
            
            microphoneSource.connect(micAnalyser);
            microphoneEnabled = true;
            
            console.log('🎤 Microphone analysis setup complete - External audio ready!');
            return true;
        })
        .catch(error => {
            console.warn('⚠️ Microphone access denied - External audio will not work:', error.message);
            console.log('💡 To use external audio: Allow microphone access and select BlackHole as input');
            return false;
        });
}

function getVolumeLevel() {
    let volume = 0;
    let hasAudioSource = false;
    
    // Check microphone input first (external audio via BlackHole)
    if (microphoneEnabled && micAnalyser) {
        micAnalyser.getByteFrequencyData(micDataArray);
        const micVolume = getAverageVolume(micDataArray);
        volume = Math.max(volume, micVolume);
        hasAudioSource = true;
        
        // Analyze frequency bands for microphone
        analyzeFrequencyBands(micDataArray, micAnalyser.context.sampleRate);
    }
    
    // Check page music (if playing and no strong microphone signal)
    if (audioReactiveEnabled && musicAnalyser && musicPlaying) {
        musicAnalyser.getByteFrequencyData(musicDataArray);
        const musicVolume = getAverageVolume(musicDataArray);
        
        // Use page music if no microphone or microphone is quiet
        if (!microphoneEnabled || volume < 0.1) {
            volume = Math.max(volume, musicVolume);
            hasAudioSource = true;
            
            // Analyze frequency bands for page music
            analyzeFrequencyBands(musicDataArray, musicAnalyser.context.sampleRate);
        }
    }
    
    // Apply smoothing
    currentVolumeLevel = currentVolumeLevel * volumeSmoothing + volume * (1 - volumeSmoothing);
    return currentVolumeLevel;
}

function getAverageVolume(dataArray) {
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
    }
    return (sum / dataArray.length) / 255; // Normalize to 0-1
}

function analyzeFrequencyBands(dataArray, sampleRate) {
    // FFT size is 256, so we have 128 frequency bins
    // Each bin represents (sampleRate / 2) / 128 Hz
    const binSize = (sampleRate / 2) / dataArray.length;
    
    // Enhanced frequency ranges based on musical perception
    let bassEnd, midEnd;
    if (audioMode === 'voice') {
        // Voice mode: focus on speech frequencies (500-2000Hz for clarity)
        bassEnd = Math.floor(500 / binSize);
        midEnd = Math.floor(2000 / binSize);
    } else {
        // Music mode: improved frequency separation (60-250Hz, 250-2000Hz, 2000-8000Hz)
        bassEnd = Math.floor(250 / binSize);
        midEnd = Math.floor(2000 / binSize);
    }
    
    // Calculate average volume for each band
    let bassSum = 0, midSum = 0, trebleSum = 0;
    let bassCount = 0, midCount = 0, trebleCount = 0;
    
    for (let i = 0; i < dataArray.length; i++) {
        if (i <= bassEnd) {
            bassSum += dataArray[i];
            bassCount++;
        } else if (i <= midEnd) {
            midSum += dataArray[i];
            midCount++;
        } else {
            trebleSum += dataArray[i];
            trebleCount++;
        }
    }
    
    // Improved smoothing for better responsiveness
    const smoothing = 0.4; // Reduced from 0.7 for better responsiveness
    let newBass = Math.min(1.0, (bassSum / bassCount / 255));
    let newMid = Math.min(1.0, (midSum / midCount / 255));
    let newTreble = Math.min(1.0, (trebleSum / trebleCount / 255));
    
    // Apply perceptual weighting with microphone boost
    const isMicrophoneInput = microphoneEnabled && currentVolumeLevel > 0;
    const micBoost = isMicrophoneInput ? 2.5 : 1.0; // 2.5x boost for microphone input
    
    newBass *= adaptiveSystem.perceptualWeight.bass * micBoost;
    newMid *= adaptiveSystem.perceptualWeight.mid * micBoost;
    newTreble *= adaptiveSystem.perceptualWeight.treble * micBoost;
    
    frequencyBands.bass = frequencyBands.bass * smoothing + newBass * (1 - smoothing);
    frequencyBands.mid = frequencyBands.mid * smoothing + newMid * (1 - smoothing);
    frequencyBands.treble = frequencyBands.treble * smoothing + newTreble * (1 - smoothing);
    
    // Update adaptive history
    updateAdaptiveHistory();
    
    // Update dynamic thresholds
    updateDynamicThresholds();
    
    // Peak detection for enhanced responsiveness
    detectAudioPeaks();
}

// New function: Update adaptive history for dynamic thresholds
function updateAdaptiveHistory() {
    const history = adaptiveSystem.history;
    const maxLength = history.maxHistoryLength;
    
    // Add current values to history
    history.bass.push(frequencyBands.bass);
    history.mid.push(frequencyBands.mid);
    history.treble.push(frequencyBands.treble);
    history.volume.push(currentVolumeLevel);
    
    // Keep history within max length
    if (history.bass.length > maxLength) history.bass.shift();
    if (history.mid.length > maxLength) history.mid.shift();
    if (history.treble.length > maxLength) history.treble.shift();
    if (history.volume.length > maxLength) history.volume.shift();
}

// New function: Update dynamic thresholds based on audio history
function updateDynamicThresholds() {
    const history = adaptiveSystem.history;
    
    if (history.bass.length < 30) return; // Wait for enough history
    
    // Calculate adaptive thresholds (80% of recent average)
    const getAverage = (arr) => arr.slice(-60).reduce((a, b) => a + b, 0) / Math.min(arr.length, 60);
    
    adaptiveSystem.frequencyThresholds.bass = Math.max(0.05, getAverage(history.bass) * 0.8);
    adaptiveSystem.frequencyThresholds.mid = Math.max(0.05, getAverage(history.mid) * 0.8);
    adaptiveSystem.frequencyThresholds.treble = Math.max(0.05, getAverage(history.treble) * 0.8);
    adaptiveSystem.volumeThreshold = Math.max(0.1, getAverage(history.volume) * 0.8);
}

// New function: Detect audio peaks for enhanced response
function detectAudioPeaks() {
    const history = adaptiveSystem.history;
    if (history.bass.length < 5) return;
    
    // Simple peak detection (current > 150% of recent average)
    const recent = 5;
    const getRecentAvg = (arr) => arr.slice(-recent).reduce((a, b) => a + b, 0) / recent;
    
    const bassAvg = getRecentAvg(history.bass.slice(0, -1));
    const midAvg = getRecentAvg(history.mid.slice(0, -1));
    const trebleAvg = getRecentAvg(history.treble.slice(0, -1));
    
    // Apply peak boost for immediate response
    if (frequencyBands.bass > bassAvg * 1.5) frequencyBands.bass *= 1.2;
    if (frequencyBands.mid > midAvg * 1.5) frequencyBands.mid *= 1.2;
    if (frequencyBands.treble > trebleAvg * 1.5) frequencyBands.treble *= 1.2;
}

function toggleAudioReactive() {
    audioReactiveEnabled = !audioReactiveEnabled;
    const button = document.getElementById('audioReactiveToggle');
    
    if (audioReactiveEnabled) {
        button.innerHTML = '🎵 Audio React ON';
        button.title = 'Audio reactive is ON (click to disable)';
        console.log('🎵 Audio-reactive mode enabled');
        // Setup audio analysis for the music element if it exists
        if (audioElement && !musicAnalyser) {
            setupMusicAnalysis(audioElement);
        }
    } else {
        button.innerHTML = '🔇 Audio React OFF';
        button.title = 'Audio reactive is OFF (click to enable)';
        console.log('🔇 Audio-reactive mode disabled');
        
        // Reset to normal state when disabling audio reactive
        resetToNormalState();
    }
}

function toggleMicrophone() {
    if (!microphoneEnabled) {
        setupMicrophoneAnalysis().then(success => {
            if (success) {
                // microphoneEnabled is already set to true in setupMicrophoneAnalysis
                const button = document.getElementById('microphoneToggle');
                button.innerHTML = '🎤 Mic ON';
                button.title = 'Microphone is ON (click to disable)';
                console.log('🎤 Microphone enabled');
            } else {
                // Failed to setup microphone, ensure flag remains false
                microphoneEnabled = false;
                const button = document.getElementById('microphoneToggle');
                button.innerHTML = '🎙️ Mic Failed';
                button.title = 'Microphone access failed';
                console.log('🎤 Microphone setup failed');
            }
        });
    } else {
        microphoneEnabled = false;
        if (microphoneSource) {
            microphoneSource.disconnect();
        }
        const button = document.getElementById('microphoneToggle');
        button.innerHTML = '🎙️ Mic OFF';
        button.title = 'Microphone is OFF (click to enable)';
        console.log('🎤 Microphone disabled');
        
        // Reset to normal state when disabling microphone (if audio reactive is also off)
        if (!audioReactiveEnabled) {
            resetToNormalState();
        }
    }
}

function applyAudioReactiveEffects() {
    const volumeLevel = getVolumeLevel();
    
    // Use adaptive thresholds instead of fixed ones
    const shouldTrigger = volumeLevel > adaptiveSystem.volumeThreshold || 
                         frequencyBands.bass > adaptiveSystem.frequencyThresholds.bass || 
                         frequencyBands.mid > adaptiveSystem.frequencyThresholds.mid || 
                         frequencyBands.treble > adaptiveSystem.frequencyThresholds.treble;
    
    if (shouldTrigger) {
        // Calculate new effect intensities
        let newSizeMultiplier, newBrightnessMultiplier, newColorIntensity;
        
        // Enhanced volume-responsive system
        if (volumeLevel > adaptiveSystem.volumeThreshold) {
            // Volume-level based effects with improved mapping
            if (volumeLevel < 0.25) {
                // Low volume: subtle pulse
                newSizeMultiplier = 1.0 + (volumeLevel * 0.8);
                newBrightnessMultiplier = 1.0 + (volumeLevel * 0.6);
                newColorIntensity = 1.0 + (volumeLevel * 0.4);
            } else if (volumeLevel < 0.6) {
                // Medium volume: wave ripple
                newSizeMultiplier = 1.0 + (frequencyBands.bass * 1.8);
                newBrightnessMultiplier = 1.0 + (frequencyBands.mid * 1.6);
                newColorIntensity = 1.0 + (frequencyBands.treble * 1.4);
            } else {
                // High volume: dramatic expansion
                newSizeMultiplier = 1.0 + (frequencyBands.bass * 2.2);
                newBrightnessMultiplier = 1.0 + (frequencyBands.mid * 2.0);
                newColorIntensity = 1.0 + (frequencyBands.treble * 1.8);
            }
        } else {
            // Frequency-only effects (when volume is low but frequencies detected)
            newSizeMultiplier = 1.0 + (frequencyBands.bass * 1.2);
            newBrightnessMultiplier = 1.0 + (frequencyBands.mid * 1.0);
            newColorIntensity = 1.0 + (frequencyBands.treble * 0.8);
        }
        
        // Apply dynamic mode boost
        if (dynamicModeEnabled) {
            const boost = 1.4;
            newSizeMultiplier = (newSizeMultiplier - 1.0) * boost + 1.0;
            newBrightnessMultiplier = (newBrightnessMultiplier - 1.0) * boost + 1.0;
            newColorIntensity = (newColorIntensity - 1.0) * boost + 1.0;
        }
        
        // Update current effects (for decay system)
        currentEffects.sizeMultiplier = Math.max(currentEffects.sizeMultiplier, newSizeMultiplier);
        currentEffects.brightnessMultiplier = Math.max(currentEffects.brightnessMultiplier, newBrightnessMultiplier);
        currentEffects.colorIntensity = Math.max(currentEffects.colorIntensity, newColorIntensity);
    }
    
    // Apply decay to all effects for natural fade-out
    currentEffects.sizeMultiplier = Math.max(1.0, currentEffects.sizeMultiplier * effectDecay.size);
    currentEffects.brightnessMultiplier = Math.max(1.0, currentEffects.brightnessMultiplier * effectDecay.brightness);
    currentEffects.colorIntensity = Math.max(1.0, currentEffects.colorIntensity * effectDecay.color);
    currentEffects.movementIntensity *= effectDecay.movement;
    
    // Apply effects to visual elements
    applyVisualEffects();
    
    // Apply movement effects
    applyMovementEffects();
    
    // Enhanced debug logging
    if (Math.random() < 0.01) {
        const modeIcon = audioMode === 'music' ? '🎵' : '🎤';
        const dynamicSuffix = dynamicModeEnabled ? ' +Dynamic' : '';
        console.log(`${modeIcon} ${audioMode} mode${dynamicSuffix}: vol=${(volumeLevel * 100).toFixed(1)}% bass=${(frequencyBands.bass * 100).toFixed(1)}% mid=${(frequencyBands.mid * 100).toFixed(1)}% treble=${(frequencyBands.treble * 100).toFixed(1)}% → size=${currentEffects.sizeMultiplier.toFixed(2)}x bright=${currentEffects.brightnessMultiplier.toFixed(2)}x color=${currentEffects.colorIntensity.toFixed(2)}x`);
    }
}

// New function: Apply visual effects (size, brightness, color)
function applyVisualEffects() {
    if (!pointCloud) return;
    
    // 1. Size effect
    pointCloud.material.size = pointSize * currentEffects.sizeMultiplier;
    
    // 2. Brightness effect
    if (ambientLight) {
        ambientLight.intensity = brightnessLevel * currentEffects.brightnessMultiplier;
    }
    if (directionalLight) {
        directionalLight.intensity = brightnessLevel * 1.5 * currentEffects.brightnessMultiplier;
    }
    
    // 3. Enhanced color intensity effect with better performance
    if (pointCloud.geometry.attributes.color) {
        const colors = pointCloud.geometry.attributes.color;
        const originalColors = pointCloud.geometry.userData.originalColors;
        
        if (originalColors) {
            const colorArray = colors.array;
            const step = Math.max(12, Math.floor(colorArray.length / 1000)); // Adaptive step size
            
            for (let i = 0; i < colorArray.length; i += step) {
                if (i + 2 < colorArray.length) {
                    colorArray[i] = Math.min(1.0, originalColors[i] * currentEffects.colorIntensity);
                    colorArray[i + 1] = Math.min(1.0, originalColors[i + 1] * currentEffects.colorIntensity);
                    colorArray[i + 2] = Math.min(1.0, originalColors[i + 2] * currentEffects.colorIntensity);
                }
            }
            colors.needsUpdate = true;
        }
    }
}

// New function: Apply movement effects based on frequency analysis
function applyMovementEffects() {
    if (!originalPositions || !particleVelocities) return;
    
    // Enhanced movement effects using adaptive thresholds
    if (audioMode === 'music') {
        // Bass: outward expansion with adaptive threshold
        if (frequencyBands.bass > adaptiveSystem.frequencyThresholds.bass * 1.5) {
            const expansionForce = frequencyBands.bass * 0.12;
            currentEffects.movementIntensity = Math.max(currentEffects.movementIntensity, expansionForce);
            
            applyExpansionEffect(expansionForce, 35); // Every 35th particle
        }
        
        // Mid: rotating wave effect
        if (frequencyBands.mid > adaptiveSystem.frequencyThresholds.mid * 1.2) {
            const waveForce = frequencyBands.mid * 0.08;
            applyWaveEffect(waveForce, 45); // Every 45th particle
        }
        
        // Treble: shimmer effect with improved distribution
        if (frequencyBands.treble > adaptiveSystem.frequencyThresholds.treble * 1.1) {
            const shimmerForce = frequencyBands.treble * 0.04;
            applyShimmerEffect(shimmerForce, 50); // Every 50th particle
        }
    } else {
        // Voice mode: gentler volume-based expansion
        if (volumeLevel > adaptiveSystem.volumeThreshold * 1.5) {
            const expansionForce = volumeLevel * 0.08;
            applyExpansionEffect(expansionForce, 40);
        }
    }
}

// Helper function: Apply expansion effect
function applyExpansionEffect(force, step) {
    for (let i = 0; i < particleVelocities.length; i += step) {
        const centerX = 0, centerY = 0, centerZ = 0;
        const dx = originalPositions[i] - centerX;
        const dy = originalPositions[i + 1] - centerY;
        const dz = originalPositions[i + 2] - centerZ;
        const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (distance > 0) {
            particleVelocities[i] += (dx / distance) * force;
            particleVelocities[i + 1] += (dy / distance) * force;
            particleVelocities[i + 2] += (dz / distance) * force;
        }
    }
}

// Helper function: Apply wave effect
function applyWaveEffect(force, step) {
    const time = Date.now() * 0.001;
    for (let i = 0; i < particleVelocities.length; i += step) {
        const angle = time + (i / step) * 0.1;
        particleVelocities[i] += Math.sin(angle) * force * 0.5;
        particleVelocities[i + 1] += Math.cos(angle) * force * 0.5;
        particleVelocities[i + 2] += Math.sin(angle * 1.3) * force * 0.3;
    }
}

// Helper function: Apply shimmer effect
function applyShimmerEffect(force, step) {
    for (let i = 0; i < particleVelocities.length; i += step) {
        particleVelocities[i] += (Math.random() - 0.5) * force;
        particleVelocities[i + 1] += (Math.random() - 0.5) * force;
        particleVelocities[i + 2] += (Math.random() - 0.5) * force;
    }
}

function resetToNormalState() {
    if (!pointCloud) return;
    
    console.log('🔄 Resetting to normal state');
    
    // Reset particle size to default
    pointCloud.material.size = pointSize;
    
    // Reset lighting to default levels
    if (ambientLight) {
        ambientLight.intensity = brightnessLevel;
    }
    if (directionalLight) {
        directionalLight.intensity = brightnessLevel * 1.5;
    }
    
    // Reset colors to original
    if (pointCloud.geometry.attributes.color) {
        const colors = pointCloud.geometry.attributes.color;
        const originalColors = pointCloud.geometry.userData.originalColors;
        
        if (originalColors) {
            colors.array.set(originalColors);
            colors.needsUpdate = true;
        }
    }
    
    // Reset audio analysis values
    currentVolumeLevel = 0;
    frequencyBands.bass = 0;
    frequencyBands.mid = 0;
    frequencyBands.treble = 0;
    
    console.log('✅ Normal state restored');
}

MUSIC_FUNCTIONS_PLACEHOLDER

// Make functions globally accessible for HTML events
window.toggleAutoRotate = toggleAutoRotate;
window.resetCamera = resetCamera;
window.updatePointSize = updatePointSize;
window.updateRotationSpeed = updateRotationSpeed;
window.toggleBrightness = toggleBrightness;
window.updateGlowIntensity = updateGlowIntensity;
window.toggleMouseGravity = toggleMouseGravity;

// Gravity adjustment functions
function updateGravityRange(value) {
    gravityRange = parseFloat(value);
    console.log(`🧲 Gravity range updated to: ${gravityRange}`);
}

function updateGravityStrength(value) {
    gravityStrength = parseFloat(value) / 100; // Convert 0-100 to 0-1
    console.log(`🧲 Gravity strength updated to: ${gravityStrength}`);
}

function updateWaveIntensity(value) {
    waveIntensity = parseFloat(value) / 100; // Convert 0-100 to 0-1
    console.log(`🌊 Wave intensity updated to: ${waveIntensity}`);
}

function toggleAudioMode() {
    audioMode = audioMode === 'music' ? 'voice' : 'music';
    const button = document.getElementById('audioModeToggle');
    
    // Reset frequency bands when switching modes to prevent residual effects
    frequencyBands.bass = 0;
    frequencyBands.mid = 0;
    frequencyBands.treble = 0;
    
    if (audioMode === 'music') {
        button.innerHTML = '🎵 Music Mode ON';
        button.title = 'Currently in music mode (bass/mid/treble separation)';
        console.log('🎵 Switched to music mode');
    } else {
        button.innerHTML = '🎤 Voice Mode ON';
        button.title = 'Currently in voice mode (speech frequency focus)';
        console.log('🎤 Switched to voice mode');
    }
}

function toggleDynamicMode() {
    dynamicModeEnabled = !dynamicModeEnabled;
    const button = document.getElementById('dynamicModeToggle');
    
    if (dynamicModeEnabled) {
        button.innerHTML = '🚀 Dynamic ON';
        button.title = 'Dynamic enhancement is ON (40% boost)';
        console.log('🚀 Dynamic mode enabled');
    } else {
        button.innerHTML = '🚀 Dynamic OFF';
        button.title = 'Dynamic enhancement is OFF';
        console.log('🚀 Dynamic mode disabled');
    }
}

window.updateGravityRange = updateGravityRange;
window.updateGravityStrength = updateGravityStrength;
window.updateWaveIntensity = updateWaveIntensity;
window.toggleGravityMode = toggleGravityMode;
window.toggleAudioReactive = toggleAudioReactive;
window.toggleMicrophone = toggleMicrophone;
window.toggleAudioMode = toggleAudioMode;
window.toggleDynamicMode = toggleDynamicMode;
MUSIC_WINDOW_PLACEHOLDER

// Start the application
init();