cd /workspace/nextjs_fastapi_template/frontend
cp .env.sample .env
npm ci

curl -LsSf https://astral.sh/uv/install.sh | sh
cd /workspace/nextjs_fastapi_template/backend
cp .env.sample .env
uv sync
