// Advanced Flower Shape Generation Algorithms
// Mathematical functions for creating realistic 3D flower structures

class FlowerAlgorithms {
    static getRoseShape(theta, layer, totalLayers) {
        // Rose petal function using polar coordinates
        // Based on r = a(1 + cos(nθ)) where n determines petal count
        const n = 5; // Number of petal lobes
        const baseRadius = (layer + 1) * 0.8;
        const petalFactor = Math.sin(n * theta) * Math.cos(theta) + 1;
        const radius = baseRadius * petalFactor;
        
        // Add layer-specific variations
        const layerFactor = 1.0 - (layer / totalLayers) * 0.3;
        const heightVariation = Math.sin(theta * 3) * 0.2 * layerFactor;
        
        return {
            radius: radius * layerFactor,
            height: heightVariation,
            density: 1.0 - (layer / totalLayers) * 0.4
        };
    }

    static getSakuraShape(theta, layer, totalLayers) {
        // Sakura (cherry blossom) with 5 distinct petals
        const petalAngle = (Math.PI * 2) / 5;
        const currentPetal = Math.floor(theta / petalAngle);
        const petalTheta = theta % petalAngle;
        
        const baseRadius = (layer + 1) * 0.6;
        // Heart-shaped petal function
        const t = (petalTheta / petalAngle) * Math.PI;
        const petalShape = Math.sin(t) * Math.sqrt(Math.abs(Math.cos(t)));
        
        const radius = baseRadius * (0.7 + petalShape * 0.3);
        const heightVariation = Math.sin(petalTheta * 8) * 0.15;
        
        return {
            radius: radius,
            height: heightVariation,
            density: 1.0 - (layer / totalLayers) * 0.3
        };
    }

    static getLilyShape(theta, layer, totalLayers) {
        // Lily with trumpet/funnel shape
        const n = 6; // Six petals
        const baseRadius = (layer + 1) * 0.7;
        
        // Exponential decay for trumpet shape
        const trumpetFactor = Math.exp(-layer * 0.2);
        const petalCurve = Math.abs(Math.sin(n * theta));
        
        const radius = baseRadius * trumpetFactor * (0.5 + petalCurve * 0.5);
        const heightVariation = layer * 0.3 * Math.sin(theta * 2);
        
        return {
            radius: radius,
            height: heightVariation,
            density: trumpetFactor
        };
    }

    static getTulipShape(theta, layer, totalLayers) {
        // Tulip with cup shape
        const baseRadius = (totalLayers - layer) * 0.5;
        const cupFactor = Math.sqrt(layer / totalLayers);
        
        const radius = baseRadius * (1.0 - cupFactor * 0.3);
        const heightVariation = layer * 0.4;
        
        return {
            radius: radius,
            height: heightVariation,
            density: 1.0 - (layer / totalLayers) * 0.2
        };
    }

    static getSunflowerShape(theta, layer, totalLayers) {
        // Sunflower with spiral pattern (Fibonacci)
        const goldenAngle = Math.PI * (3 - Math.sqrt(5)); // Golden angle
        const spiralRadius = Math.sqrt(layer + 1) * 0.5;
        
        // Fibonacci spiral positioning
        const spiralTheta = theta + layer * goldenAngle;
        const radius = spiralRadius * (1 + Math.sin(8 * spiralTheta) * 0.1);
        
        return {
            radius: radius,
            height: Math.sin(spiralTheta * 3) * 0.1,
            density: 1.0
        };
    }

    static getCustomShape(theta, layer, totalLayers, shapeParams) {
        // Customizable flower shape with parameters
        const {
            petalCount = 5,
            petalCurve = 1.0,
            layerSpacing = 0.8,
            heightVariation = 0.2,
            spiralFactor = 0
        } = shapeParams;

        const baseRadius = (layer + 1) * layerSpacing;
        const petalAngle = (Math.PI * 2) / petalCount;
        
        // Apply spiral if specified
        const spiralTheta = theta + layer * spiralFactor;
        
        // Petal shape function
        const petalFunction = Math.sin(petalCount * spiralTheta) * petalCurve + 1;
        const radius = baseRadius * petalFunction;
        
        const heightVar = Math.sin(spiralTheta * 3) * heightVariation;
        
        return {
            radius: radius,
            height: heightVar,
            density: 1.0 - (layer / totalLayers) * 0.3
        };
    }

    static generateFlowerColors(flowerType, layer, totalLayers) {
        const colorSchemes = {
            rose: {
                baseColors: [0xff69b4, 0xff1493, 0xdc143c, 0xb22222],
                gradientIntensity: 0.4
            },
            sakura: {
                baseColors: [0xffb6c1, 0xffc0cb, 0xffd0e4, 0xffe4e1],
                gradientIntensity: 0.3
            },
            lily: {
                baseColors: [0xffffff, 0xfffacd, 0xf0e68c, 0xffd700],
                gradientIntensity: 0.2
            },
            tulip: {
                baseColors: [0xff6347, 0xff4500, 0xff0000, 0x8b0000],
                gradientIntensity: 0.5
            },
            sunflower: {
                baseColors: [0xffd700, 0xffa500, 0xff8c00, 0xff4500],
                gradientIntensity: 0.3
            }
        };

        const scheme = colorSchemes[flowerType] || colorSchemes.rose;
        const colorIndex = Math.floor(Math.random() * scheme.baseColors.length);
        const baseColor = new THREE.Color(scheme.baseColors[colorIndex]);
        
        // Apply gradient based on layer
        const gradientFactor = 1.0 - (layer / totalLayers) * scheme.gradientIntensity;
        baseColor.multiplyScalar(gradientFactor);
        
        return baseColor;
    }

    static getFlowerConfig(flowerType) {
        const configs = {
            rose: {
                layers: 8,
                particlesPerLayer: 1000,
                shapeFunction: this.getRoseShape,
                size: { min: 0.02, max: 0.06 }
            },
            sakura: {
                layers: 5,
                particlesPerLayer: 1200,
                shapeFunction: this.getSakuraShape,
                size: { min: 0.015, max: 0.05 }
            },
            lily: {
                layers: 6,
                particlesPerLayer: 1166,
                shapeFunction: this.getLilyShape,
                size: { min: 0.025, max: 0.07 }
            },
            tulip: {
                layers: 7,
                particlesPerLayer: 1000,
                shapeFunction: this.getTulipShape,
                size: { min: 0.02, max: 0.06 }
            },
            sunflower: {
                layers: 10,
                particlesPerLayer: 800,
                shapeFunction: this.getSunflowerShape,
                size: { min: 0.01, max: 0.04 }
            }
        };

        return configs[flowerType] || configs.rose;
    }

    static generateFlowerParticles(flowerType, centerPosition, customParams = {}) {
        const config = this.getFlowerConfig(flowerType);
        const totalParticles = config.layers * config.particlesPerLayer;
        
        const positions = new Float32Array(totalParticles * 3);
        const colors = new Float32Array(totalParticles * 3);
        const scales = new Float32Array(totalParticles);
        
        let particleIndex = 0;

        for (let layer = 0; layer < config.layers; layer++) {
            const particlesInLayer = config.particlesPerLayer;
            
            for (let i = 0; i < particlesInLayer; i++) {
                const angle = (i / particlesInLayer) * Math.PI * 2;
                const shapeData = config.shapeFunction(angle, layer, config.layers);
                
                // Calculate 3D position
                const x = shapeData.radius * Math.cos(angle);
                const y = shapeData.height;
                const z = shapeData.radius * Math.sin(angle);
                
                // Add randomness for natural look
                const randomFactor = 0.1;
                positions[particleIndex * 3] = centerPosition.x + x + (Math.random() - 0.5) * randomFactor;
                positions[particleIndex * 3 + 1] = centerPosition.y + y + (Math.random() - 0.5) * randomFactor;
                positions[particleIndex * 3 + 2] = centerPosition.z + z + (Math.random() - 0.5) * randomFactor;
                
                // Generate color
                const color = this.generateFlowerColors(flowerType, layer, config.layers);
                colors[particleIndex * 3] = color.r;
                colors[particleIndex * 3 + 1] = color.g;
                colors[particleIndex * 3 + 2] = color.b;
                
                // Scale based on layer density
                const baseSize = config.size.min + Math.random() * (config.size.max - config.size.min);
                scales[particleIndex] = baseSize * shapeData.density;
                
                particleIndex++;
            }
        }

        return { positions, colors, scales, totalParticles };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlowerAlgorithms;
}