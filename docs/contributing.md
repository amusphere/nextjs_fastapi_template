# Contributing ガイド

このプロジェクトへの貢献ルールをまとめます。詳細の運用指針は `AGENTS.md` も参照してください。

## ブランチ運用

- 命名: 英語・ハイフン区切り・プレフィックス推奨
  - 例: `feat-user-login`, `fix-api-timeout`, `chore-deps-update`

## コミットメッセージ

- 原則: 命令形・短く具体的に
- 任意の Conventional Commits を推奨
  - 例: `feat: add user login flow`, `fix: handle 504 on fetch`, `chore: bump dependencies`

## プルリクエスト

- 目的と変更点の要約、動作確認手順、UI 変更ならスクリーンショット/動画
- スキーマや環境変数の変更があれば明示
- 影響範囲（フロント/バックエンド/DB）を記載

## コーディング規約（抜粋）

- Python: 4 スペース、型ヒント、Pydantic モデルは `app/models`、ビジネスロジックは `app/services`
- TypeScript/React: TS 使用、コンポーネントは `PascalCase`、フックは `useX` 命名、App Router 準拠
- フォーマット: Backend は Black、Frontend は ESLint

## テスト

- Backend: `uv run pytest -q`、テストは `backend/tests/` に配置
- Frontend: 必要に応じて Jest/RTL を導入。最低限 `npm run lint` を通す

## ドキュメント

- ルート `README.md`: 概要とセットアップ
- 詳細は `docs/` 配下に追加（本ファイルを含む）
- 言語ポリシー: 既定は日本語。識別子は英語、コメント/Docstring は日本語可

