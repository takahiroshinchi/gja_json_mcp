#!/bin/bash

# Bria.ai MCP Server セットアップスクリプト (uv版)

set -e

echo "🚀 Bria.ai MCP Server セットアップを開始します (uv使用)..."

# uv のインストール確認
if ! command -v uv &> /dev/null; then
    echo "❌ uv が見つかりません。uvをインストールしますか？"
    read -p "🤔 uvをインストールしますか？ (y/N): " install_uv
    if [[ $install_uv =~ ^[Yy]$ ]]; then
        echo "📦 uvをインストール中..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
        echo "✅ uvがインストールされました"
    else
        echo "❌ uvが必要です。https://docs.astral.sh/uv/ を参照してください"
        exit 1
    fi
fi

echo "✅ uv が利用可能です: $(uv --version)"

# Python バージョンチェック
echo "📋 Python バージョンを確認中..."
if ! uv python pin 3.10 --python-preference only-managed 2>/dev/null; then
    echo "📦 Python 3.10+ をインストール中..."
    uv python install 3.11  # 最新の安定版をインストール
    uv python pin 3.11
fi

echo "✅ Python バージョン確認完了"

# 仮想環境の作成と依存関係のインストール
echo "📦 仮想環境を作成し、依存関係をインストール中..."
uv sync

echo "✅ 依存関係のインストールが完了しました"

# 実行権限の付与
echo "🔧 実行権限を設定中..."
chmod +x bria_mcp_server.py
echo "✅ 実行権限が設定されました"

# 設定ファイルの作成
if [ ! -f "config.json" ]; then
    if [ -f "config.example.json" ]; then
        echo "⚙️  設定ファイルを作成中..."
        cp config.example.json config.json
        echo "✅ config.json が作成されました（config.example.json をコピー）"
        echo "📝 config.json を編集してAPIキーを設定してください"
    fi
fi

# 環境変数の設定確認
echo ""
echo "🔑 環境変数の設定が必要です:"
echo ""
echo "export BRIA_API_TOKEN=\"your_bria_api_token_here\""
echo "export BRIA_MODEL_VERSION=\"2.3\"  # オプション"
echo ""

# APIキーの入力（オプション）
read -p "🔑 Bria.ai APIキーを今すぐ設定しますか？ (y/N): " set_api_key
if [[ $set_api_key =~ ^[Yy]$ ]]; then
    read -p "Bria.ai APIキーを入力してください: " api_key
    if [ ! -z "$api_key" ]; then
        echo "export BRIA_API_TOKEN=\"$api_key\"" >> ~/.bashrc
        echo "export BRIA_MODEL_VERSION=\"2.3\"" >> ~/.bashrc
        echo "✅ APIキーが ~/.bashrc に追加されました"
        echo "🔄 新しいターミナルを開くか、'source ~/.bashrc' を実行してください"
    fi
fi

# セットアップ完了
echo ""
echo "🎉 セットアップが完了しました！"
echo ""
echo "📚 uvを使用した開発コマンド:"
echo "  uv run python bria_mcp_server.py    # サーバー起動"
echo "  uv run pytest                       # テスト実行"
echo "  uv run black .                      # コードフォーマット"
echo "  uv run ruff check                   # リンター実行"
echo "  uv add <package>                    # パッケージ追加"
echo ""
echo "📚 次のステップ:"
echo "1. Bria.ai APIキーを取得: https://bria.ai/"
echo "2. 環境変数を設定: export BRIA_API_TOKEN=\"your_api_token\""
echo "3. サーバーを起動: uv run python bria_mcp_server.py"
echo ""
echo "📖 詳細な使用方法は README.md を参照してください"
echo ""

# テスト実行の提案
if [ ! -z "$BRIA_API_TOKEN" ] || [[ $set_api_key =~ ^[Yy]$ ]]; then
    read -p "🧪 テスト実行を行いますか？ (y/N): " run_test
    if [[ $run_test =~ ^[Yy]$ ]]; then
        echo "🧪 テスト実行中..."
        echo "サーバーを起動します（Ctrl+C で停止）"
        sleep 2
        uv run python bria_mcp_server.py
    fi
fi

echo "🚀 セットアップスクリプトが完了しました！"
