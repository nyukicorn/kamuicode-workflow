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

LIGHTWEIGHT ENHANCED PARTICLE SYSTEM - COPY THESE TEMPLATES:

1. Include these JavaScript classes directly in HTML:

// TEMPLATE 1: Enhanced Particle System (Lightweight Version)
class EnhancedParticleSystem {
    constructor(scene, config = {}) {
        this.scene = scene;
        this.artStyle = config.artStyle || '$ART_STYLE';
        this.particleCount = { main: 4000, ambient: 1200, floating: 400 };
        this.time = 0;
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
            rose: { layers: 5, particlesPerLayer: 800, colors: [0xff69b4, 0xff1493, 0xdc143c] },
            sakura: { layers: 4, particlesPerLayer: 1000, colors: [0xffb6c1, 0xffc0cb, 0xffd0e4] },
            lily: { layers: 5, particlesPerLayer: 800, colors: [0xffffff, 0xfffacd, 0xf0e68c] }
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
        const positions = new Float32Array(config.layers * config.particlesPerLayer * 3);
        const colors = new Float32Array(config.layers * config.particlesPerLayer * 3);
        
        const center = new THREE.Vector3((Math.random()-0.5)*100, Math.random()*30-15, (Math.random()-0.5)*100);
        
        let particleIndex = 0;
        for (let layer = 0; layer < config.layers; layer++) {
            for (let i = 0; i < config.particlesPerLayer; i++) {
                const angle = (i / config.particlesPerLayer) * Math.PI * 2;
                const radius = (layer + 1) * 0.8 * (Math.sin(5 * angle) * 0.5 + 1);
                
                positions[particleIndex * 3] = center.x + radius * Math.cos(angle);
                positions[particleIndex * 3 + 1] = center.y + layer * 0.1;
                positions[particleIndex * 3 + 2] = center.z + radius * Math.sin(angle);
                
                const color = new THREE.Color(config.colors[Math.floor(Math.random() * config.colors.length)]);
                colors[particleIndex * 3] = color.r;
                colors[particleIndex * 3 + 1] = color.g;
                colors[particleIndex * 3 + 2] = color.b;
                
                particleIndex++;
            }
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        
        const material = new THREE.PointsMaterial({
            size: 0.5, vertexColors: true, transparent: true, opacity: 0.8,
            blending: THREE.AdditiveBlending, depthWrite: false
        });
        
        return new THREE.Points(geometry, material);
    }

    createAmbientParticles() {
        const particleCount = 1200;
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
        const particleCount = 400;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 80;
            positions[i * 3 + 1] = Math.random() * 30;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 80;
            
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
        floating.userData = { type: 'floating' };
        this.systems.push(floating);
        this.scene.add(floating);
    }

    update(deltaTime) {
        this.time += deltaTime;
        this.systems.forEach(system => {
            if (system.userData && system.userData.type === 'floating') {
                // Update floating particles
            }
        });
    }
}

IMPLEMENTATION REQUIREMENTS:
- Use the EnhancedParticleSystem class above
- Initialize with: new EnhancedParticleSystem(scene, { artStyle: '$ART_STYLE' })
- Call update() in animation loop
- High particle density for realistic flower shapes
- Mathematical petal arrangements
- Layer-based opacity and colors"

# 音楽・操作（圧縮版）
[ "$INCLUDE_MUSIC" = "true" ] && PROMPT="$PROMPT
Music: './generated-music.wav', user-click play, loop"

PROMPT="$PROMPT
Controls: mouse drag/zoom, interactive sliders, responsive

MANDATORY WebGL Shader Requirements:
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