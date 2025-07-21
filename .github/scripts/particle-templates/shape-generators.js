// Particle Shape Generators
// Creates custom textures and geometries for various particle shapes

class ParticleShapeGenerators {
    static createCircleTexture(size = 64) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const context = canvas.getContext('2d');
        
        // Clear with transparent background
        context.clearRect(0, 0, size, size);
        
        const center = size / 2;
        const radius = size * 0.4;
        
        // Create radial gradient
        const gradient = context.createRadialGradient(center, center, 0, center, center, radius);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradient.addColorStop(0.7, 'rgba(255, 255, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        context.fillStyle = gradient;
        context.beginPath();
        context.arc(center, center, radius, 0, Math.PI * 2);
        context.fill();
        
        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        return texture;
    }
    
    static createSoftCircleTexture(size = 64) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const context = canvas.getContext('2d');
        
        context.clearRect(0, 0, size, size);
        
        const center = size / 2;
        const radius = size * 0.45;
        
        // Softer gradient
        const gradient = context.createRadialGradient(center, center, 0, center, center, radius);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
        gradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.6)');
        gradient.addColorStop(0.8, 'rgba(255, 255, 255, 0.2)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        context.fillStyle = gradient;
        context.beginPath();
        context.arc(center, center, radius, 0, Math.PI * 2);
        context.fill();
        
        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        return texture;
    }

    static createHeartTexture(size = 64) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const context = canvas.getContext('2d');
        
        // CRITICAL: Ensure transparent background
        context.clearRect(0, 0, size, size);
        context.globalCompositeOperation = 'source-over';
        
        const centerX = size / 2;
        const centerY = size * 0.55;
        const scale = size * 0.02;
        
        // Heart shape path
        context.beginPath();
        context.moveTo(centerX, centerY);
        
        // Left curve
        context.bezierCurveTo(
            centerX - scale * 15, centerY - scale * 10,
            centerX - scale * 20, centerY + scale * 3,
            centerX, centerY + scale * 15
        );
        
        // Right curve  
        context.bezierCurveTo(
            centerX + scale * 20, centerY + scale * 3,
            centerX + scale * 15, centerY - scale * 10,
            centerX, centerY
        );
        
        context.closePath();
        
        // Fill with gradient
        const gradient = context.createLinearGradient(centerX, centerY - scale * 10, centerX, centerY + scale * 15);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0.7)');
        
        context.fillStyle = gradient;
        context.fill();
        
        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        return texture;
    }

    static createStarTexture(size = 64, points = 5) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const context = canvas.getContext('2d');
        
        context.clearRect(0, 0, size, size);
        
        const centerX = size / 2;
        const centerY = size / 2;
        const outerRadius = size * 0.4;
        const innerRadius = size * 0.2;
        
        context.beginPath();
        
        for (let i = 0; i < points * 2; i++) {
            const angle = (i * Math.PI) / points;
            const radius = i % 2 === 0 ? outerRadius : innerRadius;
            const x = centerX + Math.cos(angle - Math.PI / 2) * radius;
            const y = centerY + Math.sin(angle - Math.PI / 2) * radius;
            
            if (i === 0) {
                context.moveTo(x, y);
            } else {
                context.lineTo(x, y);
            }
        }
        
        context.closePath();
        
        const gradient = context.createRadialGradient(centerX, centerY, 0, centerX, centerY, outerRadius);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradient.addColorStop(0.7, 'rgba(255, 255, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        context.fillStyle = gradient;
        context.fill();
        
        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        return texture;
    }

    static createDiamondTexture(size = 64) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const context = canvas.getContext('2d');
        
        context.clearRect(0, 0, size, size);
        
        const centerX = size / 2;
        const centerY = size / 2;
        const radius = size * 0.4;
        
        context.beginPath();
        context.moveTo(centerX, centerY - radius);     // Top
        context.lineTo(centerX + radius, centerY);     // Right
        context.lineTo(centerX, centerY + radius);     // Bottom
        context.lineTo(centerX - radius, centerY);     // Left
        context.closePath();
        
        const gradient = context.createLinearGradient(centerX - radius, centerY - radius, centerX + radius, centerY + radius);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0.3)');
        
        context.fillStyle = gradient;
        context.fill();
        
        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        return texture;
    }

    static createSquareTexture(size = 64) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const context = canvas.getContext('2d');
        
        context.clearRect(0, 0, size, size);
        
        const squareSize = size * 0.8;
        const startX = (size - squareSize) / 2;
        const startY = (size - squareSize) / 2;
        
        const gradient = context.createLinearGradient(startX, startY, startX + squareSize, startY + squareSize);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0.6)');
        
        context.fillStyle = gradient;
        context.fillRect(startX, startY, squareSize, squareSize);
        
        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        return texture;
    }

    static createPetalTexture(size = 64) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const context = canvas.getContext('2d');
        
        context.clearRect(0, 0, size, size);
        
        const centerX = size / 2;
        const centerY = size * 0.8;
        const width = size * 0.4;
        const height = size * 0.6;
        
        // Petal shape using bezier curves
        context.beginPath();
        context.moveTo(centerX, centerY);
        
        // Left side of petal
        context.bezierCurveTo(
            centerX - width, centerY - height * 0.3,
            centerX - width * 0.3, centerY - height,
            centerX, centerY - height
        );
        
        // Right side of petal
        context.bezierCurveTo(
            centerX + width * 0.3, centerY - height,
            centerX + width, centerY - height * 0.3,
            centerX, centerY
        );
        
        context.closePath();
        
        const gradient = context.createLinearGradient(centerX, centerY - height, centerX, centerY);
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
        gradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.7)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0.4)');
        
        context.fillStyle = gradient;
        context.fill();
        
        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        return texture;
    }

    static getShapeTexture(shapeType, size = 64) {
        const textureCache = this.textureCache || (this.textureCache = {});
        const cacheKey = `${shapeType}_${size}`;
        
        if (textureCache[cacheKey]) {
            return textureCache[cacheKey];
        }
        
        let texture;
        
        switch (shapeType) {
            case 'circle':
                texture = this.createCircleTexture(size);
                break;
            case 'soft_circle':
                texture = this.createSoftCircleTexture(size);
                break;
            case 'heart':
                texture = this.createHeartTexture(size);
                break;
            case 'star':
                texture = this.createStarTexture(size);
                break;
            case 'diamond':
                texture = this.createDiamondTexture(size);
                break;
            case 'square':
                texture = this.createSquareTexture(size);
                break;
            case 'petal':
                texture = this.createPetalTexture(size);
                break;
            default:
                texture = this.createCircleTexture(size);
        }
        
        textureCache[cacheKey] = texture;
        return texture;
    }

    static createMaterial(shapeType, config = {}) {
        const texture = this.getShapeTexture(shapeType);
        
        const material = new THREE.PointsMaterial({
            map: texture,
            transparent: true,
            alphaTest: 0.1,
            vertexColors: true,
            blending: config.blending || THREE.AdditiveBlending,
            depthWrite: false,
            size: config.size || 1.0,
            sizeAttenuation: config.sizeAttenuation !== false,
            opacity: config.opacity || 0.8
        });
        
        return material;
    }

    static clearCache() {
        if (this.textureCache) {
            Object.values(this.textureCache).forEach(texture => {
                texture.dispose();
            });
            this.textureCache = {};
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ParticleShapeGenerators;
}