from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from app.models.links import BookGenreLink


class BookCondition(str, Enum):
    """Состояние книги."""
    new = "new"
    good = "good"
    fair = "fair"
    poor = "poor"


class BookDefault(SQLModel):
    """Базовая модель книги для создания."""
    title: str
    author: str
    description: Optional[str] = None
    year: Optional[int] = None
    condition: BookCondition = BookCondition.good
    is_available: bool = True
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")


class BookUpdate(SQLModel):
    """Модель для обновления книги."""
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    condition: Optional[BookCondition] = None
    is_available: Optional[bool] = None


class Book(BookDefault, table=True):
    """Таблица книг."""
    id: Optional[int] = Field(default=None, primary_key=True)

    # one-to-many: User > Book
    owner: Optional["User"] = Relationship(back_populates="books")

    # many-to-many: Book <> Genre
    genres: List["Genre"] = Relationship(
        back_populates="books", link_model=BookGenreLink
    )


class BookRead(SQLModel):
    """Книга для ответа (без вложенных связей)."""
    id: int
    title: str
    author: str
    description: Optional[str] = None
    year: Optional[int] = None
    condition: BookCondition
    is_available: bool
    owner_id: Optional[int] = None


class BookReadWithGenres(BookRead):
    """Книга с вложенными жанрами."""
    genres: List["GenreRead"] = []


from app.models.user import User  # noqa: E402,F401
from app.models.genre import Genre, GenreRead  # noqa: E402,F401

BookReadWithGenres.model_rebuild()
