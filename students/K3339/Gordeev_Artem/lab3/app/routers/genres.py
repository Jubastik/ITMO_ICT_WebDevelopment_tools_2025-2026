from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models.genre import Genre, GenreDefault, GenreRead

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get("/", response_model=List[GenreRead])
def genres_list(session: Session = Depends(get_session)) -> List[Genre]:
    """Получение списка всех жанров."""
    return session.exec(select(Genre)).all()


@router.get("/{genre_id}", response_model=GenreRead)
def genre_get(genre_id: int, session: Session = Depends(get_session)) -> Genre:
    """Получение жанра по id."""
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Жанр не найден")
    return genre


@router.post("/", response_model=GenreRead, status_code=201)
def genre_create(
    genre: GenreDefault, session: Session = Depends(get_session)
) -> Genre:
    """Создание нового жанра."""
    db_genre = Genre.model_validate(genre)
    session.add(db_genre)
    session.commit()
    session.refresh(db_genre)
    return db_genre


@router.patch("/{genre_id}", response_model=GenreRead)
def genre_update(
    genre_id: int,
    genre_data: GenreDefault,
    session: Session = Depends(get_session),
) -> Genre:
    """Обновление жанра."""
    db_genre = session.get(Genre, genre_id)
    if not db_genre:
        raise HTTPException(status_code=404, detail="Жанр не найден")
    update_dict = genre_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_genre, key, value)
    session.add(db_genre)
    session.commit()
    session.refresh(db_genre)
    return db_genre


@router.delete("/{genre_id}")
def genre_delete(genre_id: int, session: Session = Depends(get_session)) -> dict:
    """Удаление жанра."""
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Жанр не найден")
    session.delete(genre)
    session.commit()
    return {"ok": True}
