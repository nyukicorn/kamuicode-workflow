// Global variables
let scene, camera, renderer, controls;
let pointCloud = null;
let autoRotate = AUTO_ROTATE_PLACEHOLDER;
let rotationSpeed = ANIMATION_SPEED_PLACEHOLDER;
let pointSize = POINT_SIZE_PLACEHOLDER;
let audioElement = null;
let musicPlaying = false;

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
let mouseGravityEnabled = true;
let gravityStrength = 0.1;  // Default strength
let gravityRange = 100;     // Default range
let waveIntensity = 0.3;    // Wave propagation intensity (0-1)
let particleVelocities = null; // Store particle velocities for wave effect

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
        
        // Create point cloud material
        const material = new THREE.PointsMaterial({
            vertexColors: true,
            size: pointSize,
            sizeAttenuation: true,
            transparent: false
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
        button.innerHTML = '🌙 Dark';
        button.title = 'Switch to dark mode';
    } else {
        // Make it dim - keep original dark appearance
        brightnessLevel = 0.3;
        scene.background = new THREE.Color('BACKGROUND_COLOR_PLACEHOLDER');
        button.innerHTML = '☀️ Light';
        button.title = 'Switch to light mode';
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
        
        // Debug log occasionally
        if (Math.random() < 0.01) {
            console.log(`🖱️ Mouse: screen(${event.clientX}, ${event.clientY}) normalized(${mousePosition.x.toFixed(2)}, ${mousePosition.y.toFixed(2)})`);
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
    
    // First pass: Direct mouse gravity effect
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
            
            // Apply gravity effect (linear falloff for more visible effect)
            const force = currentStrength * (maxDistance - distance) / maxDistance;
            
            // Add velocity for wave effect
            particleVelocities[i] += dx * force * 0.1;
            particleVelocities[i + 1] += dy * force * 0.1;
            particleVelocities[i + 2] += dz * force * 0.1;
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
        
        // Add spring force back to original position
        const returnStrength = 0.02;
        const returnForceX = (originalX - positionArray[i]) * returnStrength;
        const returnForceY = (originalY - positionArray[i + 1]) * returnStrength;
        const returnForceZ = (originalZ - positionArray[i + 2]) * returnStrength;
        
        particleVelocities[i] += returnForceX;
        particleVelocities[i + 1] += returnForceY;
        particleVelocities[i + 2] += returnForceZ;
    }
    
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
        button.innerHTML = '🧲 Gravity';
        button.title = 'Mouse gravity enabled - move mouse to attract particles';
        console.log('🧲 Mouse gravity enabled');
    } else {
        button.innerHTML = '❌ No Gravity';
        button.title = 'Mouse gravity disabled';
        console.log('❌ Mouse gravity disabled');
        
        // Reset particles to original positions when disabled
        resetParticlePositions();
    }
}

function resetParticlePositions() {
    if (!pointCloud || !originalPositions) return;
    
    const positions = pointCloud.geometry.attributes.position;
    positions.array.set(originalPositions);
    
    // Reset velocities
    if (particleVelocities) {
        particleVelocities.fill(0);
    }
    
    positions.needsUpdate = true;
    
    console.log('🔄 Particles and velocities reset to original state');
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

window.updateGravityRange = updateGravityRange;
window.updateGravityStrength = updateGravityStrength;
window.updateWaveIntensity = updateWaveIntensity;
MUSIC_WINDOW_PLACEHOLDER

// Start the application
init();