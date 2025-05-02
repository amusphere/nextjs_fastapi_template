# NextJS FastAPI Template
This is a template for a web application using Next.js for the frontend and FastAPI for the backend. It is designed to be a starting point for building modern web applications with a focus on performance, scalability, and developer experience.

## Features

### Frontend
- [Next.js](https://nextjs.org/) for server-side rendering and static site generation. Uses the App Router.
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

### Optional: Rename App Name
If you want to rename the app name, change env variables in the frontend `.env` file.

```env
APP_NAME="Your App Name"
```

## Directory Structure

Backend:
```
Backend/
├── app/                   # Application source code
│   ├── migrations/        # Database migrations
│   ├── models/            # Data model definitions (Request/Response schemas by Pydantic)
│   ├── repositories/      # Database access layer
│   ├── routers/           # API route definitions
│   │   └── routers.py     # Set routing table
│   ├── services/          # Business logic layer
│   ├── utils/             # General utility functions
│   ├── database.py        # Database connection and session management
│   └── schema.py          # Database schema definitions by SQLModel
├── .env.sample            # Sample environment variables
├── alembic.ini            # Alembic configuration file
├── Dockerfile             # Dockerfile for backend
├── main.py                # Entry point for FastAPI application
└── pyproject.toml         # Environment dependencies by uv
```

Frontend:
```
Frontend/
├── app/                   # Next.js application source code
│   ├── (authed)/          # Authed routes
│   │   └── layout.tsx     # Layout component for authed routes
│   ├── api/               # API route definitions
│   ├── auth/              # Authentication related routes
│   ├── global.css         # Global CSS styles
│   ├── layout.tsx         # Main layout component
│   └── page.tsx           # Main entry point for Next.js application
├── components/            # Reusable components
│   ├── components/
│   │   ├── commons/       # Common components
│   │   ├── forms/         # Form components
│   │   └── ui/            # shadcn/ui components (Do not modify)
│   ├── hooks/             # Custom hooks (Create by shadcn/ui)
│   ├── lib/               # Library functions (Create by shadcn/ui)
│   └── pages/             # Page components
├── types/                 # TypeScript types
├── utils/                 # Utility functions
├── .env.sample            # Sample environment variables
├── Dockerfile             # Dockerfile for frontend
├── package.json           # Node.js dependencies
└── next.config.js         # Next.js configuration file
```

## Development Flow

### Create endpoint (Backend)
1. Create a new file in the `routers/` directory for the new endpoint.
2. Define the endpoint in the `routers/routers.py` file.

#### Layer Structure
- **Routers**: API route definitions. Define the API routes here.
- **Models**: Define the request and response schemas using Pydantic.
- **Services**: Business logic layer. Define the business logic here. Calling from the router layer.
- **Repositories**: Database access layer. Define the database access methods here. Calling from the service layer or router layer.
- **Utils**: General utility functions. Define the utility functions here.

#### Database Migrations
1. Add a new table or modify an existing table in the `schema.py` file.
2. Create a new migration file using Alembic:
   ```bash
   docker compose exec backend alembic revision --autogenerate -m "migration_name"
   ```
3. Check the generated migration file in the `migrations/versions/` directory and make any necessary adjustments.
4. Apply the migration:
   ```bash
   docker compose exec backend alembic upgrade head
   ```
5. If you want to downgrade the migration, use the following command:
   ```bash
   docker compose exec backend alembic downgrade -1
   ```

### Create new page (Frontend)
1. Create a new file in the `app/` directory for the new page.
  - If new page is authed, create in the `(authed)/` directory.

#### Layer Structure
- **app/**: Next.js application source code. Define the pages and components here.
- **components/**: Reusable components. Define the reusable components here.
- **components/hooks/**: Custom hooks. Define the custom hooks here.
- **components/lib/**: Library functions. Define the library functions here.
- **components/pages/**: Page components. Define the page components here.
- **types/**: TypeScript types. Define the TypeScript types here.
- **utils/**: Utility functions. Define the utility functions here.
