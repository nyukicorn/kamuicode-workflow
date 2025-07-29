# 🌐 Immersive 360° Panorama Pointcloud Viewer

360度パノラマ画像をポイントクラウドパーティクルシステムで表示する没入型Three.jsビューアーモジュールです。深度推定技術とポイントクラウド変換を統合し、真の3D空間体験を提供します。

## 🎯 概要

このモジュールは**360度パノラマ→深度推定→ポイントクラウド→没入体験**のパイプラインを使用し、従来の平面パノラマ表示を超えた立体的なパーティクル空間体験を実現します。

### ✨ 主要機能

- **🌐 没入型360度体験**: 真の3D球面ポイントクラウド空間
- **🧠 深度推定統合**: MiDaS技術による自動深度マッピング
- **✨ ポイントクラウドパーティクル**: PLYファイル対応の立体パーティクル
- **🎨 インテリジェント色彩**: 深度情報に基づく色彩表現
- **🎵 オーディオリアクティブ**: 音楽・マイクロフォン対応
- **🖱️ 3Dインタラクション**: 立体重力効果、空間マウス操作
- **🎮 没入型UI**: VR風コントロールインターフェース
- **📱 クロスプラットフォーム**: 全デバイス対応

## 🏗️ 技術仕様

### アーキテクチャ
```
360度パノラマ画像 → 深度推定(MiDaS) → PLY変換 → 球面ポイントクラウド → 没入型表示
```

### 新機能: ポイントクラウドモード
- **自動深度推定**: 2Dパノラマから3D深度情報を生成
- **PLY統合**: 標準3Dファイル形式対応
- **フォールバック**: 深度生成失敗時は従来の画像モードに自動切り替え

### 共通コンポーネント統合
- `audio-reactive-system.js`: Web Audio API、周波数分析
- `camera-controls.js`: Three.jsカメラ、OrbitControls  
- `mouse-interaction.js`: 重力モード、マウストレイル
- `particle-effects.js`: 深度効果、色彩調整
- `ui-controls.js`: 自動隠しUI、キーボードショートカット

### 技術要件
- **Three.js**: r128
- **WebGL**: 対応ブラウザ必須
- **Web Audio API**: オーディオ機能用（オプション）
- **Canvas API**: 画像分析用

## 🚀 使用方法

### GitHub Actions での使用

```yaml
- name: Create Immersive 360° Panorama Pointcloud Viewer
  uses: ./.github/actions/kamui-modules/threejs-panorama-viewer
  with:
    input_image: 'path/to/panorama.jpg'
    enable_pointcloud_mode: 'true'
    depth_model: 'midas_v21_small'
    color_mode: 'color'
    output_folder: 'docs/my-panorama'
    output_filename: 'index.html'
    background_color: '#000814'
    particle_density: 'high'
    auto_rotate: 'true'
    rotation_speed: '1.5'
    enable_music: 'true'
    music_file: 'path/to/music.mp3'
    branch_name: 'main'
```

### ワークフロー統合
完全なワークフローは `create-immersive-panorama-pointcloud-experience.yml` を使用：
```yaml
# 自動でパノラマ画像生成→ポイントクラウド変換→没入ビューアー作成
- 360度パノラマプロンプト入力
- AI画像生成 (Imagen4等)
- 自動深度推定・PLY変換
- 音楽生成 (オプション)
- 没入型ビューアー生成
```

### 入力パラメータ

| パラメータ | 説明 | デフォルト | 必須 |
|-----------|------|-----------|------|
| `input_image` | 360度パノラマ画像ファイル | - | ❌ |
| `ply_file_path` | 事前生成PLYファイル（オプション） | - | ❌ |
| `enable_pointcloud_mode` | ポイントクラウドモード有効化 | `true` | ❌ |
| `depth_model` | 深度推定モデル | `midas_v21_small` | ❌ |
| `color_mode` | 色彩モード (color/monochrome/sepia) | `color` | ❌ |
| `output_folder` | 出力フォルダ | - | ✅ |
| `output_filename` | 出力HTMLファイル名 | `panorama-viewer.html` | ❌ |
| `background_color` | 背景色（hex形式） | `#000814` | ❌ |
| `camera_position_radius` | カメラ初期位置半径 | `100` | ❌ |
| `particle_density` | パーティクル密度 (low/medium/high) | `medium` | ❌ |
| `auto_rotate` | 自動回転有効化 | `true` | ❌ |
| `rotation_speed` | 自動回転速度 | `1.0` | ❌ |
| `enable_music` | 音楽統合有効化 | `false` | ❌ |
| `music_file` | 音楽ファイル | - | ❌ |
| `branch_name` | Gitブランチ名 | `main` | ❌ |

## 🧪 テスト方法

### ローカルテストサーバー起動
```bash
cd .github/actions/kamui-modules/threejs-panorama-viewer
./test-panorama-server.sh
```

### テストURL
- **パノラマテスト**: http://localhost:8001/test-panorama-viewer.html

### テスト項目
1. **球面パーティクル表示**: 360度パノラマ効果確認
2. **マウス操作**: オービット、ズーム、パン
3. **キーボード操作**: WASD移動、スペース回転切替
4. **共通コンポーネント**: 重力、オーディオ、UI統合
5. **パフォーマンス**: 25,000パーティクルでの動作確認

## 🎮 操作方法

### マウス操作
- **左ドラッグ**: カメラ回転（360度オービット）
- **スクロール**: ズームイン/アウト
- **右ドラッグ**: パン移動（無効化可能）

### キーボード操作
- **Space**: 自動回転切替
- **WASD**: カメラ移動
- **Shift + マウスドラッグ**: 高速移動

### UIコントロール
- **左上パネル**: マウスホバーで表示
- **パーティクルサイズ**: 0.5-4.0
- **発光強度**: 0-100%
- **重力効果**: 3モード切替
- **オーディオ設定**: マイク/音楽切替

## 📊 パフォーマンス

### パーティクル密度設定
- **Low**: 10,000パーティクル（軽量デバイス向け）
- **Medium**: 25,000パーティクル（標準設定）
- **High**: 50,000パーティクル（高性能デバイス向け）

### 最適化要素
- **視覚的間引き**: カメラ距離に基づく表示制御
- **バッファ最適化**: Float32Array使用
- **GPU加速**: WebGL vertex/fragment shader
- **レンダリング効率**: Three.js r128最適化

## 🔧 開発情報

### ファイル構造
```
threejs-panorama-viewer/
├── action.yml                    # GitHub Actions設定
├── panorama-template.html        # HTMLテンプレート
├── panorama-script.js           # メインスクリプト
├── test-panorama-viewer.html    # テスト用HTML
├── test-panorama-server.sh      # テストサーバー
├── README.md                    # このファイル
└── assets/                      # 実行時作成
    └── panorama-image.jpg       # 処理済み画像
```

### 共通コンポーネント依存関係
```javascript
// 必須: shared-viewer-components/
├── audio-reactive-system.js
├── camera-controls.js
├── mouse-interaction.js
├── particle-effects.js
└── ui-controls.js
```

### カスタマイズポイント
- **球面半径**: `sphereRadius` 変数で調整
- **パーティクル分布**: `createSphericalParticleSystem()` 関数
- **色彩処理**: Canvas pixel analysis部分
- **UI配置**: CSS variables でカスタマイズ

## 🐛 トラブルシューティング

### よくある問題

#### 1. 画像が読み込まれない
```bash
# 解決策: 画像パスとHTTPサーバー確認
ls -la assets/panorama-image.jpg
./test-panorama-server.sh
```

#### 2. パーティクルが表示されない
```javascript
// デバッグ: ブラウザコンソールで確認
console.log('Particles created:', panoramaParticles.geometry.attributes.position.count);
```

#### 3. 共通コンポーネントエラー
```bash
# 解決策: shared-viewer-components/ パス確認
ls -la ../shared-viewer-components/
```

#### 4. パフォーマンス問題
```yaml
# 解決策: パーティクル密度を下げる
particle_density: 'low'  # medium → low
```

## 🔄 アップデート履歴

### v1.0.0 (2025-07-28)
- ✅ 初期リリース
- ✅ 球面パーティクルシステム実装
- ✅ 共通JSコンポーネント統合
- ✅ GitHub Actions対応
- ✅ テスト環境構築

## 📝 ライセンス

MIT License - kamuicode Creative Workshop

## 🤝 関連モジュール

- **threejs-pointcloud-viewer**: 点群データ表示用
- **shared-viewer-components**: 共通JSコンポーネント
- **音楽生成モジュール**: オーディオリアクティブ統合
- **画像生成モジュール**: パノラマ画像作成

---

🌐 **360度の世界をパーティクルで表現する新しい体験をお楽しみください！**