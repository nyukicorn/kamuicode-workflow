// Camera Controls System for Three.js Viewers
// Shared component for camera setup, controls, and navigation

// Camera and controls variables
let scene, camera, renderer, controls;
let autoRotate = false;
let rotationSpeed = 1.0;

// Initialize camera system
function initializeCameraSystem(containerElement, backgroundColorHex = '#1a1a1a') {
    // Scene setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(backgroundColorHex);
    
    // Camera setup
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
    
    // Renderer setup
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerElement.appendChild(renderer.domElement);
    
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
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Keyboard controls
    document.addEventListener('keydown', onKeyDown);
    
    // Double-click to toggle rotation (don't prevent default to preserve zoom)
    renderer.domElement.addEventListener('dblclick', (event) => {
        // Don't prevent default - let OrbitControls handle zoom
        toggleAutoRotate();
    });
    
    console.log('🎥 Camera system initialized');
    return { scene, camera, renderer, controls };
}

// Set camera position
function setCameraPosition(x, y, z) {
    if (camera) {
        camera.position.set(x, y, z);
        console.log(`📍 Camera position set to: (${x}, ${y}, ${z})`);
    }
}

// Set auto-rotate settings
function setAutoRotateSettings(enabled, speed) {
    autoRotate = enabled;
    rotationSpeed = speed;
    if (controls) {
        controls.autoRotate = autoRotate;
        controls.autoRotateSpeed = rotationSpeed;
        console.log(`🔄 Auto-rotate: ${enabled ? 'ON' : 'OFF'}, Speed: ${speed}`);
    }
}

// Fit camera to object
function fitCameraToObject(object) {
    if (!camera || !controls || !object) return;
    
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
    
    console.log('📐 Camera fitted to object:', { center, distance });
}

// Control functions
function toggleAutoRotate() {
    autoRotate = !autoRotate;
    if (controls) {
        controls.autoRotate = autoRotate;
        console.log(`🔄 Auto-rotate toggled: ${autoRotate ? 'ON' : 'OFF'}`);
    }
}

function resetCamera() {
    if (!camera || !controls) return;
    
    // Reset to default position if no specific object to fit
    camera.position.set(0, 0, 100);
    controls.target.set(0, 0, 0);
    controls.update();
    
    console.log('🔄 Camera reset to default position');
}

function resetCameraToObject(object) {
    if (object) {
        fitCameraToObject(object);
        // Ensure rotation is around the object center
        const box = new THREE.Box3().setFromObject(object);
        const center = box.getCenter(new THREE.Vector3());
        controls.target.copy(center);
        controls.update();
        console.log('🔄 Camera reset to object center');
    } else {
        resetCamera();
    }
}

function updateRotationSpeed(value) {
    rotationSpeed = parseFloat(value);
    if (controls) {
        controls.autoRotateSpeed = rotationSpeed;
        console.log(`⚡ Rotation speed updated to: ${rotationSpeed}`);
    }
}

// Update camera controls (call this in animation loop)
function updateCameraControls() {
    if (controls) {
        controls.update();
    }
}

// Render scene
function renderScene() {
    if (renderer && scene && camera) {
        renderer.render(scene, camera);
    }
}

// Window resize handler
function onWindowResize() {
    if (camera && renderer) {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
        console.log('📱 Window resized, camera aspect updated');
    }
}

// Keyboard navigation
function onKeyDown(event) {
    if (!camera) return;
    
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

// Get camera information
function getCameraInfo() {
    if (!camera || !controls) return null;
    
    return {
        position: camera.position.clone(),
        target: controls.target.clone(),
        autoRotate: autoRotate,
        rotationSpeed: rotationSpeed
    };
}

// Set background color
function setBackgroundColor(colorHex) {
    if (scene) {
        scene.background = new THREE.Color(colorHex);
        console.log(`🎨 Background color changed to: ${colorHex}`);
    }
}

// Cleanup function
function cleanupCameraSystem() {
    if (renderer && renderer.domElement && renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
    }
    
    window.removeEventListener('resize', onWindowResize);
    document.removeEventListener('keydown', onKeyDown);
    
    console.log('🧹 Camera system cleaned up');
}

// Export functions to global scope for HTML events
window.toggleAutoRotate = toggleAutoRotate;
window.resetCamera = resetCamera;
window.updateRotationSpeed = updateRotationSpeed;