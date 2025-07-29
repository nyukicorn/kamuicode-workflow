// Camera controls for panorama viewer
console.log('Camera controls loaded');

function initializeCameraSystem(container, backgroundColor) {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(backgroundColor || '#000814');
    container.appendChild(renderer.domElement);
    
    // OrbitControls setup
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enablePan = false;
    controls.enableZoom = true;
    controls.enableRotate = true;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 1.0;
    
    return { scene, camera, renderer, controls };
}

function setCameraPosition(x, y, z) {
    if (window.camera) {
        window.camera.position.set(x, y, z);
    }
}

function setAutoRotateSettings(autoRotate, speed) {
    if (window.controls) {
        window.controls.autoRotate = autoRotate;
        window.controls.autoRotateSpeed = speed;
    }
}

function updateCameraControls() {
    if (window.controls) {
        window.controls.update();
    }
}

function renderScene() {
    if (window.renderer && window.scene && window.camera) {
        window.renderer.render(window.scene, window.camera);
    }
}

// Export to global
window.initializeCameraSystem = initializeCameraSystem;
window.setCameraPosition = setCameraPosition;
window.setAutoRotateSettings = setAutoRotateSettings;
window.updateCameraControls = updateCameraControls;
window.renderScene = renderScene;