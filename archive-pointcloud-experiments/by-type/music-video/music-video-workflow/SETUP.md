# セットアップガイド

AI Music Video Generator Workflowのセットアップ手順

## 📋 前提条件

- GitHub リポジトリ（Actions有効）
- Claude API アクセス
- kamuicode MCP サーバー設定

## 🔧 ステップ1: リポジトリのクローンと設定

### 1.1 リポジトリのクローン

```bash
# リポジトリをクローン
git clone https://github.com/KentaHomma/kamuicode-workflow.git
```

### 1.2 ワークフローファイルの配置

```bash
# ワークフローディレクトリを作成
mkdir -p .github/workflows

# ワークフローファイルをコピー
cp kamuicode-workflow/music-video-workflow/create-music-video.yml .github/workflows/

# ファイルが正しくコピーされたか確認
ls -la .github/workflows/
```

### 1.3 Claude Code設定

#### MCP設定ファイルの配置

```bash
# Claude設定ディレクトリを作成
mkdir -p .claude

# kamuicode MCP設定ファイルを配置
# .claude/mcp-kamuicode.json の設定が必要
cp kamuicode-workflow/music-video-workflow/.claude/mcp-kamuicode.json .claude/

# 設定ファイルが正しく配置されたか確認
ls -la .claude/
```

#### Claude Code権限設定（重要）

**権限設定の分析方法:**
この設定は、Claude Codeが実際に実行する全ての処理を詳細に分析して作成されています。これが重要です。

**正しい分析手順:**
1. **--allowedToolsパラメータの分析** - 基本的な許可ツールを把握
2. **Claude Codeへの指示内容の分析** - PROMPTで実際に何を実行させているかを確認
3. **追加のBashコマンドの特定** - ダウンロード、動画編集、システムコマンド等の特定
4. **包括的な権限設定** - すべての必要な権限を網羅

`--allowedTools`だけでは不十分で、実際にClaude Codeが実行する処理（ダウンロード、ffmpeg、sleep等）を分析する必要があります。

`.claude/settings.json` ファイルを作成し、ワークフローで使用するツールの権限を設定する必要があります：

```bash
# settings.jsonファイルを作成
cat > .claude/settings.json << 'EOF'
{
  "defaultMode": "acceptEdits",
  "permissions": {
    "allow": [
      "Bash(curl:*)",
      "Bash(wget:*)",
      "Bash(sleep:*)",
      "Bash(stat:*)",
      "Bash(find:*)",
      "Bash(ls:*)",
      "Bash(cat:*)",
      "Bash(head:*)",
      "Bash(mkdir:*)",
      "Bash(git:checkout:*)",
      "Bash(git:config:*)",
      "Bash(git:push:*)",
      "Bash(git:add:*)",
      "Bash(git:diff:*)",
      "Bash(git:commit:*)",
      "Bash(git:pull:*)",
      "Bash(date:*)",
      "Bash(jq:*)",
      "Bash(tr:*)",
      "Bash(wc:*)",
      "Bash(echo:*)",
      "Bash(npx:*)",
      "Bash(open:*)",
      "mcp__t2i-fal-imagen4-ultra__imagen4_ultra_submit",
      "mcp__t2i-fal-imagen4-ultra__imagen4_ultra_status", 
      "mcp__t2i-fal-imagen4-ultra__imagen4_ultra_result",
      "mcp__t2i-fal-imagen4-fast__imagen4_fast_submit",
      "mcp__t2i-fal-imagen4-fast__imagen4_fast_status",
      "mcp__t2i-fal-imagen4-fast__imagen4_fast_result",
      "mcp__r2v-fal-vidu-q1__vidu_q1_submit",
      "mcp__r2v-fal-vidu-q1__vidu_q1_status",
      "mcp__r2v-fal-vidu-q1__vidu_q1_result",
      "mcp__t2v-fal-veo3-fast__veo3_fast_submit",
      "mcp__t2v-fal-veo3-fast__veo3_fast_status",
      "mcp__t2v-fal-veo3-fast__veo3_fast_result",
      "mcp__i2v-fal-hailuo-02-pro__hailuo_02_submit",
      "mcp__i2v-fal-hailuo-02-pro__hailuo_02_status",
      "mcp__i2v-fal-hailuo-02-pro__hailuo_02_result",
      "mcp__t2m-google-lyria__lyria_generate"
    ]
  }
}
EOF

# 設定ファイルが作成されたか確認
cat .claude/settings.json
```

**⚠️ 重要**: この設定がないと、Claude CodeがMCPツールを使用できずワークフローが失敗します。

**ワークフロー分析結果 - 実際に動作確認済みの権限一覧:**

**基本的なBashコマンド:**
- `Bash(curl:*)` - ファイルダウンロード
- `Bash(wget:*)` - 代替ダウンロード方法
- `Bash(sleep:*)` - 待機処理
- `Bash(stat:*)` - ファイル情報確認
- `Bash(find:*)` - ファイル検索
- `Bash(ls:*)` - ディレクトリ一覧
- `Bash(cat:*)` - ファイル内容表示
- `Bash(head:*)` - ファイル先頭表示
- `Bash(mkdir:*)` - ディレクトリ作成
- `Bash(date:*)` - 日時取得
- `Bash(jq:*)` - JSON処理
- `Bash(tr:*)` - 文字列変換
- `Bash(wc:*)` - 文字・行数カウント
- `Bash(echo:*)` - 出力
- `Bash(npx:*)` - Node.js実行
- `Bash(open:*)` - ファイルオープン

**安全なGitコマンド（必要最小限）:**
- `Bash(git:checkout:*)` - ブランチ作成・切り替え
- `Bash(git:config:*)` - ユーザー設定
- `Bash(git:push:*)` - リモートへプッシュ
- `Bash(git:add:*)` - ステージング
- `Bash(git:diff:*)` - 変更確認
- `Bash(git:commit:*)` - コミット
- `Bash(git:pull:*)` - リモートから取得

**MCPツール（生成AI）:**
- `mcp__t2i-fal-imagen4-ultra__*` - 高品質画像生成
- `mcp__t2i-fal-imagen4-fast__*` - 高速画像生成
- `mcp__r2v-fal-vidu-q1__*` - 参照動画生成
- `mcp__t2v-fal-veo3-fast__*` - テキストから動画生成
- `mcp__i2v-fal-hailuo-02-pro__*` - 画像から動画生成
- `mcp__t2m-google-lyria__*` - 音楽生成

**重要**: この設定は実際にワークフローが動作することを確認済みです。

**🔒 セキュリティについて:**
- ファイル削除コマンド（`rm`, `rmdir`, `mv`等）は一切許可していません
- 危険なgitコマンド（`git reset`, `git clean`, `git rm`等）は除外し、必要なもののみ許可
- 主に読み取り専用コマンドと必要最小限の書き込み権限のみを許可
- 実行環境はGitHub Actionsの分離された環境のため、ローカルシステムへの影響はありません

## 🔐 ステップ2: Secrets設定

### 2.1 必要なSecrets

以下のキーの設定が必要です：

| Secret名 | 説明 | 取得方法 |
|---------|------|----------|
| `ANTHROPIC_API_KEY` | Claude API Key (必須) | [Anthropic Console](https://console.anthropic.com/)でAPI Keyを作成 |
| `PAT_TOKEN` | GitHub Personal Access Token (オプション) | Settings → Developer settings → Personal access tokens → Tokens (classic) |

### 2.2 ANTHROPIC_API_KEYの取得方法

1. [Anthropic Console](https://console.anthropic.com/)にアクセス
2. ログインまたはアカウント作成
3. 左側メニューの「API Keys」をクリック
4. 「Create Key」をクリック
5. キー名を入力（例：`github-actions-music-video`）
6. 作成されたAPIキーをコピー（⚠️この画面でしか表示されません）

### 2.3 PAT_TOKENの取得方法（オプション）

1. GitHubにログイン
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 「Generate new token (classic)」をクリック
4. 以下の権限を選択：
   - `repo` (リポジトリへの完全アクセス)
   - `workflow` (GitHub Actionsワークフローの更新)
5. 「Generate token」をクリック
6. 作成されたトークンをコピー（⚠️この画面でしか表示されません）

### 2.4 Secrets設定手順

**2つの方法があります：**

#### 方法1: GitHub CLI（推奨・簡単）

**前提条件:**
- GitHub CLI (`gh`) がインストール済み
- `gh auth login` で認証済み

```bash
# カレントディレクトリがリポジトリ内の場合
gh secret set ANTHROPIC_API_KEY --app actions
# ↑ 実行後、APIキーを安全に入力（画面に表示されません）

# PAT_TOKEN（必要に応じて）
gh secret set PAT_TOKEN --app actions

# 設定確認
gh secret list --app actions
```

**特定のリポジトリに設定する場合:**
```bash
gh secret set ANTHROPIC_API_KEY --app actions --repo owner/repo-name
```

#### 方法2: GitHub Web UI（従来通り）

1. **GitHubリポジトリページ**にアクセス
2. **Settings**タブをクリック
3. 左サイドバーの**Secrets and variables** → **Actions**をクリック
4. **New repository secret**をクリック
5. 以下を順番に追加：

**ANTHROPIC_API_KEYの追加：**
- **Name**: `ANTHROPIC_API_KEY`
- **Secret**: 先ほどコピーしたClaude APIキー
- **Add secret**をクリック

**PAT_TOKENの追加（必要に応じて）：**
- **Name**: `PAT_TOKEN`  
- **Secret**: 先ほどコピーしたPersonal Access Token
- **Add secret**をクリック

### 2.5 設定確認

設定完了後、Secretsページに以下が表示されることを確認：
- ✅ `ANTHROPIC_API_KEY` (Updated X minutes ago)
- ✅ `PAT_TOKEN` (Updated X minutes ago) ※設定した場合

## 📁 ステップ3: ディレクトリ構造

```
your-repo/
├── .github/
│   └── workflows/
│       └── create-music-video.yml
├── .claude/
│   └── mcp-kamuicode.json
├── README.md
└── (他のファイル)
```

## 🎛️ ステップ4: GitHub権限設定（必要に応じて）

**ほとんどの場合、新しいリポジトリでは標準でONになっているため設定不要です。**

ワークフローが権限エラーで失敗する場合のみ、以下を確認してください：

**Settings** → **Actions** → **General** → **Workflow permissions**
- ✅ "Read and write permissions" を選択
- ✅ "Allow GitHub Actions to create and approve pull requests" をチェック

**よくあるエラー:**
- `Permission denied to create branch` → 上記設定を確認
- `Resource not accessible by integration` → PR作成権限を確認

## 🧪 ステップ5: テスト実行

### 5.1 手動テスト

1. **Actions**タブに移動
2. **Create AI Music Video**ワークフローを選択
3. **Run workflow**をクリック
4. 音楽コンセプトを入力（例: "サイバーパンク都市のテクノ音楽"）
5. **Run workflow**を実行

### 5.2 動作確認

実行後、以下を確認：

- [ ] 音楽ファイルが生成されている
- [ ] 3つの画像が生成されている
- [ ] 3つの動画が生成されている
- [ ] 最終ミュージックビデオが生成されている
- [ ] Pull Requestが自動作成されている

---

**サポート:**
- Issue報告: GitHub Issues
- ドキュメント: README.md
- 使用例: EXAMPLES.md