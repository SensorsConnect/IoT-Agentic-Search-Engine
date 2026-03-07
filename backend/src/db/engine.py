import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_URL = os.environ.get("POSTGRES_URL", "")

if not POSTGRES_URL:
    raise RuntimeError("POSTGRES_URL environment variable is required")

connect_args = {}
if POSTGRES_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(POSTGRES_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
