# Bria.ai MCP Server

Bria.aiのAPIを利用してキーワード指定による画像生成を行うMCP（Model Context Protocol）サーバーです。

## 特徴

- **Text-to-Image生成**: キーワードを指定してAI画像を生成
- **複数画像生成**: 一度に最大4つの画像を同時生成
- **同期・非同期対応**: 用途に応じて生成方式を選択可能
- **再現性**: シード値を指定して同じ結果を再現
- **コンテンツモデレーション**: 不適切なコンテンツのフィルタリング
- **高速セットアップ**: uvによる高速な依存関係管理

## 前提条件

- Python 3.8以上
- [uv](https://docs.astral.sh/uv/)
- Bria.ai APIキー（[Bria.ai](https://bria.ai/)でアカウント作成が必要）

## インストール

### 🚀 uvを使用したセットアップ

1. **自動セットアップ**:
```bash
./setup_uv.sh
```

2. **手動セットアップ**:
```bash
# uvをインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係をインストール
uv sync

# 環境変数を設定
export BRIA_API_TOKEN="your_bria_api_token_here"
export BRIA_MODEL_VERSION="2.3"  # オプション

# サーバー起動
uv run python bria_mcp_server.py
```

## 使用方法

### MCPサーバーとして実行

```bash
uv run python bria_mcp_server.py
```

### 利用可能なツール

#### 1. generate_image
キーワードを指定して画像を生成します。

**パラメータ**:
- `prompt` (必須): 画像生成用のテキストプロンプト
- `num_results` (オプション): 生成する画像数（1-4、デフォルト：1）
- `sync` (オプション): 同期生成の有無（デフォルト：true）
- `seed` (オプション): 再現性のためのシード値
- `content_moderation` (オプション): コンテンツモデレーションの有効化

**使用例**:
```json
{
  "prompt": "beautiful sunset over mountains",
  "num_results": 2,
  "sync": true,
  "seed": 12345
}
```

#### 2. get_generation_status
非同期生成の進行状況を確認します。

**パラメータ**:
- `urls` (必須): 非同期生成で返されたURL配列

**使用例**:
```json
{
  "urls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ]
}
```

## 開発・メンテナンス

### 開発コマンド

```bash
# 依存関係の同期
uv sync

# パッケージの追加
uv add <package_name>

# 開発用依存関係の追加
uv add --dev <package_name>

# 仮想環境でコマンド実行
uv run <command>

# コードフォーマット
uv run black .

# リンター実行
uv run ruff check

# リンター自動修正
uv run ruff check --fix

# 型チェック
uv run mypy .

# テスト実行
uv run pytest

# Pythonバージョンの管理
uv python install 3.11
uv python pin 3.11
```

## APIについて

### Bria.ai API仕様

- **エンドポイント**: `https://engine.prod.bria-api.com/v1/text-to-image/base/{model_version}`
- **認証**: APIトークンをヘッダーに含める
- **対応フォーマット**: JSON
- **レスポンス**: 生成された画像のURL

### 画像URLのホスティングと有効期限

#### ホスト先
Bria.ai APIから返される画像URLは**AWS S3（Amazon Simple Storage Service）**にホストされています。

**URLの形式例**:
```
https://bria-temp.s3.amazonaws.com/[path]/[filename]?AWSAccessKeyId=[key]&Signature=[signature]&Expires=[timestamp]
```

#### URL の特徴
- **署名付きURL（Presigned URL）**: AWS S3の署名付きURL機能を使用
- **一時的アクセス**: URLそのものにアクセス権限が含まれており、URLを知っている人なら誰でもアクセス可能
- **セキュア**: 署名により改ざんを防止
- **自動期限切れ**: 指定された有効期限後は自動的にアクセス不可

#### 有効期限について
- **最大有効期限**: AWS S3署名付きURLの仕様により最大7日間
- **実際の有効期限**: Bria.aiが設定する具体的な期限（通常はより短期間）
- **期限切れ後**: `The provided token has expired` エラーが表示される
- **再利用不可**: 期限切れ後は同じURLでの再アクセスは不可能

#### 推奨される使用方法
1. **即座にダウンロード**: URLを受け取ったらすぐに画像をダウンロードして保存
2. **長期保存**: 長期間使用する場合は自身のストレージに保存
3. **URL共有**: 短期間のみの共有に留める
4. **キャッシュ戦略**: アプリケーション側でのキャッシュ機能を実装

### 対応モデル

- **Bria 2.3**: 最新の高品質モデル（デフォルト）
- その他のモデルは環境変数で指定可能

## 設定

### 環境変数

| 変数名 | 説明 | 必須 | デフォルト |
|--------|------|------|------------|
| `BRIA_API_TOKEN` | Bria.ai APIキー | ✓ | - |
| `BRIA_MODEL_VERSION` | 使用するモデルバージョン | - | "2.3" |

### 設定ファイル（オプション）

`config.json`ファイルを作成して設定を管理できます:

```json
{
  "api_token": "your_api_token_here",
  "model_version": "2.3",
  "default_num_results": 1,
  "default_sync": true,
  "timeout": 60
}
```

### pyproject.toml設定

プロジェクト設定は `pyproject.toml` で管理されており、以下の機能が含まれています：

- 依存関係管理
- 開発ツール設定（black、ruff、mypy等）
- プロジェクトメタデータ
- ビルド設定

## トラブルシューティング

### 一般的な問題

1. **APIキーエラー**:
   - `BRIA_API_TOKEN`環境変数が設定されているか確認
   - APIキーが有効か確認

2. **タイムアウトエラー**:
   - ネットワーク接続を確認
   - プロンプトの複雑さを調整

3. **画像生成エラー**:
   - プロンプトの内容を確認
   - コンテンツモデレーションの設定を確認

4. **uv関連の問題**:
   - uvのバージョンを確認: `uv --version`
   - 仮想環境の再作成: `uv sync --reload`

5. **画像URL関連の問題**:
   - **「The provided token has expired」エラー**: URLの有効期限が切れています。新しい画像生成を行ってください
   - **URLアクセス不可**: ネットワーク接続を確認し、URLが正しくコピーされているか確認
   - **画像が表示されない**: URLの有効期限を確認し、必要に応じて画像を再生成

### ログ

サーバーは標準エラー出力にログを出力します：

```bash
uv run python bria_mcp_server.py 2> server.log
```

## 制限事項

- 同時生成可能な画像数は最大4つ
- **生成された画像URLは一時的（最大7日間の有効期限あり）**
- **長期保存が必要な場合は画像をダウンロードして自身のストレージに保存**
- APIレート制限の対象
- コンテンツモデレーションにより一部のプロンプトが拒否される可能性

## uvの利点

uvは従来のpipに比べて以下の利点があります：

- **高速**: 従来のpipより大幅に高速な依存関係解決
- **確実性**: ロックファイルによる完全に再現可能な環境
- **シンプル**: 単一ツールでパッケージ管理からPython環境管理まで
- **最新**: 最新のPythonパッケージング標準に準拠
- **効率的**: ディスク使用量とメモリ使用量を最適化

## サポート

- [Bria.ai公式ドキュメント](https://docs.bria.ai/)
- [Bria.ai APIリファレンス](https://bria-ai-api-docs.redoc.ly/)
- [MCPプロトコル仕様](https://modelcontextprotocol.io/)
- [uv公式ドキュメント](https://docs.astral.sh/uv/)

## ライセンス

このソフトウェアはMITライセンスの下で提供されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。

コントリビューション前に以下を実行してください：
```bash
# コードフォーマット
uv run black .

# リンターチェック
uv run ruff check --fix

# 型チェック
uv run mypy .

# テスト実行
uv run pytest
```

## 変更履歴

### v1.0.0
- 初回リリース
- Text-to-Image生成機能
- 同期・非同期生成対応
- コンテンツモデレーション機能
- uvサポート追加
- pyproject.toml設定追加