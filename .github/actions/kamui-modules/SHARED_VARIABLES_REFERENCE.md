# 🔧 共通変数参照ガイド

## ⚠️ 重要：変数重複宣言エラー防止

テストファイルや新しいスクリプトで以下の変数を使用する際は、`let`/`var`/`const`で再宣言せず、直接値を代入してください。

## 📋 共通JS変数一覧

### 🎥 Camera Controls (`camera-controls.js`)
```javascript
// ❌ NG: let scene = new THREE.Scene();
// ✅ OK: scene = new THREE.Scene();

scene                 // THREE.Scene
camera                // THREE.PerspectiveCamera  
renderer              // THREE.WebGLRenderer
controls              // THREE.OrbitControls
autoRotate = false    // boolean
rotationSpeed = 1.0   // number
```

### 🖱️ Mouse Interaction (`mouse-interaction.js`)
```javascript
mousePosition         // THREE.Vector2
mouseWorldPosition    // THREE.Vector3
originalPositions     // Float32Array
mouseGravityEnabled = false  // boolean
gravityStrength = 0.3        // number
gravityRange = 100           // number
waveIntensity = 0.0          // number
particleVelocities           // Float32Array
gravityMode = 'circle'       // string: 'circle'|'flow'|'magnet'
mouseTrail = []              // Array
```

### 🎵 Audio Reactive (`audio-reactive-system.js`)
```javascript
audioElement = null          // HTMLAudioElement
musicPlaying = false         // boolean
audioContext = null          // AudioContext
microphoneSource = null      // MediaStreamAudioSourceNode
musicAnalyser = null         // AnalyserNode
micAnalyser = null           // AnalyserNode
musicDataArray = null        // Uint8Array
micDataArray = null          // Uint8Array
audioReactiveEnabled = false // boolean
microphoneEnabled = false    // boolean
currentVolumeLevel = 0       // number
volumeSmoothing = 0.3        // number
frequencyBands = {}          // object
audioMode = 'music'          // string: 'music'|'voice'
dynamicModeEnabled = false   // boolean
adaptiveSystem = {}          // object
effectDecay = {}             // object
currentEffects = {}          // object
```

### 🎮 UI Controls (`ui-controls.js`)
```javascript
pointSize = 1.5              // number
brightnessLevel = 0.2        // number
glowIntensity = 0.0          // number
```

## 🔧 正しい使用方法

### ✅ 正しい書き方:
```javascript
// テストファイルまたは新しいスクリプトで
pointSize = 2.0;        // OK: 値の代入
autoRotate = true;      // OK: 値の代入  
gravityStrength = 0.5;  // OK: 値の代入
```

### ❌ エラーを起こす書き方:
```javascript
let pointSize = 2.0;        // NG: SyntaxError - 重複宣言
var autoRotate = true;      // NG: SyntaxError - 重複宣言
const gravityStrength = 0.5; // NG: SyntaxError - 重複宣言
```

## 🚀 テンプレートコード

### テストファイル用テンプレート:
```javascript
// テスト設定 - 共通変数の値設定（再宣言なし）
// These variables are declared in shared components
pointSize = 1.5;        // from ui-controls.js
autoRotate = false;     // from camera-controls.js  
rotationSpeed = 1.0;    // from camera-controls.js
gravityStrength = 0.3;  // from mouse-interaction.js
audioReactiveEnabled = false; // from audio-reactive-system.js

// テスト専用変数（新規宣言OK）
let testSpecificVar = 'test-value';
let myTestData = [];
```

## 🔍 変数の所属確認方法

```bash
# 特定の変数がどのファイルで宣言されているか確認
grep -r "let variableName\|var variableName\|const variableName" shared-components/

# 例: pointSizeの宣言場所を確認
grep -r "let pointSize\|var pointSize\|const pointSize" shared-components/
# → ui-controls.js:let pointSize = 1.5;
```

## 📝 新規スクリプト作成時のチェックリスト

1. ✅ 使用する変数が共通変数リストにないか確認
2. ✅ 共通変数は値の代入のみ（`let`宣言なし）
3. ✅ 新規変数のみ`let`/`const`で宣言
4. ✅ ブラウザコンソールでSyntaxErrorがないか確認

## 🎯 よくあるエラーと解決法

### エラー例:
```
Uncaught SyntaxError: Identifier 'pointSize' has already been declared
Uncaught SyntaxError: Identifier 'autoRotate' has already been declared  
Uncaught SyntaxError: Identifier 'scene' has already been declared
```

### 解決法:
```javascript
// ❌ エラー原因
let pointSize = 2.0;

// ✅ 修正後  
pointSize = 2.0;  // 共通変数への値代入
```

この参照ガイドに従えば、変数重複宣言エラーを回避できます！