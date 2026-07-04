import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

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

# Lambda freezes containers between invocations — pooled connections go stale.
# NullPool creates a fresh connection per request, avoiding SSL/timeout errors.
IS_LAMBDA = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))

if IS_LAMBDA:
    engine = create_engine(
        POSTGRES_URL,
        echo=False,
        connect_args=connect_args,
        poolclass=NullPool,
    )
else:
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
