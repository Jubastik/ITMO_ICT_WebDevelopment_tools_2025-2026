from __future__ import annotations
import os
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
if DB_URL and DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DB_URL)

class ScrapedPage(SQLModel, table=True):
    """Модель для хранения спарсенных данных."""
    id: int | None = Field(default=None, primary_key=True)
    url: str = Field()
    title: str = Field()

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
