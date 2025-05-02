# NextJS FastAPI Template
This is a template for a web application using Next.js for the frontend and FastAPI for the backend. It is designed to be a starting point for building modern web applications with a focus on performance, scalability, and developer experience.

## Features

### Frontend
- [Next.js](https://nextjs.org/) for server-side rendering and static site generation
- TypeScript support
- [Tailwindcss](https://tailwindcss.com/) for styling
- [shadcn/ui](https://ui.shadcn.com/) - a set of accessible and customizable UI components

### Backend
- [FastAPI](https://fastapi.tiangolo.com/) for building APIs
- [SQLModel](https://sqlmodel.tiangolo.com/) for ORM
- [Alembic](https://alembic.sqlalchemy.org/) for database migrations

### Authentication
- [Clerk](https://clerk.dev/) for user authentication and management

### Deployment
- Docker for containerization
- Docker Compose for local development


## Getting Started

### Environment Variables
Create a `.env` file in both the `frontend` and `backend` directories. Copy the contents of `.env.example` to `.env` and fill in the required values.

- Frontend
  - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
  - CLERK_SECRET_KEY
- Backend
  - CLERK_SECRET_KEY

### Run on Docker
Command to run the application using Docker Compose:

```bash
# Build
docker compose build

# Run
docker compose up
```

### Database Migrations
To run database migrations, use the following command:

```bash
docker compose exec backend alembic upgrade head
```

### Checking in Browser
- Web: [http://localhost:3000](http://localhost:3000)
- API: [http://localhost:8000/docs](http://localhost:8000/docs)
