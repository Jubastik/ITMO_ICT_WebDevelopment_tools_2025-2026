from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from app.models.links import BookGenreLink


class GenreDefault(SQLModel):
    """Базовая модель жанра для создания."""
    name: str
    description: Optional[str] = None


class Genre(GenreDefault, table=True):
    """Таблица жанров книг."""
    id: Optional[int] = Field(default=None, primary_key=True)

    books: List["Book"] = Relationship(
        back_populates="genres", link_model=BookGenreLink
    )


class GenreRead(GenreDefault):
    """Жанр для ответа (с id)."""
    id: int

from app.models.book import Book  # noqa: E402,F401
