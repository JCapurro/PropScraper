import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Always create Base (needed for models even if using MongoDB)
Base = declarative_base()

# Only use SQLAlchemy for SQLite
if "mongodb" not in settings.DATABASE_URL:
    DATABASE_URL = settings.DATABASE_URL
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # For MongoDB, we'll use PyMongo directly (see mongo_db.py)
    engine = None
    SessionLocal = None

def init_db():
    """Initialize database tables"""
    if engine and Base:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

def get_db():
    if SessionLocal is None:
        raise RuntimeError("SQLite database not configured. MongoDB is being used.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
