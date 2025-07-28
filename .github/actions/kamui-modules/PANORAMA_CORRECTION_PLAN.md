# 🌐 パノラマビューアー修正計画

## 📅 計画策定日
2025-07-28

## 🎯 修正目標

**正しい仕様**:
```
360度パノラマ画像 → MiDaS深度推定 → 深度情報付き球面3Dパーティクル配置 → 360度体験
```

**現在の問題実装**:
```
パノラマ画像 → ピクセル色抽出 → 平面的球面配置 (深度情報なし)
```

---

## 🔍 Phase 1: 現状分析と設計 (30分)

### 1.1 既存システム分析
- ✅ pointcloud-generation モジュール詳細調査
- ✅ MiDaS深度推定の出力形式確認  
- ✅ 既存2D→3D変換プロセス解析
- ✅ 球面座標系での深度情報活用方法設計

### 1.2 統合アーキテクチャ設計
```
[360°パノラマ画像] 
    ↓
[pointcloud-generation] 
    ├─ MiDaS深度推定
    ├─ 深度マップ生成  
    └─ 球面座標変換準備
    ↓
[panorama-viewer]
    ├─ 深度情報付き球面配置
    ├─ 真の3Dパーティクル生成
    └─ 360度インタラクション
```

### 1.3 データフロー設計
```javascript
// 入力: 360度パノラマ画像
panoramaImage (equirectangular projection)
    ↓
// Step 1: 深度推定
depthMap = midas_depth_estimation(panoramaImage)
    ↓  
// Step 2: 球面座標変換
sphericalPoints = equirectangular_to_sphere(panoramaImage, depthMap)
    ↓
// Step 3: 3Dパーティクル配置
particles = generate_3d_particles(sphericalPoints)
```

---

## 🔧 Phase 2: pointcloud-generation 拡張 (45分)

### 2.1 パノラマ対応モジュール作成
**新規ファイル**: `pointcloud-panorama-generation/action.yml`

#### 主要機能:
- 360度パノラマ画像の入力対応
- equirectangular projection → spherical coordinates変換
- MiDaS深度推定のパノラマ最適化
- 球面配置用PLYファイル生成

#### 技術仕様:
```yaml
inputs:
  panorama-image-path:
    description: '360度パノラマ画像パス (equirectangular projection)'
    required: true
  sphere-radius:
    description: '球面半径設定'
    default: '200'
  depth-resolution:
    description: '深度解析解像度'
    default: '1024x512'
```

### 2.2 球面座標変換アルゴリズム
```javascript
// equirectangular → spherical coordinates
function equirectangularToSphere(u, v, depthValue, radius) {
    const phi = u * 2 * Math.PI;           // longitude: 0 to 2π
    const theta = v * Math.PI;             // latitude: 0 to π
    
    // 深度情報による半径調整
    const adjustedRadius = radius * (1 + depthValue * 0.5);
    
    return {
        x: adjustedRadius * Math.sin(theta) * Math.cos(phi),
        y: adjustedRadius * Math.cos(theta),
        z: adjustedRadius * Math.sin(theta) * Math.sin(phi)
    };
}
```

---

## ⚡ Phase 3: panorama-viewer 修正 (60分)

### 3.1 現在のpanorama-script.js修正
**修正対象**: 
- `createSphericalParticleSystem()` 関数
- 深度情報統合
- MiDaS出力データの活用

### 3.2 新しい処理フロー
```javascript
// 修正後のフロー
async function loadPanoramaWithDepth() {
    // 1. パノラマ画像読み込み
    const panoramaImage = await loadPanoramaImage();
    
    // 2. 深度推定実行 (pointcloud-generation連携)
    const depthData = await processPanoramaDepth(panoramaImage);
    
    // 3. 深度情報付き球面パーティクル生成
    const particles = await createDepthSphericalParticles(panoramaImage, depthData);
    
    // 4. 3Dシーン配置
    scene.add(particles);
}
```

### 3.3 深度情報統合の実装
```javascript
function createDepthSphericalParticles(imageData, depthData) {
    const positions = [];
    const colors = [];
    
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const u = x / width;          // 0 to 1
            const v = y / height;         // 0 to 1
            
            // 深度値取得 (0-1正規化)
            const depth = getDepthValue(depthData, x, y);
            
            // 球面座標変換（深度情報付き）
            const spherePos = equirectangularToSphere(u, v, depth, sphereRadius);
            
            positions.push(spherePos.x, spherePos.y, spherePos.z);
            
            // 元画像の色情報
            const color = getImageColor(imageData, x, y);
            colors.push(color.r, color.g, color.b);
        }
    }
    
    return createParticleGeometry(positions, colors);
}
```

---

## 🧪 Phase 4: 統合テスト環境構築 (30分)

### 4.1 結合テストスイート作成
**新規ファイル**: `test-panorama-depth-integration.html`

#### テスト項目:
- ✅ パノラマ画像読み込み
- ✅ 深度推定処理
- ✅ 球面座標変換精度
- ✅ 3Dパーティクル配置確認
- ✅ パフォーマンス測定

### 4.2 回帰テスト環境
**新規ファイル**: `test-2d-3d-regression.html`

#### 検証項目:
- ✅ 既存2D→3D機能の動作確認
- ✅ モジュール分割後の互換性
- ✅ pointcloud-generation単体動作
- ✅ パフォーマンス比較

---

## 🚀 Phase 5: ワークフロー統合 (45分)

### 5.1 GitHub Actions ワークフロー
**新規ファイル**: `.github/workflows/panorama-generation-test.yml`

```yaml
name: 'Panorama 3D Generation Test'
on:
  workflow_dispatch:
    inputs:
      panorama_image:
        description: '360度パノラマ画像パス'
        required: true
      
jobs:
  generate-panorama-3d:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate 3D Panorama
        uses: ./.github/actions/kamui-modules/pointcloud-panorama-generation
        with:
          panorama-image-path: ${{ inputs.panorama_image }}
          sphere-radius: '200'
          
      - name: Create Panorama Viewer
        uses: ./.github/actions/kamui-modules/threejs-panorama-viewer  
        with:
          input_image: ${{ steps.generate.outputs.panorama-ply-path }}
          enable_depth: 'true'
```

### 5.2 統合動作確認
- ✅ End-to-Endワークフロー実行
- ✅ 3Dパーティクル品質確認  
- ✅ インタラクション動作確認

---

## 📊 実装優先順位

### 🔴 最高優先度 (Phase 1-2)
1. **現状分析**: pointcloud-generation詳細調査
2. **アーキテクチャ設計**: 統合方式の確定
3. **パノラマ対応モジュール**: 基本機能実装

### 🟡 高優先度 (Phase 3-4) 
4. **panorama-viewer修正**: 深度情報統合
5. **統合テスト**: 結合動作確認

### 🟢 中優先度 (Phase 5)
6. **ワークフロー統合**: GitHub Actions対応
7. **パフォーマンス最適化**: 大容量パノラマ対応

---

## ⏱️ 推定作業時間

| Phase | 内容 | 予想時間 | 累計 |
|-------|------|----------|------|
| Phase 1 | 現状分析・設計 | 30分 | 30分 |
| Phase 2 | pointcloud-generation拡張 | 45分 | 1時間15分 |
| Phase 3 | panorama-viewer修正 | 60分 | 2時間15分 |
| Phase 4 | 統合テスト構築 | 30分 | 2時間45分 |
| Phase 5 | ワークフロー統合 | 45分 ⭐ | 3時間30分 |

**合計推定時間**: 約3.5時間

---

## 🎯 成功基準

### ✅ 機能要件
- [ ] 360度パノラマ画像から深度情報付き3Dパーティクル生成
- [ ] 既存2D→3D機能の互換性維持
- [ ] 球面座標系での正確な3D配置
- [ ] 60FPS動作 (25,000パーティクル)

### ✅ 品質要件  
- [ ] 単体テスト: 全モジュール個別動作確認
- [ ] 統合テスト: End-to-End動作確認
- [ ] 回帰テスト: 既存機能の非劣化確認
- [ ] パフォーマンステスト: フレームレート維持

### ✅ ユーザビリティ要件
- [ ] 直感的な360度操作
- [ ] 滑らかなパーティクルアニメーション  
- [ ] 高品質な視覚体験
- [ ] レスポンシブ対応

---

## 🤝 次のステップ

**Phase 1から開始しますか？**
1. pointcloud-generation の詳細調査
2. MiDaS深度推定の出力形式確認
3. 球面座標統合アーキテクチャの確定

この計画で進めてよろしいでしょうか？何かご不明な点や修正すべき点があればお聞かせください。