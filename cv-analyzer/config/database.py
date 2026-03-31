from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=True  # tampilkan query SQL di terminal (debug mode)
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Dependency untuk FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()