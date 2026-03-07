import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_URL = os.environ.get("POSTGRES_URL", "")

if not POSTGRES_URL:
    raise RuntimeError("POSTGRES_URL environment variable is required")

connect_args = {}
if POSTGRES_URL.startswith(("postgresql://", "postgres://")):
    connect_args = {
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
elif POSTGRES_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    POSTGRES_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=280,
    pool_size=5,
    max_overflow=10,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
