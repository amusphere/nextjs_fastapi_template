# テストガイド

本プロジェクトのテスト方針と実行方法をまとめます。

## Backend（pytest）

- テストランナー: `pytest`
- 実行: `uv run pytest -q`
- テスト配置: `backend/tests/` 配下（ファイル名は `test_*.py`）
- フィクスチャ: `backend/tests/fixtures/` に共通フィクスチャを配置
- カバレッジ収集: 現状は実施しません（CI でも未収集）

推奨プラクティス:
- ルータは FastAPI の TestClient で I/O を検証
- サービスはユニットテストでドメインロジックを検証
- リポジトリはテスト用 DB（SQLite など）で I/O を検証

## Frontend

現状、フロントエンドのテストランナーは未スキャフォールドです。追加する場合は以下を推奨します。

- ランナー: Jest + React Testing Library（カバレッジ収集は推奨しません）
- 配置: 各コンポーネント横、もしくは `__tests__/` 配下
- Lint: `npm run lint` で静的検査

例（導入方針）:
- 依存追加: `jest`, `@testing-library/react`, `@testing-library/jest-dom`, `ts-jest` など
- スクリプト: `"test": "jest"`, `"test:watch": "jest --watch"`

導入はプロジェクト要件に応じて検討してください。
