// Enhanced Particle System Template for Three.js Experiences
// This template provides high-density particle generation for realistic 3D objects

class EnhancedParticleSystem {
    constructor(scene, config = {}) {
        this.scene = scene;
        this.config = {
            artStyle: config.artStyle || 'flower:rose',
            particleColor: config.particleColor || 'auto',
            particleShape: config.particleShape || 'circle',
            arrangement: config.arrangement || 'floating',
            objectDetails: config.objectDetails || '',
            ...config
        };
        
        this.time = 0;
        this.particleSystems = [];
        this.init();
    }

    init() {
        const [category, type] = this.config.artStyle.split(':');
        
        if (category === 'flower') {
            this.createFlowerSystem(type);
        } else if (category === 'nature') {
            this.createNatureSystem(type);
        } else if (category === 'geometric') {
            this.createGeometricSystem(type);
        } else {
            this.createSimpleParticles();
        }
        
        this.createAmbientParticles();
        this.createFloatingParticles();
    }

    createFlowerSystem(flowerType) {
        const configs = {
            rose: {
                objectCount: 10,
                particlesPerObject: 8000,
                layers: 8,
                particlesPerLayer: 1000,
                baseColors: [0xff69b4, 0xff1493, 0xdc143c, 0xb22222],
                petalFunction: (theta, layer) => {
                    const r = (layer + 1) * 0.8 * (Math.sin(5 * theta) * 0.5 + 1);
                    return r;
                }
            },
            sakura: {
                objectCount: 15,
                particlesPerObject: 6000,
                layers: 5,
                particlesPerLayer: 1200,
                baseColors: [0xffb6c1, 0xffc0cb, 0xffd0e4, 0xffe4e1],
                petalFunction: (theta, layer) => {
                    const r = (layer + 1) * 0.6 * (Math.sin(5 * theta) * 0.3 + 1);
                    return r;
                }
            },
            lily: {
                objectCount: 6,
                particlesPerObject: 7000,
                layers: 6,
                particlesPerLayer: 1166,
                baseColors: [0xffffff, 0xfffacd, 0xf0e68c, 0xffd700],
                petalFunction: (theta, layer) => {
                    const r = (layer + 1) * 0.7 * Math.exp(-layer * 0.1);
                    return r;
                }
            }
        };

        const config = configs[flowerType] || configs.rose;
        
        for (let i = 0; i < config.objectCount; i++) {
            const flower = this.createSingleFlower(config, i);
            this.particleSystems.push(flower);
            this.scene.add(flower);
        }
    }

    createSingleFlower(config, index) {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(config.particlesPerObject * 3);
        const colors = new Float32Array(config.particlesPerObject * 3);
        const scales = new Float32Array(config.particlesPerObject);
        
        // Random position for this flower
        const flowerCenter = new THREE.Vector3(
            (Math.random() - 0.5) * 100,
            Math.random() * 30 - 15,
            (Math.random() - 0.5) * 100
        );

        let particleIndex = 0;
        const particlesPerLayer = Math.floor(config.particlesPerObject / config.layers);

        // Create layers of petals
        for (let layer = 0; layer < config.layers; layer++) {
            const layerOffset = layer * 0.1;
            
            for (let i = 0; i < particlesPerLayer && particleIndex < config.particlesPerObject; i++) {
                const angle = (i / particlesPerLayer) * Math.PI * 2;
                const radius = config.petalFunction(angle, layer);
                
                // Add some randomness for natural look
                const randomOffset = 0.2;
                const x = radius * Math.cos(angle) + (Math.random() - 0.5) * randomOffset;
                const y = layerOffset + (Math.random() - 0.5) * 0.3;
                const z = radius * Math.sin(angle) + (Math.random() - 0.5) * randomOffset;
                
                positions[particleIndex * 3] = flowerCenter.x + x;
                positions[particleIndex * 3 + 1] = flowerCenter.y + y;
                positions[particleIndex * 3 + 2] = flowerCenter.z + z;
                
                // Color with gradient
                const colorIndex = Math.floor(Math.random() * config.baseColors.length);
                const color = new THREE.Color(config.baseColors[colorIndex]);
                const intensity = 1.0 - (layer / config.layers) * 0.4;
                color.multiplyScalar(intensity);
                
                colors[particleIndex * 3] = color.r;
                colors[particleIndex * 3 + 1] = color.g;
                colors[particleIndex * 3 + 2] = color.b;
                
                scales[particleIndex] = 0.02 + Math.random() * 0.03;
                particleIndex++;
            }
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(scales, 1));

        const material = new THREE.PointsMaterial({
            size: 0.5,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            sizeAttenuation: true
        });

        const flower = new THREE.Points(geometry, material);
        flower.userData = {
            type: 'flower',
            center: flowerCenter,
            phase: Math.random() * Math.PI * 2
        };

        return flower;
    }

    createAmbientParticles() {
        const particleCount = 2500;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 150;
            positions[i * 3 + 1] = Math.random() * 60 - 30;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 150;
            
            const color = new THREE.Color();
            color.setHSL(0.1 + Math.random() * 0.1, 0.3, 0.8);
            
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: 0.15,
            vertexColors: true,
            transparent: true,
            opacity: 0.4,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });

        const ambient = new THREE.Points(geometry, material);
        ambient.userData = { type: 'ambient' };
        this.particleSystems.push(ambient);
        this.scene.add(ambient);
    }

    createFloatingParticles() {
        const particleCount = 800;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const velocities = [];
        
        // Get colors from current flower type
        const [category, type] = this.config.artStyle.split(':');
        let baseColors = [0xffffff];
        
        if (category === 'flower') {
            if (type === 'rose') baseColors = [0xff69b4, 0xff1493];
            else if (type === 'sakura') baseColors = [0xffb6c1, 0xffc0cb];
            else if (type === 'lily') baseColors = [0xffffff, 0xfffacd];
        }
        
        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 120;
            positions[i * 3 + 1] = Math.random() * 50;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 120;
            
            const color = new THREE.Color(baseColors[Math.floor(Math.random() * baseColors.length)]);
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
            
            velocities.push({
                x: (Math.random() - 0.5) * 0.02,
                y: -Math.random() * 0.03 - 0.01,
                z: (Math.random() - 0.5) * 0.02
            });
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: 1.0,
            vertexColors: true,
            transparent: true,
            opacity: 0.6,
            blending: THREE.NormalBlending,
            depthWrite: false
        });

        const floating = new THREE.Points(geometry, material);
        floating.userData = { 
            type: 'floating',
            velocities: velocities 
        };
        this.particleSystems.push(floating);
        this.scene.add(floating);
    }

    update(deltaTime) {
        this.time += deltaTime;
        
        this.particleSystems.forEach(system => {
            if (system.userData.type === 'flower') {
                // Gentle swaying motion
                const phase = this.time * 0.5 + system.userData.phase;
                system.rotation.y = Math.sin(phase) * 0.05;
                system.position.y += Math.sin(phase * 2) * 0.001;
                
            } else if (system.userData.type === 'ambient') {
                // Slow rotation for ambient particles
                system.rotation.y += 0.001;
                
            } else if (system.userData.type === 'floating') {
                // Falling and swirling motion
                const positions = system.geometry.attributes.position.array;
                const velocities = system.userData.velocities;
                
                for (let i = 0; i < velocities.length; i++) {
                    positions[i * 3] += velocities[i].x + Math.sin(this.time + i) * 0.005;
                    positions[i * 3 + 1] += velocities[i].y;
                    positions[i * 3 + 2] += velocities[i].z + Math.cos(this.time + i) * 0.005;
                    
                    // Reset particles that fall too low
                    if (positions[i * 3 + 1] < -30) {
                        positions[i * 3 + 1] = 30;
                        positions[i * 3] = (Math.random() - 0.5) * 120;
                        positions[i * 3 + 2] = (Math.random() - 0.5) * 120;
                    }
                }
                
                system.geometry.attributes.position.needsUpdate = true;
            }
        });
    }

    dispose() {
        this.particleSystems.forEach(system => {
            system.geometry.dispose();
            system.material.dispose();
            this.scene.remove(system);
        });
        this.particleSystems = [];
    }
}

// Export for use in generated scenes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedParticleSystem;
}