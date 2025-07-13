#!/usr/bin/env python3
"""
Bria.ai Image Generation MCP Server

This server provides tools to generate images using Bria.ai's text-to-image API.
"""

import json
import os
import sys
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

# MCPサーバーの基本コンポーネント
try:
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
except ImportError as e:
    print(f"Error importing MCP modules: {e}", file=sys.stderr)
    print("Please install the MCP library: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Bria.ai API設定
BRIA_API_BASE_URL = "https://engine.prod.bria-api.com/v1/"
BRIA_TEXT_TO_IMAGE_ENDPOINT = "text-to-image/base/{model_version}"

# MCPサーバーのインスタンス
server = Server("bria-image-generator")

# グローバル変数
api_token: Optional[str] = None
model_version: Optional[str] = None
http_client: Optional[httpx.AsyncClient] = None

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """利用可能なツールのリストを返す"""
    return [
        types.Tool(
            name="generate_image",
            description="Generate images using Bria.ai's text-to-image API",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text prompt for image generation"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of images to generate (1-4)",
                        "minimum": 1,
                        "maximum": 4,
                        "default": 1
                    },
                    "sync": {
                        "type": "boolean",
                        "description": "Whether to use synchronous generation",
                        "default": True
                    },
                    "seed": {
                        "type": "integer",
                        "description": "Optional seed for reproducible results",
                        "minimum": 0
                    },
                    "content_moderation": {
                        "type": "boolean",
                        "description": "Enable content moderation",
                        "default": False
                    }
                },
                "required": ["prompt"]
            }
        ),
        types.Tool(
            name="get_generation_status",
            description="Check the status of an asynchronous image generation",
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "URLs returned from async generation"
                    }
                },
                "required": ["urls"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """ツールを実行"""
    if name == "generate_image":
        return await generate_image(**arguments)
    elif name == "get_generation_status":
        return await get_generation_status(**arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def generate_image(
    prompt: str,
    num_results: int = 1,
    sync: bool = True,
    seed: Optional[int] = None,
    content_moderation: bool = False
) -> List[types.TextContent]:
    """Bria.ai APIを使用して画像を生成"""
    
    if not http_client:
        return [types.TextContent(type="text", text="HTTP client not initialized")]
    
    if not model_version:
        return [types.TextContent(type="text", text="Model version not set")]
    
    try:
        # APIエンドポイントを構築
        endpoint = BRIA_TEXT_TO_IMAGE_ENDPOINT.format(model_version=model_version)
        url = urljoin(BRIA_API_BASE_URL, endpoint)
        
        # リクエストペイロード
        payload = {
            "prompt": prompt,
            "num_results": num_results,
            "sync": sync,
            "content_moderation": content_moderation
        }
        
        if seed is not None:
            payload["seed"] = seed
        
        # APIリクエスト
        response = await http_client.post(url, json=payload)
        
        if response.status_code != 200:
            error_msg = f"API Error {response.status_code}: {response.text}"
            return [types.TextContent(type="text", text=error_msg)]
        
        result = response.json()
        
        # 結果を処理
        if sync:
            # 同期生成の場合
            if "urls" in result:
                urls = result["urls"]
                seeds = result.get("seed", [])
                
                output_lines = [
                    f"Generated {len(urls)} image(s) successfully:",
                    f"Prompt: {prompt}",
                    ""
                ]
                
                for i, url in enumerate(urls):
                    output_lines.append(f"Image {i+1}: {url}")
                    if i < len(seeds) and seeds[i] is not None:
                        output_lines.append(f"Seed {i+1}: {seeds[i]}")
                    output_lines.append("")
                
                return [types.TextContent(type="text", text="\n".join(output_lines))]
            else:
                return [types.TextContent(type="text", text=f"Unexpected response format: {result}")]
        else:
            # 非同期生成の場合
            urls = result.get("urls", [])
            output_lines = [
                f"Async generation started for {len(urls)} image(s):",
                f"Prompt: {prompt}",
                "",
                "Use get_generation_status with these URLs to check progress:"
            ]
            
            for i, url in enumerate(urls):
                output_lines.append(f"URL {i+1}: {url}")
            
            return [types.TextContent(type="text", text="\n".join(output_lines))]
            
    except httpx.TimeoutException:
        return [types.TextContent(type="text", text="Request timeout. Please try again.")]
    except httpx.RequestError as e:
        return [types.TextContent(type="text", text=f"Request error: {str(e)}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def get_generation_status(urls: List[str]) -> List[types.TextContent]:
    """非同期生成のステータスを確認"""
    
    if not http_client:
        return [types.TextContent(type="text", text="HTTP client not initialized")]
    
    try:
        status_results = []
        
        for i, url in enumerate(urls):
            try:
                # URLにアクセスして画像が利用可能かチェック
                response = await http_client.head(url)
                
                if response.status_code == 200:
                    status_results.append(f"Image {i+1}: Ready - {url}")
                elif response.status_code == 404:
                    status_results.append(f"Image {i+1}: Not ready yet")
                else:
                    status_results.append(f"Image {i+1}: Status {response.status_code}")
                    
            except Exception as e:
                status_results.append(f"Image {i+1}: Error checking status - {str(e)}")
        
        return [types.TextContent(type="text", text="\n".join(status_results))]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error checking status: {str(e)}")]

async def main():
    """メイン実行関数"""
    
    global api_token, model_version, http_client
    
    # 環境変数の確認
    api_token = os.getenv("BRIA_API_TOKEN")
    if not api_token:
        print("Error: BRIA_API_TOKEN environment variable is required", file=sys.stderr)
        print("Please set your Bria.ai API token:", file=sys.stderr)
        print("export BRIA_API_TOKEN='your_api_token_here'", file=sys.stderr)
        sys.exit(1)
    
    model_version = os.getenv("BRIA_MODEL_VERSION", "2.3")
    
    # HTTPクライアントの初期化
    http_client = httpx.AsyncClient(
        timeout=60.0,
        headers={
            "Content-Type": "application/json",
            "api_token": api_token
        }
    )
    
    # MCPサーバーの実行
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="bria-image-generator",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    except KeyboardInterrupt:
        print("Server shutdown requested", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if http_client:
            await http_client.aclose()

if __name__ == "__main__":
    asyncio.run(main())