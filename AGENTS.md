# Repository Guidelines

Concise, practical rules for contributing to this monorepo. Keep changes scoped to either `backend/` (FastAPI) or `frontend/` (Next.js) unless the feature requires cross-cutting updates.

## 言語ポリシー / Language Policy

- 既定の対応言語は日本語です。特段の指定がない限り、エージェントの応答、PR/Issue の説明、README/ドキュメントは日本語で記述してください。
- コードの識別子（ファイル名・変数名・関数名・クラス名）は英語を維持します。コメントや Docstring は日本語で構いません。
- 文体は簡潔・具体的・丁寧を心がけ、不要な冗長表現は避けてください。

## ドキュメント構成 / Documentation

- ルートの `README.md`: 概要と環境構築のみ（簡潔）
- 詳細は `docs/` 配下に追加・更新します。
  - `docs/architecture.md`: 技術スタック・ディレクトリ構成
  - `docs/backend.md`: API 開発フロー、マイグレーション
  - `docs/frontend.md`: フロントエンド構成とページ作成
  - `docs/docker.md`: Docker 実行/運用
  - `docs/environment.md`: 環境変数
  - `docs/testing.md`: テスト方針
  - `docs/contributing.md`: コントリビュート規約（ブランチ/コミット/PR）

## Project Structure & Module Organization

- Root: `backend/`, `frontend/`, `docker-compose.yml`, `README.md`.
- Backend (`backend/`): FastAPI app. Key dirs: `app/routers`, `app/models`, `app/repositories`, `app/services`, `app/utils`, `app/migrations`; tests in `backend/tests/`. Entry: `backend/main.py`.
- Frontend (`frontend/`): Next.js (App Router). Key dirs: `app/`, `components/components/{commons,forms,ui}`, `components/hooks`, `components/lib`, `components/pages`, `types/`, `utils/`.
- Do not modify `components/components/ui/` or `components/lib/` (generated shadcn/ui).

## Build, Test, and Development Commands

- Backend — dev server: `uv run fastapi dev --host 0.0.0.0 --port 8000`
- Backend — DB migrate: `uv run alembic upgrade head`
- Backend — tests: `uv run pytest -q`
- Frontend — dev: `npm run dev` (from `frontend/`)
- Frontend — build: `npm run build`; start: `npm run start`
- Frontend — lint: `npm run lint`

## Coding Style & Naming Conventions

- Python: 4-space indent, type hints, Pydantic models in `app/models`. Keep routers thin; put business logic in `app/services`. Files: `snake_case.py`; functions/vars: `snake_case`; classes: `PascalCase`.
- TypeScript/React: Use TS. Components: `PascalCase` files (e.g., `UserCard.tsx`); hooks: `useX` in `components/hooks`. Route segment files follow Next.js conventions. Prefer named exports.
- Formatting: Backend uses Black; run locally with `black backend`. Frontend uses ESLint (`npm run lint`).

## Testing Guidelines

- Backend: Pytest with fixtures in `backend/tests/fixtures`. Name tests `test_*.py`. Run `uv run pytest -q`. Aim to cover routers, services, and auth flows.
- Frontend: No test runner scaffolded. If adding tests, prefer React Testing Library and keep tests beside components or under `__tests__/`.

## Commit & Pull Request Guidelines

- Branches: English, hyphen-separated, include feature (e.g., `feat-user-login`).
- Commits: Imperative mood; use conventional types where helpful (e.g., `feat:`, `fix:`, `chore:`).
- PRs: Clear description, linked issues, steps to test, and screenshots/GIFs for UI changes. Note any schema or ENV changes.

## Security & Configuration

- Environment: copy `.env.sample` to `.env` in both `backend/` and `frontend/`. Do not commit secrets. Update samples when adding variables.
- CORS/URLs: keep allowed origins and API URLs configurable via ENV.
