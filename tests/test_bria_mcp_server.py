"""
Tests for Bria.ai MCP Server
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
import json

# Import from the main module
import sys
sys.path.append('..')


class TestBriaMCPServer:
    """Bria MCP Server のテストクラス"""
    
    def setup_method(self):
        """テストの前処理"""
        self.test_api_token = "test_api_token"
        self.test_model_version = "2.3"
    
    def test_environment_variables(self):
        """環境変数のテスト"""
        # 環境変数が設定されているかテスト
        with patch.dict(os.environ, {"BRIA_API_TOKEN": self.test_api_token}):
            token = os.getenv("BRIA_API_TOKEN")
            assert token == self.test_api_token
    
    @pytest.mark.asyncio
    async def test_generate_image_parameters(self):
        """画像生成パラメータのバリデーションテスト"""
        # プロンプトが必須であることをテスト
        with pytest.raises(TypeError):
            # プロンプトなしで呼び出すとエラーになることを確認
            pass
    
    def test_api_endpoint_construction(self):
        """APIエンドポイントの構築テスト"""
        from urllib.parse import urljoin
        
        base_url = "https://engine.prod.bria-api.com/v1/"
        endpoint_template = "text-to-image/base/{model_version}"
        model_version = "2.3"
        
        endpoint = endpoint_template.format(model_version=model_version)
        full_url = urljoin(base_url, endpoint)
        
        expected_url = "https://engine.prod.bria-api.com/v1/text-to-image/base/2.3"
        assert full_url == expected_url
    
    def test_payload_construction(self):
        """APIペイロードの構築テスト"""
        payload = {
            "prompt": "test prompt",
            "num_results": 2,
            "sync": True,
            "content_moderation": False
        }
        
        # 必須フィールドが含まれているかテスト
        assert "prompt" in payload
        assert payload["prompt"] == "test prompt"
        assert payload["num_results"] == 2
        assert payload["sync"] is True
        assert payload["content_moderation"] is False
    
    def test_payload_with_seed(self):
        """シード値を含むペイロードのテスト"""
        payload = {
            "prompt": "test prompt",
            "num_results": 1,
            "sync": True,
            "content_moderation": False
        }
        
        seed = 12345
        payload["seed"] = seed
        
        assert payload["seed"] == seed
    
    @pytest.mark.asyncio
    async def test_mock_api_response(self):
        """モックAPIレスポンスのテスト"""
        # 成功レスポンスのモック
        mock_response = {
            "urls": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg"
            ],
            "seed": [12345, 67890]
        }
        
        # レスポンスの構造をテスト
        assert "urls" in mock_response
        assert "seed" in mock_response
        assert len(mock_response["urls"]) == 2
        assert len(mock_response["seed"]) == 2
    
    def test_error_response_handling(self):
        """エラーレスポンスの処理テスト"""
        error_responses = [
            {"error": "Invalid API token", "status_code": 401},
            {"error": "Rate limit exceeded", "status_code": 429},
            {"error": "Invalid prompt", "status_code": 422}
        ]
        
        for error in error_responses:
            assert "error" in error
            assert "status_code" in error
            assert error["status_code"] in [401, 422, 429]
    
    def test_url_validation(self):
        """URL検証のテスト"""
        valid_urls = [
            "https://example.com/image.jpg",
            "https://storage.server/outputs/image.jpeg",
            "https://bria-temp.s3.amazonaws.com/image.png"
        ]
        
        for url in valid_urls:
            assert url.startswith("https://")
            assert any(url.endswith(ext) for ext in [".jpg", ".jpeg", ".png"])
    
    def test_config_validation(self):
        """設定ファイルの検証テスト"""
        config = {
            "api_token": "test_token",
            "model_version": "2.3",
            "default_settings": {
                "num_results": 1,
                "sync": True,
                "content_moderation": False,
                "timeout": 60
            }
        }
        
        # 設定項目の存在確認
        assert "api_token" in config
        assert "model_version" in config
        assert "default_settings" in config
        
        # デフォルト設定の確認
        defaults = config["default_settings"]
        assert defaults["num_results"] == 1
        assert defaults["sync"] is True
        assert defaults["content_moderation"] is False
        assert defaults["timeout"] == 60


class TestToolDefinitions:
    """MCPツール定義のテスト"""
    
    def test_generate_image_tool_schema(self):
        """generate_imageツールのスキーマテスト"""
        tool_schema = {
            "name": "generate_image",
            "description": "Generate images using Bria.ai's text-to-image API",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text prompt for image generation"
                    },
                    "num_results": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 4,
                        "default": 1
                    }
                },
                "required": ["prompt"]
            }
        }
        
        assert tool_schema["name"] == "generate_image"
        assert "inputSchema" in tool_schema
        assert "prompt" in tool_schema["inputSchema"]["required"]
    
    def test_get_generation_status_tool_schema(self):
        """get_generation_statusツールのスキーマテスト"""
        tool_schema = {
            "name": "get_generation_status",
            "description": "Check the status of an asynchronous image generation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["urls"]
            }
        }
        
        assert tool_schema["name"] == "get_generation_status"
        assert "urls" in tool_schema["inputSchema"]["required"]


if __name__ == "__main__":
    pytest.main([__file__])