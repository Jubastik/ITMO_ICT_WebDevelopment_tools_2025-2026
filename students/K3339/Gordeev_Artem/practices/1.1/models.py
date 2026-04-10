from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class BookCondition(str, Enum):
    """Перечисление состояний книги."""
    new = "new"
    good = "good"
    fair = "fair"
    poor = "poor"


class Genre(BaseModel):
    """Модель жанра книги."""
    id: int
    name: str
    description: str


class GenreDefault(BaseModel):
    """Модель жанра для создания (без id)."""
    name: str
    description: str


class Book(BaseModel):
    """Модель книги с вложенными жанрами."""
    id: int
    title: str
    author: str
    description: str
    year: int
    condition: BookCondition
    is_available: bool = True
    owner_id: int
    genres: Optional[List[Genre]] = []


class BookDefault(BaseModel):
    """Модель книги для создания"""
    title: str
    author: str
    description: str
    year: int
    condition: BookCondition
    is_available: bool = True
    owner_id: int


class User(BaseModel):
    """Модель пользователя с вложенными книгами."""
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    books: Optional[List[Book]] = []


class UserDefault(BaseModel):
    """Модель пользователя для создания"""
    username: str
    email: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
