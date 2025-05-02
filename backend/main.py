from app.routers.api.health import router as health_router
from app.routers.api.users import router as users_router
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 環境変数の読み込み
load_dotenv()

# アプリケーションとログの設定
app = FastAPI(
    redirect_slashes=False,
)

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(health_router, prefix="/api", tags=["api"])
app.include_router(users_router, prefix="/api", tags=["api"])
