"""
Gmail MCP 統合サービス（推奨実装）

MCPサーバーを別プロセスとして起動するのではなく、
MCPライブラリを直接使用してGmail機能を実装
"""

import base64
import email.mime.text
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from app.schema import User
from app.services.google_oauth import GoogleOauthService
from google.oauth2.credentials import Credentials as OAuth2Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlmodel import Session

logger = logging.getLogger(__name__)


class GmailServiceError(Exception):
    """Gmail サービスエラー"""

    pass


class IntegratedGmailService:
    """Gmail API を直接使用する統合サービス（推奨実装）"""

    def __init__(self, user: Optional[User] = None, session: Optional[Session] = None):
        self.user = user
        self.db_session = session
        self.gmail_service = None
        self._credentials: Optional[OAuth2Credentials] = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        """Gmail API サービスに接続"""
        try:
            logger.info("Gmail API に直接接続中...")

            if self.user and self.db_session:
                await self._setup_credentials()

                # Gmail API サービスを構築
                self.gmail_service = build("gmail", "v1", credentials=self._credentials)

            logger.info("Gmail API に正常に接続しました")

        except Exception as e:
            logger.error(f"Gmail API への接続に失敗: {e}")
            raise GmailServiceError(f"接続エラー: {e}")

    async def _setup_credentials(self):
        """Google OAuth認証情報を設定"""
        try:
            oauth_service = GoogleOauthService(self.db_session)
            credentials = oauth_service.get_credentials(self.user.id)

            if not credentials:
                raise GmailServiceError(
                    "Google認証情報が見つかりません。再認証が必要です。"
                )

            # OAuth2Credentialsオブジェクトを構築
            self._credentials = OAuth2Credentials(
                token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
                scopes=[
                    "https://www.googleapis.com/auth/gmail.readonly",
                    "https://www.googleapis.com/auth/gmail.send",
                    "https://www.googleapis.com/auth/gmail.modify",
                ],
            )

            logger.info("Google OAuth認証情報を設定しました")

        except Exception as e:
            logger.error(f"認証設定エラー: {e}")
            raise GmailServiceError(f"認証設定に失敗しました: {e}")

    async def disconnect(self):
        """Gmail API サービスから切断"""
        # Gmail API は状態を持たないため、特別な切断処理は不要
        self.gmail_service = None
        self._credentials = None

    # Gmail操作メソッド

    async def get_emails(
        self, query: str = "", max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """メール一覧を取得"""
        try:
            if not self.gmail_service:
                raise GmailServiceError("Gmail サービスに接続されていません")

            # メッセージ一覧を取得
            result = (
                self.gmail_service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )

            messages = result.get("messages", [])
            email_list = []

            for message in messages:
                # 各メッセージの詳細を取得
                msg = (
                    self.gmail_service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=message["id"],
                        format="metadata",
                        metadataHeaders=["From", "To", "Subject", "Date"],
                    )
                    .execute()
                )

                # メタデータを整理
                headers = msg["payload"].get("headers", [])
                email_data = {
                    "id": msg["id"],
                    "threadId": msg["threadId"],
                    "snippet": msg.get("snippet", ""),
                }

                for header in headers:
                    name = header["name"].lower()
                    if name in ["from", "to", "subject", "date"]:
                        email_data[name] = header["value"]

                email_list.append(email_data)

            return email_list

        except HttpError as e:
            logger.error(f"Gmail API エラー: {e}")
            raise GmailServiceError(f"メール取得に失敗しました: {e}")
        except Exception as e:
            logger.error(f"メール取得エラー: {e}")
            raise GmailServiceError(f"メール取得に失敗しました: {e}")

    async def get_email_content(self, email_id: str) -> Dict[str, Any]:
        """特定のメール内容を取得"""
        try:
            if not self.gmail_service:
                raise GmailServiceError("Gmail サービスに接続されていません")

            msg = (
                self.gmail_service.users()
                .messages()
                .get(userId="me", id=email_id, format="full")
                .execute()
            )

            # メール本文を抽出
            body = self._extract_message_body(msg["payload"])

            # ヘッダー情報を抽出
            headers = msg["payload"].get("headers", [])
            email_data = {
                "id": msg["id"],
                "threadId": msg["threadId"],
                "body": body,
                "snippet": msg.get("snippet", ""),
            }

            for header in headers:
                name = header["name"].lower()
                if name in ["from", "to", "subject", "date", "cc", "bcc"]:
                    email_data[name] = header["value"]

            return email_data

        except HttpError as e:
            logger.error(f"Gmail API エラー: {e}")
            raise GmailServiceError(f"メール内容取得に失敗しました: {e}")
        except Exception as e:
            logger.error(f"メール内容取得エラー: {e}")
            raise GmailServiceError(f"メール内容取得に失敗しました: {e}")

    def _extract_message_body(self, payload: Dict[str, Any]) -> str:
        """メッセージペイロードから本文を抽出"""
        body = ""

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data")
                    if data:
                        body = base64.urlsafe_b64decode(data).decode("utf-8")
                        break
                elif part["mimeType"] == "text/html" and not body:
                    data = part["body"].get("data")
                    if data:
                        body = base64.urlsafe_b64decode(data).decode("utf-8")
        else:
            if payload["mimeType"] in ["text/plain", "text/html"]:
                data = payload["body"].get("data")
                if data:
                    body = base64.urlsafe_b64decode(data).decode("utf-8")

        return body

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
            if not self.gmail_service:
                raise GmailServiceError("Gmail サービスに接続されていません")

            # メッセージを構築
            message = email.mime.text.MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            if cc:
                message["cc"] = cc
            if bcc:
                message["bcc"] = bcc

            # Base64エンコード
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            # メール送信
            result = (
                self.gmail_service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )

            return {
                "id": result["id"],
                "threadId": result["threadId"],
                "status": "sent",
            }

        except HttpError as e:
            logger.error(f"Gmail API エラー: {e}")
            raise GmailServiceError(f"メール送信に失敗しました: {e}")
        except Exception as e:
            logger.error(f"メール送信エラー: {e}")
            raise GmailServiceError(f"メール送信に失敗しました: {e}")

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
            if not self.gmail_service:
                raise GmailServiceError("Gmail サービスに接続されていません")

            # メッセージを構築
            message = email.mime.text.MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            if cc:
                message["cc"] = cc
            if bcc:
                message["bcc"] = bcc

            # Base64エンコード
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            # 下書き作成
            result = (
                self.gmail_service.users()
                .drafts()
                .create(userId="me", body={"message": {"raw": raw_message}})
                .execute()
            )

            return {
                "id": result["id"],
                "message": result["message"],
                "status": "draft_created",
            }

        except HttpError as e:
            logger.error(f"Gmail API エラー: {e}")
            raise GmailServiceError(f"下書き作成に失敗しました: {e}")
        except Exception as e:
            logger.error(f"下書き作成エラー: {e}")
            raise GmailServiceError(f"下書き作成に失敗しました: {e}")

    # 未実装機能（Gmail APIで実装可能）
    async def mark_as_read(self, email_id: str) -> Dict[str, Any]:
        """メールを既読にマーク"""
        try:
            if not self.gmail_service:
                raise GmailServiceError("Gmail サービスに接続されていません")

            result = (
                self.gmail_service.users()
                .messages()
                .modify(userId="me", id=email_id, body={"removeLabelIds": ["UNREAD"]})
                .execute()
            )

            return {"id": result["id"], "status": "marked_as_read"}

        except HttpError as e:
            logger.error(f"Gmail API エラー: {e}")
            raise GmailServiceError(f"既読マークに失敗しました: {e}")

    async def mark_as_unread(self, email_id: str) -> Dict[str, Any]:
        """メールを未読にマーク"""
        try:
            if not self.gmail_service:
                raise GmailServiceError("Gmail サービスに接続されていません")

            result = (
                self.gmail_service.users()
                .messages()
                .modify(userId="me", id=email_id, body={"addLabelIds": ["UNREAD"]})
                .execute()
            )

            return {"id": result["id"], "status": "marked_as_unread"}

        except HttpError as e:
            logger.error(f"Gmail API エラー: {e}")
            raise GmailServiceError(f"未読マークに失敗しました: {e}")


# ファクトリー関数


@asynccontextmanager
async def get_integrated_gmail_service(
    user: Optional[User] = None, session: Optional[Session] = None
):
    """IntegratedGmailServiceのコンテキストマネージャー"""
    service = IntegratedGmailService(user=user, session=session)
    try:
        async with service:
            yield service
    except Exception as e:
        logger.error(f"Gmail サービスエラー: {e}")
        raise


@asynccontextmanager
async def get_authenticated_gmail_service(user: User, session: Session):
    """認証付きIntegratedGmailServiceのコンテキストマネージャー"""
    async with get_integrated_gmail_service(user=user, session=session) as service:
        yield service
