# アーキテクチャ / ディレクトリ構成

## 技術スタック

- フロントエンド: Next.js（App Router）, TypeScript, Tailwind CSS, shadcn/ui
- バックエンド: FastAPI, SQLModel, Alembic
- 認証: Clerk
- コンテナ: Docker / Docker Compose（任意）

## ルート構成

```
backend/           # FastAPI アプリケーション
frontend/          # Next.js アプリケーション
docker-compose.yml # ローカル開発用コンテナ定義
README.md          # 概要と環境構築（簡潔版）
AGENTS.md          # コントリビューション/運用ガイド（日本語対応方針含む）
docs/              # 詳細ドキュメント
```

## Backend (FastAPI)

主なディレクトリ:

- `app/routers`       ルータ（API エンドポイント定義）
- `app/models`        Pydantic モデル（リクエスト/レスポンス）
- `app/services`      ビジネスロジック
- `app/repositories`  DB アクセス（永続化）
- `app/utils`         共通ユーティリティ
- `app/migrations`    Alembic マイグレーション

エントリポイント: `backend/main.py`

## Frontend (Next.js)

主なディレクトリ:

- `app/`                        ルート配下のページ/レイアウト
- `components/components/{commons,forms,ui}`  再利用コンポーネント（ui, lib は shadcn 生成のため非変更）
- `components/hooks`            カスタムフック
- `components/lib`              ライブラリ（自動生成/非変更）
- `components/pages`            ページレベルのビュー
- `types/`                      型定義
- `utils/`                      共通ユーティリティ

## 開発フローの原則

- ルータは薄く（バリデーション・入出力定義中心）、ビジネスロジックはサービス層へ。
- リポジトリは DB への読み書き責務を担当し、テスタビリティを高める。
- フロントは App Router 構成に則り、責務ごとにコンポーネントを分割。

