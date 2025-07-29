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