"""
統合型 Gmail API エンドポイント（推奨実装）
既存のAPIインターフェースを維持しながら、バックエンドを統合型に変更
"""

import logging
from typing import Optional

from app.database import get_session
from app.schema import User
from app.services.auth import auth_user
from app.services.gmail_integrated import (
    GmailServiceError,
    get_authenticated_gmail_service,
    get_integrated_gmail_service,
)
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gmail", tags=["Gmail (Integrated)"])


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
async def test_gmail_connection():
    """Gmail API 接続テスト"""
    try:
        async with get_integrated_gmail_service():
            # 接続テスト（認証情報なしでもサービス作成は可能）
            return {
                "status": "success",
                "message": "Gmail統合サービス接続成功",
                "service_type": "integrated_gmail_api",
                "features": [
                    "direct_api_access",
                    "full_gmail_functionality",
                    "high_performance",
                ],
            }
    except GmailServiceError as e:
        logger.error(f"Gmail接続エラー: {e}")
        raise HTTPException(status_code=500, detail=f"Gmail接続エラー: {e}")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        raise HTTPException(status_code=500, detail=f"予期しないエラー: {e}")


@router.get("/emails")
async def get_emails(
    query: str = "",
    max_results: int = 10,
    user: User = Depends(auth_user),
    session: Session = Depends(get_session),
):
    """メール一覧を取得"""
    try:
        async with get_authenticated_gmail_service(user, session) as service:
            emails = await service.get_emails(query=query, max_results=max_results)
            return {
                "status": "success",
                "query": query,
                "max_results": max_results,
                "emails_count": len(emails),
                "emails": emails,
                "service_type": "integrated",
            }
    except GmailServiceError as e:
        logger.error(f"メール取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"メール取得エラー: {e}")


@router.get("/emails/{email_id}")
async def get_email_content(
    email_id: str,
    user: User = Depends(auth_user),
    session: Session = Depends(get_session),
):
    """特定のメール内容を取得"""
    try:
        async with get_authenticated_gmail_service(user, session) as service:
            email_content = await service.get_email_content(email_id)
            return {
                "status": "success",
                "email_id": email_id,
                "content": email_content,
                "service_type": "integrated",
            }
    except GmailServiceError as e:
        logger.error(f"メール内容取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"メール内容取得エラー: {e}")


@router.post("/emails/send")
async def send_email(
    request: EmailSendRequest,
    user: User = Depends(auth_user),
    session: Session = Depends(get_session),
):
    """メールを送信"""
    try:
        async with get_authenticated_gmail_service(user, session) as service:
            result = await service.send_email(
                to=request.to,
                subject=request.subject,
                body=request.body,
                cc=request.cc,
                bcc=request.bcc,
            )
            return {
                "status": "success",
                "message": "メール送信完了",
                "result": result,
                "service_type": "integrated",
            }
    except GmailServiceError as e:
        logger.error(f"メール送信エラー: {e}")
        raise HTTPException(status_code=500, detail=f"メール送信エラー: {e}")


@router.post("/drafts")
async def create_draft(
    request: EmailSendRequest,
    user: User = Depends(auth_user),
    session: Session = Depends(get_session),
):
    """下書きを作成"""
    try:
        async with get_authenticated_gmail_service(user, session) as service:
            result = await service.create_draft(
                to=request.to,
                subject=request.subject,
                body=request.body,
                cc=request.cc,
                bcc=request.bcc,
            )
            return {
                "status": "success",
                "message": "下書き作成完了",
                "result": result,
                "service_type": "integrated",
            }
    except GmailServiceError as e:
        logger.error(f"下書き作成エラー: {e}")
        raise HTTPException(status_code=500, detail=f"下書き作成エラー: {e}")


@router.patch("/emails/{email_id}/mark-read")
async def mark_email_as_read(
    email_id: str,
    user: User = Depends(auth_user),
    session: Session = Depends(get_session),
):
    """メールを既読にマーク"""
    try:
        async with get_authenticated_gmail_service(user, session) as service:
            result = await service.mark_as_read(email_id)
            return {
                "status": "success",
                "message": "既読マーク完了",
                "email_id": email_id,
                "result": result,
                "service_type": "integrated",
            }
    except GmailServiceError as e:
        logger.error(f"既読マークエラー: {e}")
        raise HTTPException(status_code=500, detail=f"既読マークエラー: {e}")


@router.patch("/emails/{email_id}/mark-unread")
async def mark_email_as_unread(
    email_id: str,
    user: User = Depends(auth_user),
    session: Session = Depends(get_session),
):
    """メールを未読にマーク"""
    try:
        async with get_authenticated_gmail_service(user, session) as service:
            result = await service.mark_as_unread(email_id)
            return {
                "status": "success",
                "message": "未読マーク完了",
                "email_id": email_id,
                "result": result,
                "service_type": "integrated",
            }
    except GmailServiceError as e:
        logger.error(f"未読マークエラー: {e}")
        raise HTTPException(status_code=500, detail=f"未読マークエラー: {e}")
