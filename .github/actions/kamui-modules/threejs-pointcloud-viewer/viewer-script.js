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
    
    // Mouse position tracking
    document.addEventListener('mousemove', (e) => {
        // Show if mouse is in left 300px of screen
        if (e.clientX < 300) {
            showControls();
        } else {
            scheduleHide();
        }
    });
    
    // Show when hovering over controls
    controls.addEventListener('mouseenter', showControls);
    controls.addEventListener('mouseleave', scheduleHide);
    
    // Initial hide after 5 seconds
    setTimeout(() => {
        scheduleHide();
    }, 5000);
}

function setupMouseInteraction() {
    // Track mouse position for 3D interaction
    document.addEventListener('mousemove', (event) => {
        // Normalize mouse coordinates to [-1, 1]
        mousePosition.x = (event.clientX / window.innerWidth) * 2 - 1;
        mousePosition.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        // Convert to world coordinates
        updateMouseWorldPosition();
    });
}

function updateMouseWorldPosition() {
    if (!camera || !pointCloud) return;
    
    // Create a raycaster to get 3D mouse position
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(mousePosition, camera);
    
    // Get intersection with point cloud bounds
    const box = new THREE.Box3().setFromObject(pointCloud);
    const center = box.getCenter(new THREE.Vector3());
    const distance = camera.position.distanceTo(center);
    
    // Project mouse position onto a plane at the point cloud center
    mouseWorldPosition.copy(raycaster.ray.origin)
        .add(raycaster.ray.direction.multiplyScalar(distance * 0.8));
}

function storeOriginalPositions() {
    if (!pointCloud) return;
    
    const positions = pointCloud.geometry.attributes.position;
    originalPositions = new Float32Array(positions.array.length);
    originalPositions.set(positions.array);
    
    console.log('📍 Original positions stored for mouse interaction');
}

function applyMouseGravity() {
    const positions = pointCloud.geometry.attributes.position;
    const positionArray = positions.array;
    
    const gravityStrength = 0.02; // Adjustable gravity strength
    const maxDistance = 50; // Maximum effective distance
    
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
            // Apply gravity effect (inverse square law with smoothing)
            const force = gravityStrength * (maxDistance - distance) / maxDistance;
            const smoothForce = force * force; // Smooth falloff
            
            // Move particle towards mouse
            positionArray[i] = originalX + dx * smoothForce;
            positionArray[i + 1] = originalY + dy * smoothForce;
            positionArray[i + 2] = originalZ + dz * smoothForce;
        } else {
            // Return to original position when far from mouse
            const returnSpeed = 0.05;
            positionArray[i] += (originalX - positionArray[i]) * returnSpeed;
            positionArray[i + 1] += (originalY - positionArray[i + 1]) * returnSpeed;
            positionArray[i + 2] += (originalZ - positionArray[i + 2]) * returnSpeed;
        }
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
    positions.needsUpdate = true;
    
    console.log('🔄 Particles reset to original positions');
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
MUSIC_WINDOW_PLACEHOLDER

// Start the application
init();