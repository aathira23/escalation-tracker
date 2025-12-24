"""
Database Configuration
Sets up SQLAlchemy engine, session, and base model.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

# Determine if using SQLite (for development without Docker)
is_sqlite = settings.database_url.startswith('sqlite')

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True if not is_sqlite else False,
    **({"pool_size": 10, "max_overflow": 20} if not is_sqlite else {"connect_args": {"check_same_thread": False}})
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    Yields a session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
