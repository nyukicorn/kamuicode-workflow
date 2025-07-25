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
        
        console.log('✅ Point cloud loaded:', pointCount, 'points');
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
    
    // Simple 2-level toggle: dim (0.2) <-> bright (0.8)
    if (brightnessLevel <= 0.5) {
        // Make it bright
        brightnessLevel = 0.8;
        button.innerHTML = '🌙 Dark';
        button.title = 'Switch to dark mode';
    } else {
        // Make it dim
        brightnessLevel = 0.2;
        button.innerHTML = '☀️ Light';
        button.title = 'Switch to light mode';
    }
    
    // Apply brightness change to both lights for dramatic effect
    ambientLight.intensity = brightnessLevel;
    directionalLight.intensity = brightnessLevel * 1.5; // Even more dramatic difference
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

MUSIC_FUNCTIONS_PLACEHOLDER

// Make functions globally accessible for HTML events
window.toggleAutoRotate = toggleAutoRotate;
window.resetCamera = resetCamera;
window.updatePointSize = updatePointSize;
window.updateRotationSpeed = updateRotationSpeed;
window.toggleBrightness = toggleBrightness;
window.updateGlowIntensity = updateGlowIntensity;
MUSIC_WINDOW_PLACEHOLDER

// Start the application
init();