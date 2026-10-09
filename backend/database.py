"""Database Configuration & Engine Module.

Manages SQLite database connections, SQLAlchemy session creation,
and database initialization for RansomGuard Storage AI.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database file path configured relative to the database directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "ransomguard.db")

# Ensure database directory exists
os.makedirs(DB_DIR, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency iterator providing a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
