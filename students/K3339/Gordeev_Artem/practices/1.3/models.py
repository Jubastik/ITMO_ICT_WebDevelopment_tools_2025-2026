from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class BookCondition(str, Enum):
    """Состояние книги."""
    new = "new"
    good = "good"
    fair = "fair"
    poor = "poor"


class BookGenreLink(SQLModel, table=True):
    """Связь книги и жанра (many-to-many) с дополнительным полем note."""
    book_id: Optional[int] = Field(
        default=None, foreign_key="book.id", primary_key=True
    )
    genre_id: Optional[int] = Field(
        default=None, foreign_key="genre.id", primary_key=True
    )
    note: Optional[str] = None  # характеризующее связь поле


class GenreDefault(SQLModel):
    """Базовая модель жанра."""
    name: str
    description: str


class Genre(GenreDefault, table=True):
    """Таблица жанров."""
    id: int = Field(default=None, primary_key=True)
    books: Optional[List["Book"]] = Relationship(
        back_populates="genres", link_model=BookGenreLink
    )


class BookDefault(SQLModel):
    """Базовая модель книги для создания."""
    title: str
    author: str
    description: str
    year: int
    condition: BookCondition
    is_available: bool = True
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")


class Book(BookDefault, table=True):
    """Таблица книг."""
    id: int = Field(default=None, primary_key=True)
    owner: Optional["User"] = Relationship(back_populates="books")
    genres: Optional[List[Genre]] = Relationship(
        back_populates="books", link_model=BookGenreLink
    )


class UserDefault(SQLModel):
    """Базовая модель пользователя."""
    username: str
    email: str
    first_name: str
    last_name: str
    bio: Optional[str] = None


class User(UserDefault, table=True):
    """Таблица пользователей."""
    id: int = Field(default=None, primary_key=True)
    books: Optional[List[Book]] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete"},
    )


class GenreRead(GenreDefault):
    """Жанр с id (для чтения)."""
    id: int


class BookWithGenres(BookDefault):
    """Книга с вложенными жанрами."""
    id: int
    genres: Optional[List[GenreRead]] = []


class UserWithBooks(UserDefault):
    """Пользователь с вложенными книгами."""
    id: int
    books: Optional[List[BookWithGenres]] = []
