# 🌐 Three.js 360° Panorama Viewer

360度パノラマ画像を球面パーティクルシステムで表示するThree.jsビューアーモジュールです。共通JSコンポーネントシステムを活用し、音楽反応、マウスインタラクション、オーディオリアクティブ効果を統合します。

## 🎯 概要

このモジュールは**平面分割→球面パーティクル配置**アプローチを使用し、入力画像を分析して球面上にパーティクルを配置することで360度パノラマ体験を提供します。

### ✨ 主要機能

- **🌐 360度パノラマ表示**: 球面座標系でのパーティクル配置
- **🎨 画像ピクセル分析**: Canvas APIによる色情報抽出
- **🎵 オーディオリアクティブ**: 音楽・マイクロフォン対応
- **🖱️ マウスインタラクション**: 重力効果、波動エフェクト
- **🎮 現代的UI**: 自動隠しコントロールパネル
- **📱 レスポンシブ**: 全デバイス対応

## 🏗️ 技術仕様

### アーキテクチャ
```
入力画像 → ピクセル分析 → 球面座標変換 → パーティクル生成 → 360度表示
```

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
- name: Create 360° Panorama Viewer
  uses: ./.github/actions/kamui-modules/threejs-panorama-viewer
  with:
    input_image: 'path/to/panorama.jpg'
    output_filename: 'my-panorama.html'
    background_color: '#000814'
    particle_density: 'high'
    auto_rotate: 'true'
    rotation_speed: '1.5'
    enable_music: 'true'
    music_file: 'path/to/music.mp3'
```

### 入力パラメータ

| パラメータ | 説明 | デフォルト | 必須 |
|-----------|------|-----------|------|
| `input_image` | パノラマ画像ファイル | - | ✅ |
| `output_filename` | 出力HTMLファイル名 | `panorama-viewer.html` | ❌ |
| `background_color` | 背景色（hex形式） | `#000814` | ❌ |
| `camera_position_radius` | カメラ初期位置半径 | `100` | ❌ |
| `particle_density` | パーティクル密度 (low/medium/high) | `medium` | ❌ |
| `auto_rotate` | 自動回転有効化 | `true` | ❌ |
| `rotation_speed` | 自動回転速度 | `1.0` | ❌ |
| `enable_music` | 音楽統合有効化 | `false` | ❌ |
| `music_file` | 音楽ファイル | - | ❌ |

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