from typing import Optional, List
from datetime import date

from sqlmodel import SQLModel, Field, Relationship


class UserCreate(SQLModel):
    """Модель для регистрации пользователя."""
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    birth_date: Optional[date] = None


class UserUpdate(SQLModel):
    """Модель для обновления профиля пользователя."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    birth_date: Optional[date] = None


class UserPasswordChange(SQLModel):
    """Модель для смены пароля."""
    old_password: str
    new_password: str


class User(SQLModel, table=True):
    """Таблица пользователей."""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    birth_date: Optional[date] = None

    # one-to-many: User > Book
    books: List["Book"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    # one-to-many: User > ExchangeRequest (как отправитель)
    sent_requests: List["ExchangeRequest"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[ExchangeRequest.sender_id]",
        },
    )

    # one-to-many: User > ExchangeRequest (как получатель)
    received_requests: List["ExchangeRequest"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[ExchangeRequest.receiver_id]",
        },
    )


class UserRead(SQLModel):
    """Пользователь для ответа (без пароля)."""
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    birth_date: Optional[date] = None


class UserReadWithBooks(UserRead):
    """Пользователь с вложенными книгами."""
    books: List["BookRead"] = []


from app.models.book import BookRead  # noqa: E402

UserReadWithBooks.model_rebuild()
