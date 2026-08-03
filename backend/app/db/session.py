from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Railway PostgreSQL requires SSL; pg8000 accepts ssl via connect_args
_ssl_required = "railway" in settings.DATABASE_URL or settings.APP_ENV == "production"
_connect_args = {"ssl": True} if _ssl_required else {}

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
