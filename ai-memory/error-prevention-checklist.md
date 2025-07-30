# エラー予防・対処ガイド

**Summary**: AI開発時のエラー予防チェックリストと発生時の対処法  
**Tags**: #error-prevention #github-actions #debugging #data-flow #yaml-syntax  
**Related**: [debugging-lessons-from-agents.md], [github-actions-troubleshooting.md]  
**AI Usage**: 新機能実装前の事前チェックとエラー発生時の対処手順として活用  
**Date**: 2025-01-27  
**Status**: active

## GitHub Actions YAML構文

### 必須チェック項目
- `if:` 条件は必ず `${{ }}` で囲む
- output名・env変数名にハイフン使用禁止（アンダースコア使用）
- `run: |` ブロック内のインデントは統一
- HEREDOCの `EOF` とその後の `)` も適切なインデント
- マルチライン文字列は避ける

### 検証コマンド
```bash
ruby -ryaml -e "YAML.load_file('ファイル名')"
```

### よくある間違い
- `if: contains(...)` → `if: ${{ contains(...) }}`
- `folder-name` → `folder_name`
- HEREDOCのインデント不整合

## Git同期問題

### 実行前必須確認
```bash
git status          # 未コミット確認
git log --oneline -3 # 最新コミット確認
git push origin main # 同期確認
```

### GitHub Actions実行時の不整合
- 症状: 古いコミットで実行される
- 原因: ローカルとリモートの同期問題
- 対処: プッシュ→ワークフロー再実行

## データフロー問題

### GitHub Actions変数
- `$GITHUB_ENV` は信頼できない場合がある
- 直接パス指定の方が確実
- 例: `${{ steps.setup.outputs.folder-name }}/world-analysis/image-analysis.json`

### データ受け渡し確認
- 各stepでのデータ存在確認
- ファイルパスの検証
- 空データのエラーハンドリング

## 段階的統合

### A→B→C統合パターン
- Phase A: 単体テスト
- Phase B: 部分統合
- Phase C: 完全統合
- 各段階で完全検証してから次へ

### 統合失敗時
- 前の段階に戻って確認
- データフローを端から端まで追跡
- 仮説に固執せず証拠に基づく修正

## 修正作業効率化

### 段階的修正
1. 1つずつ問題を修正
2. 修正後は必ず検証
3. 同種ファイルは一括チェック
4. 修正完了まで他タスク着手禁止

### 時間ロス回避
- エラーメッセージを詳細読取
- 複数箇所の同時エラーを想定
- テンプレート修正パターン適用
- チェックリスト厳格遵守

## エラー発生時の対処順序

1. **エラーメッセージ詳細確認**
2. **影響範囲特定**
3. **根本原因分析**（表面的症状に惑わされない）
4. **同種エラー全体検索**
5. **段階的修正実施**
6. **修正効果確認**
7. **予防策実装**

## 絶対に避けるべき行動

- エラーメッセージを読まずに推測修正
- 複数問題を同時に修正
- 検証せずに次の修正に進む
- 仮説に固執して証拠を無視
- 同種ファイルの個別修正
- 修正途中での他タスク着手

## AI自動化のための学習ポイント

### 成功パターン
- 事前検証による予防
- 段階的修正アプローチ
- データフロー中心の問題解決
- シンプルソリューション優先

### 失敗パターン
- 表面的エラーメッセージへの固執
- 複雑な変数受け渡し機構への依存
- 検証手順の省略
- 根本原因分析の不足

このガイドを参照してエラーを予防し、発生時は系統的に対処すること。

## YAMLヒアドキュメント構文エラー (2025-01-28追記)

### エラー症状
```
yaml.scanner.ScannerError: while scanning a simple key
could not find expected ':'
```

### 原因
- `run: |`ブロック内のヒアドキュメントで、HTMLコンテンツがインデントされていない
- YAMLパーサーが`<!DOCTYPE html>`等を新しいキーとして解釈

### 誤った例
```yaml
run: |
  cat > file.html <<EOF
<!DOCTYPE html>  # ← インデントなし（エラー）
<html>
EOF
```

### 正しい例
```yaml
run: |
  cat > file.html <<EOF
  <!DOCTYPE html>  # ← 統一インデント（正しい）
  <html>
  EOF
```

### 重要ポイント
1. **すべての行が同じインデント**: `run: |`ブロック内のすべての行（ヒアドキュメント内容含む）
2. **終了デリミタも同じレベル**: EOFやENDHTML等の終了タグも同じインデント
3. **変数展開の考慮**: シングルクォート`<<'EOF'`は変数展開を無効化するので注意

### 対処手順
1. エラー行番号を確認し、該当箇所のインデントをチェック
2. ヒアドキュメント全体のインデントを統一
3. `python3 -c "import yaml; yaml.safe_load(open('file.yml'))"`で検証
4. 修正は一度に一つずつ、検証してから次へ

### 教訓
- アドバイスを受けた際は、その意図を正確に理解する
- 問題の本質（この場合はYAMLインデント）から逸れない
- 複数の修正方法を試す前に、現在の問題を完全に理解する

## Python YAMLパーサー使用時の注意点

### エラーメッセージの読み方
- **「while scanning a simple key」**: 新しいキー値ペアを期待している
- **2行にわたるエラー表示**: 1行目が問題開始、2行目が問題確定位置
- **「could not find expected ':'」**: YAMLキーとして解釈され、コロンを探している

### 検証コマンド
```bash
# 基本検証
python3 -c "import yaml; yaml.safe_load(open('file.yml'))"

# 詳細なエラー情報
python3 -c "
import yaml
try:
    with open('file.yml') as f:
        yaml.safe_load(f)
    print('✅ YAML is valid')
except yaml.YAMLError as e:
    print(f'❌ Error: {e}')
    if hasattr(e, 'problem_mark'):
        mark = e.problem_mark
        print(f'📍 Line: {mark.line + 1}, Column: {mark.column + 1}')
"
```

### よくあるエラーパターン
1. **`could not find expected ':'`** → インデント不整合
2. **`found undefined alias`** → YAMLアンカー(&, *)の問題  
3. **`expected <block end>, but found`** → ブロック終了の問題
4. **`found character that cannot start any token`** → タブ文字混入

### デバッグのコツ
1. **部分的な検証**: エラー箇所周辺だけを抽出して検証
2. **インデント可視化**: `cat -A`でタブ・スペースを確認
3. **段階的修正**: 1つのエラーを修正→検証→次のエラーへ

## 複合システム統合エラー (2025-01-30追記)

### YAML + Python + GitHub Actions 複合エラーパターン

#### エラー分類フレームワーク
```yaml
Layer 1 (構文レベル): YAML, Python, JSON等の書式問題
Layer 2 (実行環境): パス解決, 権限, 依存関係問題  
Layer 3 (ロジック): パラメータ, フロー, 状態管理問題
Layer 4 (統合): システム間連携, 出力形式, プロトコル問題
```

#### 30秒緊急チェックリスト
```markdown
□ エラーメッセージ全文をコピペしたか？
□ エラーの「種類」を特定したか？（構文/実行時/設定/パス）
□ 最後に変更したファイルを特定したか？
□ 類似する動作例を1つ以上確認したか？
□ 推測で修正する前に根拠を明文化したか？
```

### YAML内Python統合時の必須確認

#### 1. ヒアドキュメント問題の予防
```yaml
# 危険パターン
run: |
  python3 << 'EOF'
import cv2  # ← この行がYAMLキーとして解釈される
EOF

# 安全パターン  
run: |
  python3 -c "
  import cv2
  # Pythonコードをここに書く
  "
  
# 最安全パターン
run: |
  python3 scripts/external_script.py
```

#### 2. スコープ問題の回避
- **原則**: 複雑なPythonスクリプトは最初から外部ファイル化
- **検証**: `import`文がモジュール最上位にあることを確認
- **エラー**: `UnboundLocalError: local variable 'module' referenced before assignment`

### Composite Action出力変数問題

#### GitHub Actions出力の正しい設定
```yaml
# action.yml内の正しい設定
outputs:
  output_name:
    description: 'Description of output'
    value: ${{ steps.step-id.outputs.output_name }}

# JavaScript/Pythonでの出力設定
run: |
  echo "output_name=value" >> $GITHUB_OUTPUT
```

#### よくある間違い
- `::set-output`コマンド（廃止済み）を使用
- `$GITHUB_OUTPUT`への書き込みのみ（value mappingなし）
- JavaScript ActionとComposite Actionの混同

### ファイルパス・作業ディレクトリ問題

#### 絶対パス徹底の重要性
```python
# 危険パターン
relative_path = "images/input.png"

# 安全パターン
workspace = os.environ.get("GITHUB_WORKSPACE", os.getcwd())
absolute_path = os.path.join(workspace, "images/input.png")
```

#### 検証コマンド
```bash
# 現在の作業ディレクトリ確認
pwd
echo $GITHUB_WORKSPACE

# ファイル存在確認
ls -la $GITHUB_WORKSPACE/expected/path/
find $GITHUB_WORKSPACE -name "target-file.*" -type f
```

### 必須パラメータ管理

#### action.yml定義の厳密チェック
```yaml
inputs:
  required_param:
    description: 'This is required'
    required: true
  optional_param:
    description: 'This is optional'
    required: false
    default: 'default_value'
```

#### 実行時の全パラメータ確認
```yaml
with:
  required_param: ${{ steps.previous.outputs.value }}
  optional_param: ${{ steps.setup.outputs.folder_name }}/path/to/file
```

### 予防策の投資対効果ランキング

#### ⭐⭐⭐ 最高優先度（工数30分→エラー削減90%）
1. **外部ファイル化**: YAMLに複雑ロジックを書かない
2. **絶対パス徹底**: `GITHUB_WORKSPACE`基準のパス使用
3. **既存パターン確認**: 動作例との差分明確化

#### ⭐⭐ 高優先度（工数1時間→エラー削減70%）  
4. **出力変数の明示的設定**: Composite Actionのvalue mapping
5. **エラーメッセージの精読**: 推測修正を避ける
6. **段階的修正・検証**: 1問題1修正1検証

#### ⭐ 標準優先度（工数2時間→エラー削減50%）
7. **複合エラーの分類**: Layer別問題分析
8. **類似コード調査**: 成功パターンの適用
9. **根本原因分析**: 表面的症状から脱却

### 複合システムエラー発生時の対処順序

1. **エラー分類**: Layer 1-4のどこに該当するか特定
2. **システム切り分け**: YAML/Python/GitHub Actions/ファイルシステム
3. **データフロー追跡**: 入力→処理→出力の各段階確認
4. **既存パターン比較**: 類似する動作例との差分分析
5. **段階的修正**: 1つのLayer問題を完全解決してから次へ
6. **統合テスト**: 修正後の全体動作確認

### 絶対に避けるべき複合エラー対応

- **推測による複数修正**: 複数のLayerを同時に修正
- **表面的症状への固執**: エラーメッセージのみでの判断  
- **複雑化による解決**: シンプルソリューションを回避
- **仮説への執着**: 証拠と矛盾する仮説の継続
- **統合テストの省略**: 部分修正後の全体確認不足