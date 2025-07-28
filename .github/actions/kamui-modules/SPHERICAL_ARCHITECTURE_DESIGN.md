# 🌐 球面座標系統合アーキテクチャ設計

## 📋 Phase 1 分析結果

### ✅ 既存システム理解完了

#### 🔍 pointcloud-generation 詳細分析
**ファイル構成**:
- `simple_depth_test.py`: 画像 → 深度マップ (PNG)
- `depth2ply.js`: 深度マップ + 色情報 → PLY点群ファイル

**座標変換**:
```javascript
// 既存の平面座標変換 (depth2ply.js)
worldX = (x - width/2) * spacing     // 中心原点の平面X
worldY = -(y - height/2) * spacing   // Y軸反転の平面Y  
worldZ = (1.0 - depth) * depthScale  // 深度値をZ座標に
```

**PLY出力形式**:
```
vertex_count: 65536点
format: x y z r g b (float float float uchar uchar uchar)
例: -256.000000 256.000000 75.686275 41 32 24
```

#### 🎯 MiDaS深度推定出力
**ファイル形式**:
- `depth.png`: カラー可視化深度マップ  
- `depth_gray.png`: グレースケール深度値 (0-255)

**深度値の意味**:
- 0 (黒): 最も遠い
- 255 (白): 最も近い
- 中間値: 距離に比例

---

## 🎯 パノラマ統合アーキテクチャ

### 新しいデータフロー設計

```
[360°パノラマ画像] (equirectangular projection)
    ↓
[panorama-depth-estimation] (Python) 
    ├─ パノラマ専用MiDaS処理
    ├─ equirectangular → depth map  
    └─ パノラマ深度マップ出力
    ↓
[panorama-ply-generation] (Node.js)
    ├─ 深度マップ読み込み
    ├─ equirectangular → spherical 座標変換
    ├─ 深度情報による半径調整
    └─ 球面PLYファイル生成
    ↓
[panorama-viewer] (JavaScript)
    ├─ 球面PLY読み込み
    ├─ Three.js球面配置
    └─ 360度インタラクション
```

### 🧮 球面座標変換アルゴリズム

#### 基本変換公式
```javascript
// equirectangular (u,v) → spherical coordinates
function equirectangularToSphere(u, v, depthValue, baseRadius) {
    // u: 0-1 (画像X座標正規化) → longitude 0-2π
    // v: 0-1 (画像Y座標正規化) → latitude 0-π
    
    const phi = u * 2 * Math.PI;           // 経度: 0 to 2π
    const theta = v * Math.PI;             // 緯度: 0 to π
    
    // 深度による半径調整 (重要!)
    const depthFactor = 1.0 - (depthValue / 255.0); // 0-1正規化
    const adjustedRadius = baseRadius * (0.8 + depthFactor * 0.4);
    
    // 球面座標 → 直交座標変換
    return {
        x: adjustedRadius * Math.sin(theta) * Math.cos(phi),
        y: adjustedRadius * Math.cos(theta), 
        z: adjustedRadius * Math.sin(theta) * Math.sin(phi)
    };
}
```

#### 深度情報の球面適用
```javascript
// 深度による立体感の表現方法
const DEPTH_MAPPING = {
    // 近い物体: 球面より外側に配置
    near: (depth) => baseRadius * (1.0 + depth * 0.3),
    
    // 遠い物体: 球面より内側に配置  
    far: (depth) => baseRadius * (0.7 + depth * 0.3),
    
    // 適応的: 深度分布に応じて調整
    adaptive: (depth, depthStats) => {
        const normalized = (depth - depthStats.min) / (depthStats.max - depthStats.min);
        return baseRadius * (0.6 + normalized * 0.8);
    }
};
```

---

## 🔧 実装仕様

### Module 1: panorama-depth-estimation.py
```python
def process_panorama_depth(panorama_path, output_path):
    """
    360度パノラマ画像の深度推定
    
    Input: equirectangular projection image (2:1 aspect ratio)
    Output: panorama_depth.png (same dimensions as input)
    """
    
    # 1. パノラマ画像読み込み
    panorama = load_panorama_image(panorama_path)
    
    # 2. MiDaS深度推定 (パノラマ最適化)
    depth_map = estimate_panorama_depth(panorama)
    
    # 3. パノラマ特有の処理
    # - equirectangular distortion compensation
    # - pole area (上下端) の深度補正
    # - seamline (左右端) の連続性保証
    depth_corrected = correct_panorama_distortion(depth_map)
    
    # 4. 出力
    save_depth_maps(depth_corrected, output_path)
```

### Module 2: panorama-ply-generator.js
```javascript
class PanoramaPLYGenerator extends DepthToPLYConverter {
    
    async convertPanoramaToSphere(depthPath, imagePath, options = {}) {
        const opts = {
            sphereRadius: 200,
            depthVariation: 0.4,    // 深度による半径変動幅
            poleCompression: 0.8,   // 極域圧縮率
            ...options
        };
        
        const points = [];
        
        // パノラマ画像とプしマップ読み込み
        const depthData = await this.loadPNG(depthPath);
        const imageData = await this.loadPNG(imagePath);
        
        const { width, height } = depthData;
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                // 正規化座標
                const u = x / width;   // 0-1
                const v = y / height;  // 0-1
                
                // 深度値取得
                const depthValue = depthData.data[(y * width + x) * 4];
                
                // 球面座標変換 (深度情報付き)
                const spherePos = this.equirectangularToSphere(
                    u, v, depthValue, opts.sphereRadius
                );
                
                // 色情報取得
                const colorIdx = (y * width + x) * 4;
                const r = imageData.data[colorIdx];
                const g = imageData.data[colorIdx + 1];
                const b = imageData.data[colorIdx + 2];
                
                points.push({
                    x: spherePos.x,
                    y: spherePos.y, 
                    z: spherePos.z,
                    r, g, b
                });
            }
        }
        
        return points;
    }
    
    equirectangularToSphere(u, v, depthValue, baseRadius) {
        const phi = u * 2 * Math.PI;
        const theta = v * Math.PI;
        
        // 深度による半径調整
        const depthFactor = 1.0 - (depthValue / 255.0);
        const adjustedRadius = baseRadius * (0.8 + depthFactor * 0.4);
        
        // 極域での圧縮補正
        const poleWeight = Math.sin(theta); // 0 at poles, 1 at equator
        const finalRadius = adjustedRadius * (0.9 + poleWeight * 0.1);
        
        return {
            x: finalRadius * Math.sin(theta) * Math.cos(phi),
            y: finalRadius * Math.cos(theta),
            z: finalRadius * Math.sin(theta) * Math.sin(phi)
        };
    }
}
```

### Module 3: panorama-viewer 統合
```javascript
// panorama-script.js の修正版
async function loadPanoramaWithDepth() {
    // 1. 球面PLYファイル読み込み
    const plyData = await loadSphericalPLY('assets/panorama-sphere.ply');
    
    // 2. Three.js パーティクルシステム作成
    const geometry = new THREE.BufferGeometry();
    
    // PLYデータを直接使用 (既に球面座標)
    const positions = extractPositions(plyData);
    const colors = extractColors(plyData);
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    // 3. カメラを球の中心に配置
    camera.position.set(0, 0, 0);
    controls.enablePan = false;  // パノラマ体験維持
    
    // 4. パーティクルシステム作成
    const particles = createParticleSystem(geometry, {
        size: particleSize,
        vertexColors: true,
        transparent: true
    });
    
    scene.add(particles);
    
    console.log('✅ 深度情報付きパノラマロード完了');
}
```

---

## 🎯 技術的な課題と解決策

### 課題1: equirectangular 歪み補正
**問題**: 極域 (上下端) でピクセル密度が極端に高い
**解決**: 緯度に応じたサンプリング密度調整
```javascript
const samplingRate = Math.sin(theta); // 極域で密度を下げる
if (Math.random() > samplingRate) continue; // 確率的間引き
```

### 課題2: パノラマ境界の連続性
**問題**: 左端と右端が繋がらない
**解決**: 境界域での座標補間処理
```javascript
if (u < 0.01 || u > 0.99) {
    // 境界域での特別処理
    applySeamlineCorrection(u, v, depthValue);
}
```

### 課題3: 深度マップの球面適用
**問題**: 平面深度情報の球面配置での意味
**解決**: 球面半径を深度で変調
```javascript
// 深度に応じた半径調整
const radiusVariation = baseRadius * 0.4; // 40%の変動幅
const finalRadius = baseRadius + (depthFactor - 0.5) * radiusVariation;
```

---

## 📊 パフォーマンス設計

### 目標仕様
- **パーティクル数**: 50,000-100,000 (高解像度パノラマ用)
- **フレームレート**: 60FPS維持  
- **メモリ使用量**: <200MB
- **読み込み時間**: <3秒

### 最適化戦略
1. **適応的サンプリング**: 重要度に応じた密度調整
2. **LOD (Level of Detail)**: 距離に応じた詳細度変更
3. **GPU活用**: WebGL shader による並列処理
4. **メモリ管理**: 不要データの即座解放

---

## 🎯 Phase 1 完了判定

### ✅ 達成項目
- [x] pointcloud-generation 完全理解
- [x] MiDaS深度推定出力形式確認  
- [x] 既存2D→3D変換プロセス解析
- [x] 球面座標統合アーキテクチャ設計完了

### 📋 設計成果物
- [x] 統合データフロー仕様
- [x] 球面座標変換アルゴリズム
- [x] 3モジュール実装仕様
- [x] 技術課題と解決策
- [x] パフォーマンス設計

---

## 🚀 Phase 2への移行準備

**次の実装項目**:
1. `pointcloud-panorama-generation/action.yml` 新規作成
2. `panorama-depth-estimation.py` 実装
3. `panorama-ply-generator.js` 実装  
4. 統合テスト環境準備

**Phase 1 → Phase 2 移行可能！** 🎯