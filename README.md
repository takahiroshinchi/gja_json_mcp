# Bria.ai MCP Server

Bria.aiのAPIを利用してキーワード指定による画像生成を行うMCP（Model Context Protocol）サーバーです。

## 特徴

- **Text-to-Image生成**: キーワードを指定してAI画像を生成
- **複数画像生成**: 一度に最大4つの画像を同時生成
- **同期・非同期対応**: 用途に応じて生成方式を選択可能
- **再現性**: シード値を指定して同じ結果を再現
- **コンテンツモデレーション**: 不適切なコンテンツのフィルタリング

## 前提条件

- Python 3.8以上
- Bria.ai APIキー（[Bria.ai](https://bria.ai/)でアカウント作成が必要）

## インストール

1. **依存関係をインストール**:
```bash
pip install -r requirements.txt
```

2. **環境変数を設定**:
```bash
export BRIA_API_TOKEN="your_bria_api_token_here"
export BRIA_MODEL_VERSION="2.3"  # オプション（デフォルト：2.3）
```

3. **実行権限を付与**:
```bash
chmod +x bria_mcp_server.py
```

## 使用方法

### MCPサーバーとして実行

```bash
python bria_mcp_server.py
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

## APIについて

### Bria.ai API仕様

- **エンドポイント**: `https://engine.prod.bria-api.com/v1/text-to-image/base/{model_version}`
- **認証**: APIトークンをヘッダーに含める
- **対応フォーマット**: JSON
- **レスポンス**: 生成された画像のURL

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

### ログ

サーバーは標準エラー出力にログを出力します：
```bash
python bria_mcp_server.py 2> server.log
```

## 制限事項

- 同時生成可能な画像数は最大4つ
- 生成された画像URLは一時的（有効期限あり）
- APIレート制限の対象
- コンテンツモデレーションにより一部のプロンプトが拒否される可能性

## サポート

- [Bria.ai公式ドキュメント](https://docs.bria.ai/)
- [Bria.ai APIリファレンス](https://bria-ai-api-docs.redoc.ly/)
- [MCPプロトコル仕様](https://modelcontextprotocol.io/)

## ライセンス

このソフトウェアはMITライセンスの下で提供されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。

## 変更履歴

### v1.0.0
- 初回リリース
- Text-to-Image生成機能
- 同期・非同期生成対応
- コンテンツモデレーション機能