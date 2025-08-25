# Docker 運用

## 起動/停止

```bash
docker compose build
docker compose up
# 停止
# Ctrl+C で停止、もしくは別ターミナルで
docker compose down
```

## マイグレーション

```bash
docker compose run --rm backend alembic upgrade head
```

## 動作確認

- Web: http://localhost:3000
- API: http://localhost:8000/docs

