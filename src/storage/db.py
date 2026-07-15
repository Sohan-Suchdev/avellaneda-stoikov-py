import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.storage.models import Base


DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "results.db"
DB_PATH = Path(os.environ.get("DMM_DB_PATH", DEFAULT_DB_PATH)).resolve()
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)


def create_tables():
    Base.metadata.create_all(bind=engine)
