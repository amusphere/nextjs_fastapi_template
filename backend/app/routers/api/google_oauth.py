import os

import requests
from app.database import get_session
from app.schema import User
from app.services.auth import auth_user
from app.utils.google_calendar import GoogleCalendarService
from fastapi import APIRouter, Depends, HTTPException, status
from google_auth_oauthlib.flow import Flow
from pydantic import BaseModel
from sqlmodel import Session

router = APIRouter(prefix="/google")

# Google OAuth設定
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:3000/api/auth/google/callback"
)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# Google Calendar API のスコープ
SCOPES = [
    "openid",  # Google が自動で追加するため明示的に含める
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


class GoogleAuthUrlResponse(BaseModel):
    auth_url: str


class GoogleCallbackRequest(BaseModel):
    code: str
    state: str


class GoogleAuthResponse(BaseModel):
    success: bool
    message: str


@router.get("/auth-url", response_model=GoogleAuthUrlResponse)
async def get_google_auth_url(user: User = Depends(auth_user)):
    """Google OAuth認証URLを生成"""
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI],
                }
            },
            scopes=SCOPES,
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI

        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            state=str(user.id),  # ユーザーIDをstateに含める
        )

        return GoogleAuthUrlResponse(auth_url=auth_url)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate auth URL: {str(e)}",
        )


@router.post("/callback", response_model=GoogleAuthResponse)
async def google_oauth_callback(
    request: GoogleCallbackRequest,
    session: Session = Depends(get_session),
):
    """Google OAuth認証コールバック処理"""
    try:
        # stateからユーザーIDを取得
        user_id = int(request.state)

        # 認証コードをアクセストークンに交換
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI],
                }
            },
            scopes=SCOPES,
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI

        # 認証コードでトークンを取得
        try:
            flow.fetch_token(code=request.code)
            credentials = flow.credentials
        except Exception as e:
            # スコープの違いエラーの場合、より寛容な設定でリトライ
            error_msg = str(e)
            if "Scope has changed" in error_msg:
                print(
                    f"Scope change detected (this is normal with Google OAuth): {error_msg}"
                )

                # 新しいフローを作成し、include_granted_scopesを使用
                flow = Flow.from_client_config(
                    {
                        "web": {
                            "client_id": GOOGLE_CLIENT_ID,
                            "client_secret": GOOGLE_CLIENT_SECRET,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": [GOOGLE_REDIRECT_URI],
                        }
                    },
                    scopes=SCOPES,
                )
                flow.redirect_uri = GOOGLE_REDIRECT_URI

                # include_granted_scopesを使ってトークンを取得
                flow.fetch_token(code=request.code, include_granted_scopes=True)
                credentials = flow.credentials
            else:
                raise e

        # ユーザー情報を取得（People APIの代わりにOAuth2 userinfoエンドポイントを使用）

        # OAuth2 userinfo エンドポイントを使用してユーザー情報を取得
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

        headers = {"Authorization": f"Bearer {credentials.token}"}
        response = requests.get(userinfo_url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch user info: {response.text}",
            )

        user_info = response.json()
        google_email = user_info.get("email")
        google_user_id = user_info.get("id")

        # トークンをデータベースに保存
        calendar_service = GoogleCalendarService(ENCRYPTION_KEY, session)
        calendar_service.store_oauth_tokens(
            user_id=user_id,
            credentials=credentials,
            google_user_id=google_user_id,
            google_email=google_email,
        )

        return GoogleAuthResponse(
            success=True, message="Google account connected successfully"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process callback: {str(e)}",
        )


@router.delete("/disconnect")
async def disconnect_google_account(
    user: User = Depends(auth_user),
    session: Session = Depends(get_session),
):
    """Google アカウントの連携を解除"""
    try:
        calendar_service = GoogleCalendarService(ENCRYPTION_KEY, session)
        calendar_service.revoke_access(user.id)

        return GoogleAuthResponse(
            success=True, message="Google account disconnected successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect account: {str(e)}",
        )


@router.get("/status")
async def get_google_connection_status(
    user: User = Depends(auth_user),
    session: Session = Depends(get_session),
):
    """Google連携状況を確認"""
    try:
        calendar_service = GoogleCalendarService(ENCRYPTION_KEY, session)
        credentials = calendar_service.get_credentials(user.id)

        return {"connected": credentials is not None, "user_id": user.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check connection status: {str(e)}",
        )
