# Contributor Guide

This repository contains both the frontend and backend. Each directory is independent, allowing for simultaneous development of both frontend and backend.

## Directory Structure

Refer to the `README.md` at the root for the basic directory structure. Generally, you will be modifying files within the `Backend/` and `Frontend/` directories, as outlined below.

### Backend

The backend is based on FastAPI and is structured in the following layers:

- `routers/`: Defines API routing.
- `models/`: Defines request/response schemas.
- `repositories/`: Handles data access.
- `services/`: Contains business logic.
- `utils/`: Utility functions.

## Frontend

The frontend is based on Next.js and is structured in the following layers:

- `app/api/`: Defines API routing.
- `app/(authed)/`: Defines routes that require authentication.
- `app/auth/`: Handles authentication-related routes.
- `components/components/commons`: Common components.
- `components/components/forms`: Form components.
- `components/components/ui`: shadcn/ui components (do not modify).
- `components/hooks/`: Custom hooks.
- `components/lib/`: shadcn/ui library functions (do not modify).
- `components/pages/`: Page components.
- `types/`: TypeScript type definitions.
- `utils/`: Utility functions.

## Lint and Format

### Backend

- Use `black` for code formatting.

### Frontend

- Run `npm run lint` to execute linting.

## Testing

### Backend

Start the server and test endpoints with the following command:

```bash
uv run fastapi dev --host 0.0.0.0 --port 8000
```

If necessary, run database migrations:

```bash
uv run alembic upgrade head
```

### Frontend

Start the server and test the UI with the following command. Make sure the backend server is also running.

```bash
npm run dev
```

Also, verify that the build passes with the following command:

```bash
npm run build
```

## UI
- Use shadcn/ui for UI components.
- Do not modify the files in `components/components/ui/` or `components/lib/`.
- Use the components in `components/components/commons/` and `components/components/forms/` for custom components.
- Use the components in `components/components/pages/` for page components.

## Pull Requests
- Branch names must be in English and include the feature name.
- Use hyphens (-) as separators between words.

## etc.
- If instructions are given in Japanese, respond in Japanese.
