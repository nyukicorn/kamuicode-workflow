// Mouse Interaction System for Three.js Viewers
// Shared component for mouse gravity, wave effects, and particle interactions

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

// Initialize mouse interaction system
function initializeMouseInteraction(pointCloudObject, cameraObject) {
    // Store original positions for interaction
    storeOriginalPositions(pointCloudObject);
    
    // Track mouse position for 3D interaction
    document.addEventListener('mousemove', (event) => {
        // Handle control visibility
        const controls = document.getElementById('controls');
        if (controls && event.clientX < 300) {
            controls.classList.add('visible');
        }
        
        // Normalize mouse coordinates to [-1, 1]
        mousePosition.x = (event.clientX / window.innerWidth) * 2 - 1;
        mousePosition.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        // Convert to world coordinates
        updateMouseWorldPosition(pointCloudObject, cameraObject);
        
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
    
    console.log('🖱️ Mouse interaction system initialized');
}

function updateMouseWorldPosition(pointCloudObject, cameraObject) {
    if (!cameraObject || !pointCloudObject) return;
    
    // Create a raycaster to get 3D mouse position
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(mousePosition, cameraObject);
    
    // Try to intersect with the point cloud geometry
    const intersects = raycaster.intersectObject(pointCloudObject);
    
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

function storeOriginalPositions(pointCloudObject) {
    if (!pointCloudObject) return;
    
    const positions = pointCloudObject.geometry.attributes.position;
    originalPositions = new Float32Array(positions.array.length);
    originalPositions.set(positions.array);
    
    // Initialize particle velocities for wave effect
    particleVelocities = new Float32Array(positions.array.length);
    particleVelocities.fill(0);
    
    console.log('📍 Original positions and velocities stored for mouse interaction');
}

// Apply mouse gravity effect (call this in animation loop)
function applyMouseGravity(pointCloudObject) {
    if (!mouseGravityEnabled || !pointCloudObject || !originalPositions) return;
    
    const positions = pointCloudObject.geometry.attributes.position;
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

function resetParticlePositions(pointCloudObject) {
    if (!pointCloudObject || !originalPositions) return;
    
    const positions = pointCloudObject.geometry.attributes.position;
    positions.array.set(originalPositions);
    
    // Reset velocities
    if (particleVelocities) {
        particleVelocities.fill(0);
    }
    
    positions.needsUpdate = true;
    
    console.log('🔄 Particles and velocities reset to original state');
}

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

// Movement effects for audio integration
function applyMovementEffects() {
    if (!originalPositions || !particleVelocities) return;
    
    // Enhanced movement effects using adaptive thresholds (requires audio system integration)
    if (typeof frequencyBands !== 'undefined' && typeof adaptiveSystem !== 'undefined') {
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
            if (typeof currentVolumeLevel !== 'undefined' && currentVolumeLevel > adaptiveSystem.volumeThreshold * 1.5) {
                const expansionForce = currentVolumeLevel * 0.08;
                applyExpansionEffect(expansionForce, 40);
            }
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

// Export functions to global scope for HTML events
window.toggleMouseGravity = toggleMouseGravity;
window.toggleGravityMode = toggleGravityMode;
window.updateGravityRange = updateGravityRange;
window.updateGravityStrength = updateGravityStrength;
window.updateWaveIntensity = updateWaveIntensity;