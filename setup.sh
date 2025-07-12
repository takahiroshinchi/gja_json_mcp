#!/bin/bash

# Bria.ai MCP Server セットアップスクリプト

set -e

echo "🚀 Bria.ai MCP Server セットアップを開始します..."

# Python バージョンチェック
echo "📋 Python バージョンを確認中..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8以上が必要です。現在のバージョン: $python_version"
    exit 1
fi

echo "✅ Python バージョン確認完了: $python_version"

# 仮想環境の作成（オプション）
read -p "🤔 仮想環境を作成しますか？ (y/N): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 仮想環境を作成中..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 仮想環境が作成され、アクティベートされました"
fi

# 依存関係のインストール
echo "📦 依存関係をインストール中..."
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ 依存関係のインストールが完了しました"
else
    echo "❌ requirements.txt が見つかりません"
    exit 1
fi

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
echo "📚 次のステップ:"
echo "1. Bria.ai APIキーを取得: https://bria.ai/"
echo "2. 環境変数を設定: export BRIA_API_TOKEN=\"your_api_token\""
echo "3. サーバーを起動: python bria_mcp_server.py"
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
        python bria_mcp_server.py
    fi
fi

echo "🚀 セットアップスクリプトが完了しました！"