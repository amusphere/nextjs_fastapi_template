"""
MCP Gmail サービス - Gmail MCPサーバーとの通信を管理するサービスレイヤー

このサービスは docker-compose.yml で定義された mcp_gmail コンテナと
Model Context Protocol (MCP) を使って通信し、Gmail操作を提供します。

Docker Compose環境での接続方法：
1. Docker Socket マウントによりホストのDockerデーモンにアクセス
2. mcp_gmailコンテナでMCPサーバーとSTDIO通信
"""

import asyncio
import json
import logging
import subprocess
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPError(Exception):
    """MCP通信エラー"""
    pass


class MCPGmailService:
    """Gmail MCP サーバーとの通信を管理するサービスクラス"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.request_id_counter = 0

    async def __aenter__(self):
        """非同期コンテキストマネージャー - 接続開始"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャー - 接続終了"""
        await self.disconnect()

    async def connect(self):
        """MCP Gmail サーバーに接続"""
        try:
            # Docker環境の判定
            is_docker = os.path.exists("/.dockerenv")

            if is_docker:
                # Docker Compose環境内での接続
                logger.info("Docker環境内での接続を開始...")

                # Docker Socket経由でmcp_gmailコンテナと通信
                # /var/run/docker.sockがマウントされている前提
                cmd = [
                    "docker", "exec", "-i", "mcp_gmail",
                    "python", "-c",
                    "import sys; sys.path.append('/app/src'); from mcp_server_headless_gmail import main; main()"
                ]
            else:
                # ローカル環境での接続
                logger.info("ローカル環境での接続を開始...")
                cmd = [
                    "docker", "exec", "-i", "mcp_gmail",
                    "python", "-c",
                    "import sys; sys.path.append('/app/src'); from mcp_server_headless_gmail import main; main()"
                ]

            # MCP サーバープロセスを開始
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
            )

            # 初期化メッセージを送信
            self._send_initialize()
            logger.info("MCP Gmail サーバーに正常に接続しました")

        except Exception as e:
            logger.error(f"MCP Gmail サーバーへの接続に失敗: {e}")
            raise MCPError(f"接続エラー: {e}")

    async def disconnect(self):
        """MCP Gmail サーバーから切断"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except Exception as e:
                logger.error(f"切断エラー: {e}")
            finally:
                self.process = None

    def _send_initialize(self):
        """MCP初期化メッセージを送信"""
        init_request = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "aureca-backend", "version": "1.0.0"},
            },
        }

        response = self._send_request(init_request)
        if "error" in response:
            raise MCPError(f"初期化エラー: {response['error']}")

        # initialized 通知を送信
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        self._send_notification(initialized_notification)

    def _get_request_id(self) -> str:
        """リクエストIDを生成"""
        self.request_id_counter += 1
        return str(self.request_id_counter)

    def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """MCPリクエストを送信し、レスポンスを受信"""
        if not self.process or not self.process.stdin:
            raise MCPError("MCPサーバーに接続されていません")

        try:
            # リクエストを送信
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()

            # レスポンスを受信
            response_line = self.process.stdout.readline()
            if not response_line:
                raise MCPError("MCPサーバーからの応答がありません")

            response = json.loads(response_line.strip())
            return response

        except json.JSONDecodeError as e:
            raise MCPError(f"JSON解析エラー: {e}")
        except Exception as e:
            raise MCPError(f"通信エラー: {e}")

    def _send_notification(self, notification: Dict[str, Any]):
        """MCP通知を送信（レスポンス不要）"""
        if not self.process or not self.process.stdin:
            raise MCPError("MCPサーバーに接続されていません")

        try:
            notification_json = json.dumps(notification) + "\n"
            self.process.stdin.write(notification_json)
            self.process.stdin.flush()
        except Exception as e:
            raise MCPError(f"通知送信エラー: {e}")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """利用可能なツール一覧を取得"""
        request = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": "tools/list",
        }

        response = self._send_request(request)
        if "error" in response:
            raise MCPError(f"ツール一覧取得エラー: {response['error']}")

        return response.get("result", {}).get("tools", [])

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """指定したツールを実行"""
        request = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        response = self._send_request(request)
        if "error" in response:
            raise MCPError(f"ツール実行エラー: {response['error']}")

        return response.get("result", {})

    # Gmail操作の高レベルメソッド

    async def get_emails(
        self, query: str = "", max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """メール一覧を取得"""
        try:
            result = await self.call_tool(
                "search_emails", {"query": query, "max_results": max_results}
            )
            # MCP Gmail サーバーからのレスポンス形式に応じて調整
            return result.get("content", [])
        except Exception as e:
            logger.error(f"メール取得エラー: {e}")
            raise MCPError(f"メール取得に失敗しました: {e}")

    async def get_email_content(self, email_id: str) -> Dict[str, Any]:
        """特定のメール内容を取得"""
        try:
            result = await self.call_tool("get_email", {"email_id": email_id})
            return result.get("content", [{}])[0] if result.get("content") else {}
        except Exception as e:
            logger.error(f"メール内容取得エラー: {e}")
            raise MCPError(f"メール内容取得に失敗しました: {e}")

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
    ) -> Dict[str, Any]:
        """メールを送信"""
        try:
            arguments = {"to": to, "subject": subject, "body": body}
            if cc:
                arguments["cc"] = cc
            if bcc:
                arguments["bcc"] = bcc

            result = await self.call_tool("send_email", arguments)
            return result.get("content", [{}])[0] if result.get("content") else {}
        except Exception as e:
            logger.error(f"メール送信エラー: {e}")
            raise MCPError(f"メール送信に失敗しました: {e}")

    async def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
    ) -> Dict[str, Any]:
        """下書きを作成"""
        try:
            arguments = {"to": to, "subject": subject, "body": body}
            if cc:
                arguments["cc"] = cc
            if bcc:
                arguments["bcc"] = bcc

            result = await self.call_tool("create_draft", arguments)
            return result.get("content", [{}])[0] if result.get("content") else {}
        except Exception as e:
            logger.error(f"下書き作成エラー: {e}")
            raise MCPError(f"下書き作成に失敗しました: {e}")

    async def reply_to_email(
        self, email_id: str, body: str, reply_all: bool = False
    ) -> Dict[str, Any]:
        """メールに返信"""
        try:
            result = await self.call_tool(
                "reply_to_email",
                {"email_id": email_id, "body": body, "reply_all": reply_all},
            )
            return result.get("content", [{}])[0] if result.get("content") else {}
        except Exception as e:
            logger.error(f"メール返信エラー: {e}")
            raise MCPError(f"メール返信に失敗しました: {e}")

    async def mark_as_read(self, email_id: str) -> Dict[str, Any]:
        """メールを既読にマーク"""
        try:
            result = await self.call_tool("mark_as_read", {"email_id": email_id})
            return result.get("content", [{}])[0] if result.get("content") else {}
        except Exception as e:
            logger.error(f"既読マークエラー: {e}")
            raise MCPError(f"既読マークに失敗しました: {e}")

    async def mark_as_unread(self, email_id: str) -> Dict[str, Any]:
        """メールを未読にマーク"""
        try:
            result = await self.call_tool("mark_as_unread", {"email_id": email_id})
            return result.get("content", [{}])[0] if result.get("content") else {}
        except Exception as e:
            logger.error(f"未読マークエラー: {e}")
            raise MCPError(f"未読マークに失敗しました: {e}")

    async def add_label(self, email_id: str, label: str) -> Dict[str, Any]:
        """メールにラベルを追加"""
        try:
            result = await self.call_tool(
                "add_label", {"email_id": email_id, "label": label}
            )
            return result.get("content", [{}])[0] if result.get("content") else {}
        except Exception as e:
            logger.error(f"ラベル追加エラー: {e}")
            raise MCPError(f"ラベル追加に失敗しました: {e}")

    async def remove_label(self, email_id: str, label: str) -> Dict[str, Any]:
        """メールからラベルを削除"""
        try:
            result = await self.call_tool(
                "remove_label", {"email_id": email_id, "label": label}
            )
            return result.get("content", [{}])[0] if result.get("content") else {}
        except Exception as e:
            logger.error(f"ラベル削除エラー: {e}")
            raise MCPError(f"ラベル削除に失敗しました: {e}")


# ファクトリー関数とユーティリティ

@asynccontextmanager
async def get_mcp_gmail_service():
    """MCPGmailServiceのコンテキストマネージャー"""
    service = MCPGmailService()
    try:
        async with service:
            yield service
    except Exception as e:
        logger.error(f"MCP Gmail サービスエラー: {e}")
        raise


async def test_mcp_connection() -> bool:
    """MCP Gmail 接続テスト"""
    try:
        async with get_mcp_gmail_service() as service:
            tools = await service.list_tools()
            logger.info(f"利用可能なツール: {len(tools)}個")
            return True
    except Exception as e:
        logger.error(f"接続テスト失敗: {e}")
        return False


# 使用例
if __name__ == "__main__":
    import asyncio

    async def main():
        # 接続テスト
        print("MCP Gmail 接続テスト中...")
        success = await test_mcp_connection()
        print(f"接続テスト結果: {'成功' if success else '失敗'}")

        if success:
            # メール操作の例
            async with get_mcp_gmail_service() as service:
                # 利用可能なツール一覧
                tools = await service.list_tools()
                print(f"利用可能なツール: {[tool.get('name') for tool in tools]}")

                # 最新のメールを取得
                emails = await service.get_emails(max_results=5)
                print(f"取得したメール数: {len(emails)}")

    asyncio.run(main())
