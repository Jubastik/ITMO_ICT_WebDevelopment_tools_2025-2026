from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from app.database import get_session
from app.models.exchange import (
    ExchangeRequest, ExchangeRequestCreate, ExchangeRequestUpdate,
    ExchangeRequestRead, ExchangeStatus,
    ExchangeHistory, ExchangeHistoryRead,
)
from app.models.book import Book
from app.models.user import User
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/exchanges", tags=["Exchanges"])


@router.get("/requests", response_model=List[ExchangeRequestRead])
def list_my_requests(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[ExchangeRequest]:
    """Получение всех запросов на обмен, связанных с текущим пользователем
    (отправленных и полученных)."""
    return session.exec(
        select(ExchangeRequest).where(
            (ExchangeRequest.sender_id == current_user.id)
            | (ExchangeRequest.receiver_id == current_user.id)
        )
    ).all()


@router.get("/requests/{request_id}", response_model=ExchangeRequestRead)
def get_request(
    request_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ExchangeRequest:
    """Получение запроса на обмен по id."""
    exchange = session.get(ExchangeRequest, request_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Запрос не найден")
    if exchange.sender_id != current_user.id and exchange.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому запросу")
    return exchange


@router.post("/requests", response_model=ExchangeRequestRead, status_code=201)
def create_request(
    data: ExchangeRequestCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ExchangeRequest:
    """Создание запроса на обмен книгами.

    Отправитель предлагает свою книгу (sender_book_id) в обмен на книгу
    получателя (receiver_book_id).
    """
    # Проверяем, что книга отправителя принадлежит ему
    sender_book = session.get(Book, data.sender_book_id)
    if not sender_book or sender_book.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Указанная книга не принадлежит вам")
    if not sender_book.is_available:
        raise HTTPException(status_code=400, detail="Ваша книга недоступна для обмена")

    # Проверяем, что книга получателя существует
    receiver_book = session.get(Book, data.receiver_book_id)
    if not receiver_book or receiver_book.owner_id != data.receiver_id:
        raise HTTPException(status_code=400, detail="Книга получателя не найдена")
    if not receiver_book.is_available:
        raise HTTPException(status_code=400, detail="Книга получателя недоступна")

    # Нельзя обмениваться с самим собой
    if current_user.id == data.receiver_id:
        raise HTTPException(status_code=400, detail="Нельзя отправить запрос самому себе")

    exchange = ExchangeRequest(
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        sender_book_id=data.sender_book_id,
        receiver_book_id=data.receiver_book_id,
        message=data.message,
    )
    session.add(exchange)
    session.commit()
    session.refresh(exchange)
    return exchange


@router.patch("/requests/{request_id}", response_model=ExchangeRequestRead)
def update_request_status(
    request_id: int,
    data: ExchangeRequestUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ExchangeRequest:
    """Подтверждение или отклонение запроса на обмен (только получатель)."""
    exchange = session.get(ExchangeRequest, request_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Запрос не найден")

    # Только получатель может менять статус
    if exchange.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только получатель может менять статус запроса")

    if exchange.status != ExchangeStatus.pending:
        raise HTTPException(status_code=400, detail="Запрос уже обработан")

    exchange.status = data.status
    session.add(exchange)
    session.commit()
    session.refresh(exchange)

    # Если запрос принят — создаём запись в истории и меняем доступность книг
    if data.status == ExchangeStatus.accepted:
        history = ExchangeHistory(
            request_id=exchange.id,
            exchanged_at=datetime.utcnow(),
            notes=f"Обмен: '{exchange.sender_book.title}' ↔ '{exchange.receiver_book.title}'",
        )
        session.add(history)

        # Помечаем книги как недоступные
        sender_book = session.get(Book, exchange.sender_book_id)
        receiver_book = session.get(Book, exchange.receiver_book_id)
        if sender_book:
            sender_book.is_available = False
        if receiver_book:
            receiver_book.is_available = False
        session.commit()

    return exchange


@router.delete("/requests/{request_id}")
def delete_request(
    request_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Удаление запроса на обмен (только отправитель, только pending)."""
    exchange = session.get(ExchangeRequest, request_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Запрос не найден")
    if exchange.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только отправитель может удалить запрос")
    if exchange.status != ExchangeStatus.pending:
        raise HTTPException(status_code=400, detail="Нельзя удалить обработанный запрос")
    session.delete(exchange)
    session.commit()
    return {"ok": True}


@router.get("/history", response_model=List[ExchangeHistoryRead])
def list_history(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[ExchangeHistory]:
    """Получение истории обменов текущего пользователя."""
    return session.exec(
        select(ExchangeHistory)
        .join(ExchangeRequest)
        .where(
            (ExchangeRequest.sender_id == current_user.id)
            | (ExchangeRequest.receiver_id == current_user.id)
        )
    ).all()
