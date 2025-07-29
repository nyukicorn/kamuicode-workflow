// Simple Method A panorama viewer for comparison test
let scene, camera, renderer, sphere;
let autoRotate = true;

function init() {
    console.log('🅰️ Method A: Specialized Panorama Viewer (Simplified for test)');
    
    // Scene setup
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ antialias: true });
    
    // Get container or use body
    const container = document.getElementById('container') || document.body;
    const rect = container.getBoundingClientRect();
    renderer.setSize(rect.width || 600, rect.height || 400);
    renderer.setClearColor(0x000814);
    container.appendChild(renderer.domElement);
    
    // Create sphere geometry (Method A - "specialized")
    const geometry = new THREE.SphereGeometry(200, 64, 32); // Higher resolution than Method B
    
    // Load texture
    const loader = new THREE.TextureLoader();
    loader.load('panorama.jpg', function(texture) {
        const material = new THREE.MeshBasicMaterial({ 
            map: texture,
            side: THREE.BackSide  // Render inside of sphere
        });
        
        sphere = new THREE.Mesh(geometry, material);
        scene.add(sphere);
        
        // Hide loading
        const loading = document.getElementById('loading');
        if (loading) loading.style.display = 'none';
        
        console.log('✅ Method A: Specialized panorama loaded');
    }, undefined, function(error) {
        console.error('❌ Method A: Failed to load panorama:', error);
    });
    
    // Camera position (center of sphere)
    camera.position.set(0, 0, 0);
    
    // Mouse controls
    setupControls();
    
    // Start animation
    animate();
}

function setupControls() {
    let mouseDown = false;
    let mouse = { x: 0, y: 0 };
    
    renderer.domElement.addEventListener('mousedown', (event) => {
        mouseDown = true;
        mouse.x = event.clientX;
        mouse.y = event.clientY;
    });
    
    renderer.domElement.addEventListener('mousemove', (event) => {
        if (!mouseDown) return;
        
        const deltaX = event.clientX - mouse.x;
        const deltaY = event.clientY - mouse.y;
        
        camera.rotation.y += deltaX * 0.005;
        camera.rotation.x += deltaY * 0.005;
        
        // Limit vertical rotation
        camera.rotation.x = Math.max(-Math.PI/2, Math.min(Math.PI/2, camera.rotation.x));
        
        mouse.x = event.clientX;
        mouse.y = event.clientY;
    });
    
    renderer.domElement.addEventListener('mouseup', () => {
        mouseDown = false;
    });
    
    renderer.domElement.addEventListener('wheel', (event) => {
        camera.fov += event.deltaY * 0.05;
        camera.fov = Math.max(10, Math.min(75, camera.fov));
        camera.updateProjectionMatrix();
    });
}

function animate() {
    requestAnimationFrame(animate);
    
    // Auto-rotation (Method A feature)
    if (autoRotate && sphere) {
        camera.rotation.y += 0.003; // Slightly faster than Method B
    }
    
    renderer.render(scene, camera);
}

// Dummy functions for UI compatibility
function toggleAutoRotate() {
    autoRotate = !autoRotate;
    console.log('Method A auto-rotate:', autoRotate);
}

function resetCamera() {
    camera.position.set(0, 0, 0);
    camera.rotation.set(0, 0, 0);
    camera.fov = 75;
    camera.updateProjectionMatrix();
}

function updateParticleSize() { /* Method A doesn't use particles in this test */ }
function updateRotationSpeed() { /* Simplified */ }

// Export to global
window.toggleAutoRotate = toggleAutoRotate;
window.resetCamera = resetCamera;
window.updateParticleSize = updateParticleSize;
window.updateRotationSpeed = updateRotationSpeed;

// Handle window resize
window.addEventListener('resize', function() {
    const container = document.getElementById('container') || document.body;
    const rect = container.getBoundingClientRect();
    camera.aspect = rect.width / rect.height;
    camera.updateProjectionMatrix();
    renderer.setSize(rect.width, rect.height);
});

// Initialize
init();