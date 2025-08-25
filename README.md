# Next.js + FastAPI Template

[![CI](https://github.com/amusphere/nextjs_fastapi_template/actions/workflows/ci.yml/badge.svg)](https://github.com/amusphere/nextjs_fastapi_template/actions/workflows/ci.yml)

モダンなフロントエンド（Next.js）と高速なバックエンド（FastAPI）で構成されたテンプレートです。開発体験・パフォーマンス・拡張性を重視したスタータープロジェクトとして利用できます。

## 概要

- フロントエンド: Next.js（App Router）, TypeScript, Tailwind CSS, shadcn/ui
- バックエンド: FastAPI, SQLModel, Alembic
- 認証: Clerk
- コンテナ: Docker / Docker Compose（任意）

詳細な構成や開発手順は [docs/](./docs/README.md) 以下に分割して掲載しています。まずは環境構築手順に従ってローカルで起動してください。

## 環境構築（ローカル）

### 前提条件
- Node.js 20 以上（npm 同梱）
- Python 3.11+ と `uv`
- （任意）Docker / Docker Compose

### 環境変数の作成
`backend/` と `frontend/` の両方で `.env.sample` を `.env` にコピーし、必要値を設定します。

```bash
cp backend/.env.sample backend/.env
cp frontend/.env.sample frontend/.env
```

### 起動手順（ローカル実行）
- バックエンド（FastAPI 開発サーバ）
  - ルートで実行: `uv run fastapi dev --host 0.0.0.0 --port 8000`
  - DB マイグレーション: `uv run alembic upgrade head`
- フロントエンド（Next.js）
  - `cd frontend && npm install`
  - `npm run dev`

表示確認:
- Web: http://localhost:3000
- API: http://localhost:8000/docs

## Docker で実行（任意）

```bash
docker compose build
docker compose up
```

DB マイグレーション:

```bash
docker compose run --rm backend alembic upgrade head
```

## 追加ドキュメント（docs/）

- [docs/README.md](./docs/README.md): 目次とガイドへのリンク
- [docs/architecture.md](./docs/architecture.md): 技術スタック・ディレクトリ構成
- [docs/backend.md](./docs/backend.md): ルータ/サービス/リポジトリの役割、API作成手順、マイグレーション
- [docs/frontend.md](./docs/frontend.md): ページ・コンポーネント構成、開発手順
- [docs/docker.md](./docs/docker.md): Docker 運用・コマンド
- [docs/environment.md](./docs/environment.md): 必要な環境変数一覧
- [docs/testing.md](./docs/testing.md): テストの方針と実行方法
- [docs/contributing.md](./docs/contributing.md): コントリビュート規約（ブランチ/コミット/PR）

より詳細なガイドは各ドキュメントを参照してください。
