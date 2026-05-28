from typing import Optional

from sqlmodel import SQLModel, Field


class BookGenreLink(SQLModel, table=True):
    """Ассоциативная таблица для связи many-to-many между Book и Genre"""
    book_id: Optional[int] = Field(
        default=None, foreign_key="book.id", primary_key=True
    )
    genre_id: Optional[int] = Field(
        default=None, foreign_key="genre.id", primary_key=True
    )
    note: Optional[str] = Field(
        default=None,
        description="Характеристика связи, например 'основной жанр'"
    )
