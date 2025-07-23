#!/bin/bash
set -e

echo "::group::🎨 Three.js Scene Generation"
echo "Starting at: $(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"

# 環境変数から設定を読み込み
SRC_DIR="$FOLDER_NAME/src"
ASSETS_DIR="$FOLDER_NAME/assets"

echo "Configuration:"
echo "  Experience concept: $EXPERIENCE_CONCEPT"
echo "  Background type: $BACKGROUND_TYPE"
echo "  Art style: $ART_STYLE"
echo "  Object details: $OBJECT_DETAILS"
echo "  Arrangement: $ARRANGEMENT"
echo "  Color scheme: $COLOR_SCHEME"
echo "  Particle color: $PARTICLE_COLOR"
echo "  Target folders: $SRC_DIR"

# ディレクトリを事前に作成
mkdir -p "$SRC_DIR"
mkdir -p "$ASSETS_DIR"
echo "📁 Created directory structure"

# プロンプト構築（トークン最適化版）
PROMPT="Create HTML file at $SRC_DIR/index.html for: $EXPERIENCE_CONCEPT

Tech: Three.js CDN r128, inline JS, no OrbitControls"

# 背景・アート・設定（圧縮版）
PROMPT="$PROMPT
BG: $BACKGROUND_TYPE"

PROMPT="$PROMPT
Art: $ART_STYLE, $ARRANGEMENT layout"

# オブジェクト詳細仕様があれば追加
[ -n "$OBJECT_DETAILS" ] && PROMPT="$PROMPT
Object: $OBJECT_DETAILS"

# 設定追加
[ "$COLOR_SCHEME" != "auto" ] && PROMPT="$PROMPT, $COLOR_SCHEME colors"
[ "$EFFECTS" != "none" ] && PROMPT="$PROMPT, $EFFECTS effects"

# パーティクル形状・色・密度
PROMPT="$PROMPT
Particle Shape: $PARTICLE_SHAPE shaped particles
Particle Color: $PARTICLE_COLOR color scheme

HIGH-DENSITY ENHANCED PARTICLE SYSTEM - COPY THESE TEMPLATES:

1. Include these JavaScript classes directly in HTML:

// TEMPLATE 1: Enhanced Particle System (High-Density + 3D Visual Version)
class EnhancedParticleSystem {
    constructor(scene, config = {}) {
        this.scene = scene;
        this.artStyle = config.artStyle || '$ART_STYLE';
        this.particleCount = { main: 10000, ambient: 3000, floating: 1000 };
        this.time = 0;
        this.animationSpeed = 1.0;
        this.rotationSpeed = 1.0;
        this.isRotating = false;
        this.systems = [];
        this.init();
    }

    init() {
        const [category, type] = this.artStyle.split(':');
        if (category === 'flower') this.createFlower(type);
        this.createAmbientParticles();
        this.createFloatingParticles();
    }

    createFlower(type) {
        const configs = {
            rose: { 
                totalParticles: 4800, // Optimized for performance (under 5000)
                petalCount: 25, // 20-30 petals as requested
                spiralLayers: 12, // Multi-layer spiral structure
                colors: {
                    center: 0xE62850, // Deep red center
                    edge: 0xFFBED2   // Light pink edge
                }
            },
            sakura: { 
                totalParticles: 3600, 
                petalCount: 8, 
                spiralLayers: 6,
                colors: { center: 0xffc0cb, edge: 0xffd0e4 }
            },
            lily: { 
                totalParticles: 4200, 
                petalCount: 12, 
                spiralLayers: 8,
                colors: { center: 0xfffacd, edge: 0xfff8dc }
            }
        };
        
        const config = configs[type] || configs.rose;
        
        for (let i = 0; i < 5; i++) {
            const flower = this.createSingleFlower(config, i);
            this.systems.push(flower);
            this.scene.add(flower);
        }
    }

    createSingleFlower(config, index) {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(config.totalParticles * 3);
        const colors = new Float32Array(config.totalParticles * 3);
        const sizes = new Float32Array(config.totalParticles);
        
        const center = new THREE.Vector3((Math.random()-0.5)*100, Math.random()*30-15, (Math.random()-0.5)*100);
        
        // Golden ratio for natural spiral
        const goldenAngle = Math.PI * (3.0 - Math.sqrt(5.0));
        
        for (let i = 0; i < config.totalParticles; i++) {
            // Spiral distribution using golden ratio
            const spiralRadius = Math.sqrt(i / config.totalParticles) * 3.0; // 0 to 3 units
            const spiralAngle = i * goldenAngle;
            
            // Multi-layer spiral structure (12 layers)
            const layerIndex = Math.floor(i / (config.totalParticles / config.spiralLayers));
            const layerProgress = layerIndex / (config.spiralLayers - 1);
            
            // Petal assignment using Fibonacci spiral
            const petalPhase = (spiralAngle + layerProgress * Math.PI * 0.3) % (Math.PI * 2);
            const petalIndex = Math.floor((petalPhase / (Math.PI * 2)) * config.petalCount);
            const petalCenter = (petalIndex / config.petalCount) * Math.PI * 2;
            
            // Distance from petal center for shape definition
            const petalAngleDiff = Math.abs(petalPhase - petalCenter);
            const normalizedPetalDiff = Math.min(petalAngleDiff, Math.PI * 2 - petalAngleDiff);
            const petalDistance = normalizedPetalDiff / (Math.PI / config.petalCount);
            
            // Petal strength (1 = center, 0 = edge)
            const petalStrength = Math.max(0, 1 - petalDistance * 1.5);
            
            // 3D positioning with spiral and petal structure
            const finalRadius = spiralRadius * (0.4 + 0.6 * petalStrength);
            const finalAngle = spiralAngle + layerProgress * 0.2;
            
            // Enhanced Z-axis thickness for petal width (adjustable via UI: 0.05-0.3 range)
            const basePetalWidth = 0.15; // Default petal width (can be controlled by UI)
            const petalWidth = basePetalWidth + basePetalWidth * petalStrength; 
            const thickness = petalWidth * (Math.random() - 0.5) + layerProgress * 0.05;
            
            // Height with inward curling toward center
            const curlFactor = Math.pow(1 - spiralRadius / 3.0, 1.5);
            const height = layerProgress * 2.0 + curlFactor * 0.8;
            
            // Final positioning
            positions[i * 3] = center.x + finalRadius * Math.cos(finalAngle);
            positions[i * 3 + 1] = center.y + height;
            positions[i * 3 + 2] = center.z + finalRadius * Math.sin(finalAngle) + thickness;
            
            // 3-color radial gradient: center=#E62850 → middle=#FF8FB3 → edge=#FFBED2
            const centerColor = new THREE.Color(0xE62850);
            const middleColor = new THREE.Color(0xFF8FB3);
            const edgeColor = new THREE.Color(0xFFBED2);
            const radialDistance = spiralRadius / 3.0; // 0 to 1
            
            // Adjustable mid color position (default 0.5, UI range: 0.2-0.8)
            const midColorPosition = 0.5; // Can be controlled by UI slider
            
            let finalColor;
            if (radialDistance < midColorPosition) {
                // Center to middle transition
                const t = radialDistance / midColorPosition; // 0 to 1
                finalColor = centerColor.clone().lerp(middleColor, t);
            } else {
                // Middle to edge transition
                const t = (radialDistance - midColorPosition) / (1 - midColorPosition); // 0 to 1
                finalColor = middleColor.clone().lerp(edgeColor, t);
            }
            
            // Apply petal brightness variation
            const petalBrightness = 0.6 + 0.4 * petalStrength;
            finalColor.multiplyScalar(petalBrightness);
            
            colors[i * 3] = finalColor.r;
            colors[i * 3 + 1] = finalColor.g;
            colors[i * 3 + 2] = finalColor.b;
            
            // Size variation: center=0.02, edge=0.005 (much smaller range)
            sizes[i] = 0.02 - 0.015 * radialDistance;
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        
        const material = new THREE.PointsMaterial({
            sizeAttenuation: true, vertexColors: true, transparent: true, opacity: 0.95,
            blending: THREE.AdditiveBlending, depthWrite: false
        });
        
        return new THREE.Points(geometry, material);
    }

    createAmbientParticles() {
        const particleCount = 3000;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 100;
            positions[i * 3 + 1] = Math.random() * 40 - 20;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 100;
            
            const color = new THREE.Color();
            color.setHSL(0.1 + Math.random() * 0.1, 0.3, 0.8);
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: 0.2, vertexColors: true, transparent: true, opacity: 0.4,
            blending: THREE.AdditiveBlending, depthWrite: false
        });

        const ambient = new THREE.Points(geometry, material);
        this.systems.push(ambient);
        this.scene.add(ambient);
    }

    createFloatingParticles() {
        const particleCount = 1000;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const velocities = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 80;
            positions[i * 3 + 1] = Math.random() * 30;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 80;
            
            velocities[i * 3] = (Math.random() - 0.5) * 0.1;
            velocities[i * 3 + 1] = Math.random() * 0.05;
            velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.1;
            
            const color = new THREE.Color(0xff69b4);
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: 0.8, vertexColors: true, transparent: true, opacity: 0.6,
            blending: THREE.NormalBlending, depthWrite: false
        });

        const floating = new THREE.Points(geometry, material);
        floating.userData = { type: 'floating', velocities: velocities };
        this.systems.push(floating);
        this.scene.add(floating);
    }

    update(deltaTime) {
        this.time += deltaTime * this.animationSpeed;
        this.systems.forEach(system => {
            if (system.userData && system.userData.type === 'floating') {
                const positions = system.geometry.attributes.position.array;
                const velocities = system.userData.velocities;
                
                for (let i = 0; i < positions.length; i += 3) {
                    positions[i] += velocities[i] * deltaTime * 60 * this.animationSpeed;
                    positions[i + 1] += velocities[i + 1] * deltaTime * 60 * this.animationSpeed;
                    positions[i + 2] += velocities[i + 2] * deltaTime * 60 * this.animationSpeed;
                    
                    if (positions[i + 1] > 40) {
                        positions[i + 1] = -20;
                        positions[i] = (Math.random() - 0.5) * 80;
                        positions[i + 2] = (Math.random() - 0.5) * 80;
                    }
                }
                system.geometry.attributes.position.needsUpdate = true;
            } else if (system.userData && system.userData.type === 'flower') {
                // Only subtle floating animation for flowers
                system.position.y = Math.sin(this.time + system.userData.index) * 2;
            }
        });
    }

    updateControls(controls) {
        this.animationSpeed = controls.animationSpeed;
        this.rotationSpeed = controls.rotationSpeed || 1.0;
        this.systems.forEach(system => {
            if (system.userData && system.userData.type === 'flower') {
                system.material.size = controls.particleSize;
                system.material.opacity = controls.roseOpacity;
            } else if (system.userData && system.userData.type === 'ambient') {
                system.material.opacity = controls.ambientOpacity;
            }
        });
    }

    toggleRotation() {
        this.isRotating = !this.isRotating;
    }
    
    updateCameraRotation(camera, deltaTime) {
        if (this.isRotating) {
            // Rotate camera around scene center
            const radius = Math.sqrt(camera.position.x * camera.position.x + camera.position.z * camera.position.z);
            const currentAngle = Math.atan2(camera.position.z, camera.position.x);
            const newAngle = currentAngle + this.rotationSpeed * deltaTime;
            
            camera.position.x = radius * Math.cos(newAngle);
            camera.position.z = radius * Math.sin(newAngle);
            camera.lookAt(0, 0, 0);
        }
    }
}

IMPLEMENTATION REQUIREMENTS:
- Use the EnhancedParticleSystem class above
- Initialize with: new EnhancedParticleSystem(scene, { artStyle: '$ART_STYLE' })
- In animation loop: call particleSystem.update(deltaTime) AND particleSystem.updateCameraRotation(camera, deltaTime)
- Double-click canvas calls: particleSystem.toggleRotation()
- High particle density for realistic flower shapes
- Mathematical petal arrangements
- Layer-based opacity and colors"

# 音楽・操作（圧縮版）
[ "$INCLUDE_MUSIC" = "true" ] && PROMPT="$PROMPT
Music: 'generated-music.wav', user-click play, loop
CRITICAL MUSIC PATH FIX: 
- Music file path must be EXACTLY 'generated-music.wav' (same directory as index.html)
- DO NOT use '../music/generated-music.wav' or any other path
- Panorama image path must be 'assets/panorama.jpg' (in assets subdirectory)
- Ensure assets folder exists and panorama is copied during integration"

PROMPT="$PROMPT
Controls: mouse drag/zoom, interactive sliders, responsive

CRITICAL FEATURES:
1. MOUSE CONTROLS (ESSENTIAL):
   - Mouse drag: Rotate camera view around scene center
   - Mouse wheel: Zoom in/out 
   - MUST work smoothly and responsively

2. ANIMATION CONTROLS:
   - Animation Speed slider (0.1-3.0): Controls particle floating/movement speed
   - Rotation Speed slider (0.1-5.0): Controls camera/scene rotation speed

3. CAMERA ROTATION:
   - Double-click canvas: Start/stop automatic camera rotation around scene
   - Camera rotates around Y-axis, NOT individual flowers
   - Individual flowers should only float up/down subtly

4. UI CONTROLS:
   - Particle Size, Animation Speed, Rotation Speed, Rose Opacity, Ambient Opacity
   - Petal Width (0.05-0.3): Controls Z-axis thickness of petals
   - Mid Color Position (0.2-0.8): Controls where middle gradient color appears

IMPLEMENTATION REQUIREMENTS:
- ESSENTIAL: Mouse drag for camera control must work
- ESSENTIAL: Mouse wheel zoom must work  
- Double-click toggles camera rotation (not flower rotation)
- Animation Speed affects floating particles only
- Rotation Speed affects camera rotation only

WebGL Shader Requirements:
- Use BasicMaterial or PointsMaterial instead of custom ShaderMaterial
- If custom shaders needed, use these exact patterns:
  * uniform float uTime (NOT time)
  * uniform float uSize (NOT size)  
  * attribute float aScale (NOT size or particleSize)
- NEVER define 'attribute vec3 color' (THREE.js provides it)
- NEVER use 'as' keyword in shader code

Particle Shape Implementation:
- circle: Use PointsMaterial with transparent canvas texture, proper alpha blending
- heart/star/diamond: Generate custom shape textures with FULLY TRANSPARENT backgrounds
  * CRITICAL: Use canvas clearRect() or fillStyle='transparent' for background
  * Set canvas context.globalCompositeOperation = 'source-over'
  * Ensure PointsMaterial has transparent: true, alphaTest: 0.1
  * Background MUST be transparent (alpha=0), not white or any color
- square: Simple square texture (for pixel art effect)
- soft_circle: Gradient circle with soft edges

TRANSPARENCY REQUIREMENTS:
- All custom particle shapes MUST have completely transparent backgrounds
- Never use white, black, or any solid color as particle background
- Canvas background should be fully transparent (rgba(0,0,0,0))
- Use proper alpha blending: material.transparent = true, material.alphaTest = 0.1"

echo "🚀 Starting Three.js Scene Generation Agent..."
echo "📝 Prompt length: ${#PROMPT} characters"

# Claude Code CLI（最適化版）
npx @anthropic-ai/claude-code \
  --allowedTools "Write" \
  --max-turns 8 \
  --permission-mode "acceptEdits" \
  -p "$PROMPT"

# 生成されたファイルの確認
echo ""
echo "📸 Checking generated Three.js files..."
if [ -f "$SRC_DIR/index.html" ]; then
  echo "✅ Main HTML file created: $SRC_DIR/index.html"
  HTML_SIZE=$(wc -c < "$SRC_DIR/index.html")
  echo "  HTML file size: $HTML_SIZE bytes"
else
  echo "::error::❌ Main HTML file not found at $SRC_DIR/index.html"
  exit 1
fi

TOTAL_FILES=$(find "$SRC_DIR" -type f | wc -l)
echo "scene-files-created=$TOTAL_FILES" >> $GITHUB_OUTPUT
echo "completed=true" >> $GITHUB_OUTPUT
echo "::endgroup::"