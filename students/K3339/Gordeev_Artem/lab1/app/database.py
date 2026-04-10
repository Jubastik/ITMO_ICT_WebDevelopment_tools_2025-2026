from sqlmodel import SQLModel, Session, create_engine

from app.config import settings

engine = create_engine(settings.DB_URL, echo=True)


def init_db():
    """Создаёт все таблицы, описанные в моделях SQLModel."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Генератор сессий для Depends."""
    with Session(engine) as session:
        yield session
