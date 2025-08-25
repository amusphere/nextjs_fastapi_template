# Backend 開発ガイド（FastAPI）

## レイヤ構成

- Routers: API エンドポイント定義（入出力のスキーマを扱う）
- Models: Pydantic によるリクエスト/レスポンスモデル
- Services: ビジネスロジック（ドメイン処理）
- Repositories: DB アクセス（SQLModel 等による永続化）
- Utils: 共通関数

## エンドポイントの追加手順

1. `app/models` に入出力用の Pydantic モデルを追加（必要に応じて）。
2. `app/services` にビジネスロジックを実装。
3. `app/repositories` に必要な DB アクセス処理を追加/変更。
4. `app/routers` にルータを追加し、サービスを呼び出す。

## マイグレーション（Alembic）

スキーマ変更時:

```bash
# 変更の自動生成
docker compose run --rm backend alembic revision --autogenerate -m "add_feature_x"

# 内容確認後、適用
docker compose run --rm backend alembic upgrade head

# ローカル実行での適用（Docker を使わない場合）
uv run alembic upgrade head
```

ダウングレード例:

```bash
docker compose run --rm backend alembic downgrade -1
```

## ローカル開発サーバ

```bash
uv run fastapi dev --host 0.0.0.0 --port 8000
```

API ドキュメント: http://localhost:8000/docs

