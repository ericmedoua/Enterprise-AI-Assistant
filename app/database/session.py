from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

from sqlalchemy.orm import Session


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
