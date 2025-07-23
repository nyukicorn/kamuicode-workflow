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

// TEMPLATE 1: Rose Bouquet System (InstancedMesh-based for realistic flower recognition)
class RoseBouquetSystem {
    constructor(scene, config = {}) {
        this.scene = scene;
        this.artStyle = config.artStyle || '$ART_STYLE';
        this.time = 0;
        this.animationSpeed = 1.0;
        this.rotationSpeed = 1.0;
        this.isRotating = false;
        this.systems = [];
        this.petalWidth = 0.05; // Controllable via UI (0.05-0.3)
        this.particleSize = 0.01; // Much smaller default (0.005-0.02 range)
        this.init();
    }

    init() {
        const [category, type] = this.artStyle.split(':');
        if (category === 'flower') this.createRoseBouquet(type);
        this.createAmbientParticles();
        this.createFloatingParticles();
    }

    createRoseBouquet(type) {
        // Create single rose head mesh (15-25 curved plate petals)
        const roseHeadGeometry = this.createRoseHeadGeometry();
        const roseMaterial = new THREE.MeshStandardMaterial({
            color: 0xE62850,
            metalness: 0.1,
            roughness: 0.8,
            transparent: true,
            opacity: 0.9
        });
        
        // Create 5 rose heads in bouquet arrangement
        const bouquetPositions = [
            new THREE.Vector3(-2, 2, 0),   // Left top
            new THREE.Vector3(2, 2, 0),    // Right top  
            new THREE.Vector3(-3, 0, 0),   // Left middle
            new THREE.Vector3(3, 0, 0),    // Right middle
            new THREE.Vector3(0, 1, 0)     // Center
        ];
        
        bouquetPositions.forEach((position, index) => {
            let roseHead;
            if (roseHeadGeometry instanceof THREE.Group) {
                // If geometry is a group (fallback case), clone the group
                roseHead = roseHeadGeometry.clone();
                roseHead.children.forEach(child => {
                    child.material = child.material.clone();
                });
            } else {
                // If geometry is merged, create a single mesh
                roseHead = new THREE.Mesh(roseHeadGeometry, roseMaterial.clone());
            }
            
            roseHead.position.copy(position);
            roseHead.rotation.y = (Math.PI * 2 / 5) * index; // Rotate each head slightly
            roseHead.userData = { type: 'rose', index: index };
            this.systems.push(roseHead);
            this.scene.add(roseHead);
        });
        
        // Add stems
        this.createStems(bouquetPositions);
    }

    createRoseHeadGeometry() {
        const group = new THREE.Group();
        const petalCount = 20; // 15-25 petals
        const goldenAngle = Math.PI * (3.0 - Math.sqrt(5.0));
        
        for (let i = 0; i < petalCount; i++) {
            // Spiral positioning using golden ratio
            const spiralRadius = Math.sqrt(i / petalCount) * 1.5;
            const spiralAngle = i * goldenAngle;
            const layerHeight = (i / petalCount) * 0.8;
            
            // Create curved plate petal geometry
            const petalGeometry = new THREE.PlaneGeometry(this.petalWidth * 2, this.petalWidth * 3, 4, 6);
            
            // Apply curvature to petal
            const positions = petalGeometry.attributes.position.array;
            for (let j = 0; j < positions.length; j += 3) {
                const x = positions[j];
                const y = positions[j + 1];
                // Add curvature: more curve at edges
                positions[j + 2] = Math.sin(x / this.petalWidth) * 0.02 + Math.cos(y / this.petalWidth) * 0.01;
            }
            petalGeometry.attributes.position.needsUpdate = true;
            petalGeometry.computeVertexNormals();
            
            const petal = new THREE.Mesh(petalGeometry, new THREE.MeshStandardMaterial({
                color: new THREE.Color().lerpColors(
                    new THREE.Color(0xE62850), 
                    new THREE.Color(0xFFBED2), 
                    spiralRadius / 1.5
                ),
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.9
            }));
            
            // Position petal in spiral
            petal.position.set(
                spiralRadius * Math.cos(spiralAngle),
                layerHeight,
                spiralRadius * Math.sin(spiralAngle)
            );
            petal.rotation.z = spiralAngle + Math.PI / 2;
            petal.rotation.x = -Math.PI / 6 + (spiralRadius / 1.5) * Math.PI / 4; // Curl inward
            
            group.add(petal);
        }
        
        // Convert group to single geometry for performance
        // Note: BufferGeometryUtils.mergeGeometries may not be available in all Three.js versions
        // Alternative: return the group directly, or use InstancedMesh
        const mergedGeometry = new THREE.BufferGeometry();
        const geometries = [];
        group.children.forEach(child => {
            child.updateMatrix();
            const geo = child.geometry.clone();
            geo.applyMatrix4(child.matrix);
            geometries.push(geo);
        });
        
        // Try to use BufferGeometryUtils.mergeGeometries if available, otherwise return first geometry
        if (typeof THREE.BufferGeometryUtils !== 'undefined' && THREE.BufferGeometryUtils.mergeGeometries) {
            return THREE.BufferGeometryUtils.mergeGeometries(geometries);
        } else {
            // Fallback: return the group as-is for individual mesh rendering
            return group;
        }
    }
    
    createStems(positions) {
        positions.forEach((position, index) => {
            const stemGeometry = new THREE.CylinderGeometry(0.05, 0.05, 4, 8);
            const stemMaterial = new THREE.MeshStandardMaterial({
                color: 0x2d5016,
                roughness: 0.9
            });
            const stem = new THREE.Mesh(stemGeometry, stemMaterial);
            stem.position.set(position.x, position.y - 2, position.z);
            stem.userData = { type: 'stem', index: index };
            this.systems.push(stem);
            this.scene.add(stem);
        });
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
        
        // Update petal width if provided
        if (controls.petalWidth !== undefined) {
            this.petalWidth = controls.petalWidth;
        }
        
        // Update particle size for ambient particles
        if (controls.particleSize !== undefined) {
            this.particleSize = Math.max(0.005, Math.min(0.02, controls.particleSize));
        }
        
        this.systems.forEach(system => {
            if (system.userData && system.userData.type === 'rose') {
                system.material.opacity = controls.roseOpacity || 0.9;
                if (controls.roseColor) {
                    system.material.color.setHex(controls.roseColor);
                }
            } else if (system.userData && system.userData.type === 'stem') {
                system.material.opacity = controls.stemOpacity || 1.0;
            } else if (system.userData && system.userData.type === 'ambient') {
                system.material.opacity = controls.ambientOpacity || 0.4;
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
- Use the RoseBouquetSystem class above (InstancedMesh-based for realistic flower recognition)
- Initialize with: new RoseBouquetSystem(scene, { artStyle: '$ART_STYLE' })
- In animation loop: call bouquetSystem.update(deltaTime) AND bouquetSystem.updateCameraRotation(camera, deltaTime)
- Double-click canvas calls: bouquetSystem.toggleRotation()
- CRITICAL: Set camera position further back to show entire bouquet (position: [0, 0, 15] or more distant)
- CRITICAL LIGHTING: Add DirectionalLight and AmbientLight for MeshStandardMaterial rendering
  * const ambientLight = new THREE.AmbientLight(0xffffff, 0.4); scene.add(ambientLight);
  * const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8); directionalLight.position.set(10, 10, 5); scene.add(directionalLight);
- 5 rose heads arranged in bouquet formation with individual stems
- Each rose head: 20 curved plate petals using PlaneGeometry with applied curvature
- MeshStandardMaterial for realistic lighting and depth (requires proper lighting setup)
- Performance optimized: merged geometries when possible, under 8000 vertices total  
- UI Controls include: Petal Width (0.05-0.3), Particle Size (0.005-0.02), Rose Opacity, Stem Opacity"

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
   - Particle Size (0.005-0.02): Controls ambient particle size (MUCH SMALLER range)
   - Animation Speed, Rotation Speed, Rose Opacity, Ambient Opacity
   - Petal Width (0.05-0.3): Controls width of individual rose petals
   - Stem Opacity (0.0-1.0): Controls visibility of flower stems
   - Rose Color: Primary color of rose petals (default: #E62850)

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