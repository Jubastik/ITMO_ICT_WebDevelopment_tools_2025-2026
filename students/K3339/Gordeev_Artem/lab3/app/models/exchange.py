from enum import Enum
from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship


class ExchangeStatus(str, Enum):
    """Статус запроса на обмен."""
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class ExchangeRequestCreate(SQLModel):
    """Модель для создания запроса на обмен."""
    receiver_id: int
    sender_book_id: int
    receiver_book_id: int
    message: Optional[str] = None


class ExchangeRequestUpdate(SQLModel):
    """Модель для обновления статуса запроса."""
    status: ExchangeStatus


class ExchangeRequest(SQLModel, table=True):
    """Таблица запросов на обмен книгами."""
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    sender_book_id: int = Field(foreign_key="book.id")
    receiver_book_id: int = Field(foreign_key="book.id")
    status: ExchangeStatus = Field(default=ExchangeStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = None

    sender: Optional["User"] = Relationship(
        back_populates="sent_requests",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_id]"},
    )
    receiver: Optional["User"] = Relationship(
        back_populates="received_requests",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_id]"},
    )
    sender_book: Optional["Book"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_book_id]"},
    )
    receiver_book: Optional["Book"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_book_id]"},
    )

    # one-to-many: ExchangeRequest > ExchangeHistory
    history: Optional["ExchangeHistory"] = Relationship(back_populates="request")



class ExchangeHistory(SQLModel, table=True):
    """Таблица истории обменов (фиксирует состоявшийся обмен)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="exchangerequest.id")
    exchanged_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

    request: Optional[ExchangeRequest] = Relationship(back_populates="history")


class ExchangeRequestRead(SQLModel):
    """Запрос на обмен для ответа."""
    id: int
    sender_id: int
    receiver_id: int
    sender_book_id: int
    receiver_book_id: int
    status: ExchangeStatus
    created_at: datetime
    message: Optional[str] = None


class ExchangeHistoryRead(SQLModel):
    """История обмена для ответа."""
    id: int
    request_id: int
    exchanged_at: datetime
    notes: Optional[str] = None


from app.models.user import User  # noqa: E402,F401
from app.models.book import Book  # noqa: E402,F401
