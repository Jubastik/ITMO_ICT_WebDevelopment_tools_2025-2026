from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional

from app.database import get_session
from app.models.book import Book, BookDefault, BookUpdate, BookRead, BookReadWithGenres
from app.models.genre import Genre
from app.models.links import BookGenreLink
from app.models.user import User
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=List[BookRead])
def books_list(
    session: Session = Depends(get_session),
    available_only: bool = Query(False, description="Показать только доступные"),
    search: Optional[str] = Query(None, description="Поиск по названию или автору"),
) -> List[Book]:
    """Получение списка книг с возможностью фильтрации и поиска."""
    query = select(Book)
    if available_only:
        query = query.where(Book.is_available == True)  # noqa: E712
    if search:
        query = query.where(
            (Book.title.contains(search)) | (Book.author.contains(search))  # type: ignore
        )
    return session.exec(query).all()


@router.get("/{book_id}", response_model=BookReadWithGenres)
def book_get(book_id: int, session: Session = Depends(get_session)) -> Book:
    """Получение книги по id с вложенными жанрами."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return book


@router.post("/", response_model=BookRead, status_code=201)
def book_create(
    book: BookDefault,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Book:
    """Добавление книги в библиотеку текущего пользователя."""
    db_book = Book.model_validate(book)
    db_book.owner_id = current_user.id
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.patch("/{book_id}", response_model=BookRead)
def book_update(
    book_id: int,
    book_data: BookUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Book:
    """Обновление книги (только владелец)."""
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    if db_book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Вы не владелец этой книги")

    update_dict = book_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_book, key, value)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@router.delete("/{book_id}")
def book_delete(
    book_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Удаление книги (только владелец)."""
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    if db_book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Вы не владелец этой книги")
    session.delete(db_book)
    session.commit()
    return {"ok": True}


@router.post("/{book_id}/genres/{genre_id}")
def book_add_genre(
    book_id: int,
    genre_id: int,
    note: Optional[str] = Query(None, description="Примечание к связи (напр. 'основной жанр')"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Добавление жанра к книге (many-to-many)."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Вы не владелец этой книги")
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Жанр не найден")

    # Проверяем, не существует ли уже связь
    existing = session.exec(
        select(BookGenreLink).where(
            BookGenreLink.book_id == book_id,
            BookGenreLink.genre_id == genre_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Жанр уже добавлен к книге")

    link = BookGenreLink(book_id=book_id, genre_id=genre_id, note=note)
    session.add(link)
    session.commit()
    return {"ok": True, "message": f"Жанр '{genre.name}' добавлен к книге '{book.title}'"}


@router.delete("/{book_id}/genres/{genre_id}")
def book_remove_genre(
    book_id: int,
    genre_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Удаление жанра у книги."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Вы не владелец этой книги")

    link = session.exec(
        select(BookGenreLink).where(
            BookGenreLink.book_id == book_id,
            BookGenreLink.genre_id == genre_id,
        )
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Связь не найдена")

    session.delete(link)
    session.commit()
    return {"ok": True}
