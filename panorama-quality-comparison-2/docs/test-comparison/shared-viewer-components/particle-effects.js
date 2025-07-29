// Particle effects for panorama viewer
console.log('Particle effects loaded');

function createParticleSystem(geometry, options) {
    const material = new THREE.PointsMaterial({
        size: options.size || 2.0,
        sizeAttenuation: options.sizeAttenuation !== false,
        transparent: options.transparent !== false,
        opacity: options.opacity || 0.9,
        vertexColors: options.vertexColors !== false,
        blending: options.blending || THREE.NormalBlending
    });
    
    return new THREE.Points(geometry, material);
}

function updateParticleSystem(particles, camera, ambientLight, directionalLight) {
    // Update particle system effects
    if (particles && particles.material) {
        // Basic particle system update
        particles.material.needsUpdate = true;
    }
}

function updateStatsDisplay(particles) {
    const statsElement = document.getElementById('stats');
    if (statsElement && particles && particles.geometry) {
        const count = particles.geometry.attributes.position.count;
        statsElement.textContent = `Particles: ${count.toLocaleString()}`;
    }
}

function updateLoadingProgress(message) {
    const loading = document.getElementById('loading');
    if (loading) {
        const text = loading.querySelector('div:last-child');
        if (text) text.textContent = message;
    }
}

// Export to global
window.createParticleSystem = createParticleSystem;
window.updateParticleSystem = updateParticleSystem;
window.updateStatsDisplay = updateStatsDisplay;
window.updateLoadingProgress = updateLoadingProgress;