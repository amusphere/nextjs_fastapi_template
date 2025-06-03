from os import getenv

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

load_dotenv()


def get_database_url():
    """Get the database URL from environment variables."""
    DATABASE_URL = getenv("DATABASE_URL")
    return DATABASE_URL


def get_engine():
    """Get the SQLModel engine."""
    return create_engine(get_database_url(), future=True)


def get_session():
    """Get a SQLModel session."""
    engine = get_engine()
    with Session(engine) as session:
        yield session
