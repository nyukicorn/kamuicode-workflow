// UI Controls for panorama viewer
console.log('UI controls loaded');

function initializeCompleteUISystem(scene, backgroundColor) {
    // Add basic lighting for specialized panorama
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    
    scene.add(ambientLight);
    scene.add(directionalLight);
    
    return {
        ambientLight,
        directionalLight
    };
}

// Export to global
window.initializeCompleteUISystem = initializeCompleteUISystem;