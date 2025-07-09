"""
MCP Gmail API エンドポイント - FastAPI経由でMCP Gmailサービスをテスト
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.mcp_gmail import get_mcp_gmail_service, MCPError
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp-gmail", tags=["MCP Gmail"])

class EmailSendRequest(BaseModel):
    to: str
    subject: str
    body: str
    cc: Optional[str] = None
    bcc: Optional[str] = None

class EmailReplyRequest(BaseModel):
    body: str
    reply_all: bool = False

class EmailLabelRequest(BaseModel):
    label: str


@router.get("/test-connection")
async def test_mcp_connection():
    """MCP Gmail 接続テスト"""
    try:
        async with get_mcp_gmail_service() as service:
            tools = await service.list_tools()
            return {
                "status": "success",
                "message": "MCP Gmail接続成功",
                "tools_count": len(tools),
                "tools": [tool.get("name") for tool in tools]
            }
    except MCPError as e:
        logger.error(f"MCP接続エラー: {e}")
        raise HTTPException(status_code=500, detail=f"MCP接続エラー: {e}")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        raise HTTPException(status_code=500, detail=f"予期しないエラー: {e}")


@router.get("/tools")
async def list_available_tools():
    """利用可能なツール一覧を取得"""
    try:
        async with get_mcp_gmail_service() as service:
            tools = await service.list_tools()
            return {
                "status": "success",
                "tools": tools
            }
    except MCPError as e:
        logger.error(f"ツール一覧取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"ツール一覧取得エラー: {e}")


@router.get("/emails")
async def get_emails(
    query: str = "",
    max_results: int = 10
):
    """メール一覧を取得"""
    try:
        async with get_mcp_gmail_service() as service:
            emails = await service.get_emails(query=query, max_results=max_results)
            return {
                "status": "success",
                "query": query,
                "max_results": max_results,
                "emails_count": len(emails),
                "emails": emails
            }
    except MCPError as e:
        logger.error(f"メール取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"メール取得エラー: {e}")


@router.get("/emails/{email_id}")
async def get_email_content(email_id: str):
    """特定のメール内容を取得"""
    try:
        async with get_mcp_gmail_service() as service:
            email_content = await service.get_email_content(email_id)
            return {
                "status": "success",
                "email_id": email_id,
                "content": email_content
            }
    except MCPError as e:
        logger.error(f"メール内容取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"メール内容取得エラー: {e}")


@router.post("/emails/send")
async def send_email(
    request: EmailSendRequest
):
    """メールを送信"""
    try:
        async with get_mcp_gmail_service() as service:
            result = await service.send_email(
                to=request.to,
                subject=request.subject,
                body=request.body,
                cc=request.cc,
                bcc=request.bcc
            )
            return {
                "status": "success",
                "message": "メール送信完了",
                "result": result
            }
    except MCPError as e:
        logger.error(f"メール送信エラー: {e}")
        raise HTTPException(status_code=500, detail=f"メール送信エラー: {e}")


@router.post("/emails/{email_id}/reply")
async def reply_to_email(
    email_id: str,
    request: EmailReplyRequest
):
    """メールに返信"""
    try:
        async with get_mcp_gmail_service() as service:
            result = await service.reply_to_email(
                email_id=email_id,
                body=request.body,
                reply_all=request.reply_all
            )
            return {
                "status": "success",
                "message": "返信完了",
                "email_id": email_id,
                "result": result
            }
    except MCPError as e:
        logger.error(f"返信エラー: {e}")
        raise HTTPException(status_code=500, detail=f"返信エラー: {e}")


@router.patch("/emails/{email_id}/mark-read")
async def mark_email_as_read(email_id: str):
    """メールを既読にマーク"""
    try:
        async with get_mcp_gmail_service() as service:
            result = await service.mark_as_read(email_id)
            return {
                "status": "success",
                "message": "既読マーク完了",
                "email_id": email_id,
                "result": result
            }
    except MCPError as e:
        logger.error(f"既読マークエラー: {e}")
        raise HTTPException(status_code=500, detail=f"既読マークエラー: {e}")


@router.patch("/emails/{email_id}/mark-unread")
async def mark_email_as_unread(email_id: str):
    """メールを未読にマーク"""
    try:
        async with get_mcp_gmail_service() as service:
            result = await service.mark_as_unread(email_id)
            return {
                "status": "success",
                "message": "未読マーク完了",
                "email_id": email_id,
                "result": result
            }
    except MCPError as e:
        logger.error(f"未読マークエラー: {e}")
        raise HTTPException(status_code=500, detail=f"未読マークエラー: {e}")


@router.post("/emails/{email_id}/labels")
async def add_label_to_email(
    email_id: str,
    request: EmailLabelRequest
):
    """メールにラベルを追加"""
    try:
        async with get_mcp_gmail_service() as service:
            result = await service.add_label(email_id, request.label)
            return {
                "status": "success",
                "message": "ラベル追加完了",
                "email_id": email_id,
                "label": request.label,
                "result": result
            }
    except MCPError as e:
        logger.error(f"ラベル追加エラー: {e}")
        raise HTTPException(status_code=500, detail=f"ラベル追加エラー: {e}")


@router.delete("/emails/{email_id}/labels/{label}")
async def remove_label_from_email(
    email_id: str,
    label: str
):
    """メールからラベルを削除"""
    try:
        async with get_mcp_gmail_service() as service:
            result = await service.remove_label(email_id, label)
            return {
                "status": "success",
                "message": "ラベル削除完了",
                "email_id": email_id,
                "label": label,
                "result": result
            }
    except MCPError as e:
        logger.error(f"ラベル削除エラー: {e}")
        raise HTTPException(status_code=500, detail=f"ラベル削除エラー: {e}")


@router.post("/drafts")
async def create_draft(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None
):
    """下書きを作成"""
    try:
        async with get_mcp_gmail_service() as service:
            result = await service.create_draft(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc
            )
            return {
                "status": "success",
                "message": "下書き作成完了",
                "result": result
            }
    except MCPError as e:
        logger.error(f"下書き作成エラー: {e}")
        raise HTTPException(status_code=500, detail=f"下書き作成エラー: {e}")
