// Mouse interaction for panorama viewer
console.log('Mouse interaction loaded');

function initializeMouseInteraction(particles, camera) {
    console.log('Mouse interaction initialized for particles');
}

function applyMouseGravity(particles) {
    // Basic mouse gravity effect placeholder
}

function resetParticleColors(particles) {
    if (particles && particles.geometry && particles.geometry.attributes.color) {
        particles.geometry.attributes.color.needsUpdate = true;
    }
}

// Export to global
window.initializeMouseInteraction = initializeMouseInteraction;
window.applyMouseGravity = applyMouseGravity;
window.resetParticleColors = resetParticleColors;