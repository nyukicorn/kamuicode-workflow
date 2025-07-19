class UmbrellaParticleSystem {
    constructor(scene) {
        this.scene = scene;
        this.particleSystem = null;
        this.time = 0;
        this.umbrellaParticles = [];
        this.petalParticles = null;
        
        this.init();
    }

    init() {
        this.createUmbrellaParticles();
        this.createPetalParticles();
    }

    createUmbrellaParticles() {
        const umbrellaCount = 15;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(umbrellaCount * 3);
        const colors = new Float32Array(umbrellaCount * 3);
        const scales = new Float32Array(umbrellaCount);
        const rotations = new Float32Array(umbrellaCount);
        const speeds = new Float32Array(umbrellaCount);

        for (let i = 0; i < umbrellaCount; i++) {
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.random() * Math.PI;
            const radius = 20 + Math.random() * 60;

            positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i * 3 + 1] = radius * Math.cos(phi) - 10;
            positions[i * 3 + 2] = radius * Math.sin(phi) * Math.sin(theta);

            const color = new THREE.Color();
            color.setHSL(Math.random() * 0.1 + 0.9, 0.8, 0.6);
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;

            scales[i] = Math.random() * 0.5 + 0.5;
            rotations[i] = Math.random() * Math.PI * 2;
            speeds[i] = Math.random() * 0.02 + 0.01;

            this.umbrellaParticles.push({
                originalY: positions[i * 3 + 1],
                speed: speeds[i],
                rotationSpeed: (Math.random() - 0.5) * 0.02
            });
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('scale', new THREE.BufferAttribute(scales, 1));

        const vertexShader = `
            attribute float scale;
            attribute vec3 color;
            varying vec3 vColor;
            varying vec2 vUv;

            void main() {
                vColor = color;
                vUv = position.xy;
                
                vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                gl_PointSize = scale * 30.0 * (300.0 / -mvPosition.z);
                gl_Position = projectionMatrix * mvPosition;
            }
        `;

        const fragmentShader = `
            varying vec3 vColor;
            varying vec2 vUv;

            void main() {
                vec2 center = gl_PointCoord - vec2(0.5);
                float dist = length(center);
                
                if (dist > 0.5) discard;
                
                float alpha = 1.0 - smoothstep(0.3, 0.5, dist);
                gl_FragColor = vec4(vColor, alpha * 0.8);
            }
        `;

        const material = new THREE.ShaderMaterial({
            vertexShader: vertexShader,
            fragmentShader: fragmentShader,
            transparent: true,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
            vertexColors: true
        });

        this.particleSystem = new THREE.Points(geometry, material);
        this.scene.add(this.particleSystem);
    }

    createPetalParticles() {
        const petalCount = 200;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(petalCount * 3);
        const colors = new Float32Array(petalCount * 3);
        const scales = new Float32Array(petalCount);

        for (let i = 0; i < petalCount; i++) {
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.random() * Math.PI;
            const radius = 10 + Math.random() * 80;

            positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i * 3 + 1] = Math.random() * 40 - 20;
            positions[i * 3 + 2] = radius * Math.sin(phi) * Math.sin(theta);

            const color = new THREE.Color();
            const hue = Math.random() * 0.15 + 0.85;
            color.setHSL(hue, 0.6, 0.7);
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;

            scales[i] = Math.random() * 0.3 + 0.1;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('scale', new THREE.BufferAttribute(scales, 1));

        const material = new THREE.PointsMaterial({
            size: 2,
            transparent: true,
            opacity: 0.6,
            vertexColors: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });

        this.petalParticles = new THREE.Points(geometry, material);
        this.scene.add(this.petalParticles);
    }

    update(deltaTime) {
        this.time += deltaTime;

        if (this.particleSystem) {
            const positions = this.particleSystem.geometry.attributes.position.array;
            
            for (let i = 0; i < this.umbrellaParticles.length; i++) {
                const particle = this.umbrellaParticles[i];
                
                positions[i * 3 + 1] = particle.originalY + Math.sin(this.time * particle.speed) * 3;
                
                const rotationOffset = Math.sin(this.time * particle.rotationSpeed) * 0.5;
                positions[i * 3] += rotationOffset;
                positions[i * 3 + 2] += rotationOffset;
            }
            
            this.particleSystem.geometry.attributes.position.needsUpdate = true;
            this.particleSystem.rotation.y += 0.002;
        }

        if (this.petalParticles) {
            const positions = this.petalParticles.geometry.attributes.position.array;
            
            for (let i = 0; i < positions.length / 3; i++) {
                positions[i * 3 + 1] -= 0.02;
                positions[i * 3] += Math.sin(this.time * 0.01 + i) * 0.01;
                
                if (positions[i * 3 + 1] < -25) {
                    positions[i * 3 + 1] = 25;
                    const theta = Math.random() * Math.PI * 2;
                    const radius = 10 + Math.random() * 80;
                    positions[i * 3] = radius * Math.cos(theta);
                    positions[i * 3 + 2] = radius * Math.sin(theta);
                }
            }
            
            this.petalParticles.geometry.attributes.position.needsUpdate = true;
            this.petalParticles.rotation.y += 0.001;
        }
    }

    dispose() {
        if (this.particleSystem) {
            this.particleSystem.geometry.dispose();
            this.particleSystem.material.dispose();
            this.scene.remove(this.particleSystem);
        }
        
        if (this.petalParticles) {
            this.petalParticles.geometry.dispose();
            this.petalParticles.material.dispose();
            this.scene.remove(this.petalParticles);
        }
    }
}