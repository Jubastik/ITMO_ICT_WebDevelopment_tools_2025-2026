import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import select, Session
from typing import List
from typing_extensions import TypedDict

from connection import init_db, get_session
from models import (
    User, UserDefault, UserWithBooks,
    Book, BookDefault, BookWithGenres,
    Genre, GenreDefault, GenreRead,
    BookGenreLink,
)

app = FastAPI(title="Bookcrossing Practice 1.3")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def hello() -> str:
    return "Привет! Это приложение для буккросинга (Practice 1.3 — Alembic + .env)."


@app.get("/users", response_model=List[UserDefault])
def users_list(session: Session = Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()


@app.get("/users/{user_id}", response_model=UserWithBooks)
def user_get(user_id: int, session: Session = Depends(get_session)) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users")
def user_create(
    user: UserDefault, session: Session = Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": User}):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"status": 200, "data": db_user}


@app.patch("/users/{user_id}", response_model=UserDefault)
def user_update(
    user_id: int, user: UserDefault, session: Session = Depends(get_session)
) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def user_delete(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


@app.get("/books", response_model=List[BookDefault])
def books_list(session: Session = Depends(get_session)) -> List[Book]:
    return session.exec(select(Book)).all()


@app.get("/books/{book_id}", response_model=BookWithGenres)
def book_get(book_id: int, session: Session = Depends(get_session)) -> Book:
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books")
def book_create(
    book: BookDefault, session: Session = Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Book}):
    db_book = Book.model_validate(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return {"status": 200, "data": db_book}


@app.patch("/books/{book_id}", response_model=BookDefault)
def book_update(
    book_id: int, book: BookDefault, session: Session = Depends(get_session)
) -> Book:
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    book_data = book.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.delete("/books/{book_id}")
def book_delete(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return {"ok": True}


@app.get("/genres", response_model=List[GenreRead])
def genres_list(session: Session = Depends(get_session)) -> List[Genre]:
    return session.exec(select(Genre)).all()


@app.get("/genres/{genre_id}", response_model=GenreRead)
def genre_get(genre_id: int, session: Session = Depends(get_session)) -> Genre:
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@app.post("/genres")
def genre_create(
    genre: GenreDefault, session: Session = Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Genre}):
    db_genre = Genre.model_validate(genre)
    session.add(db_genre)
    session.commit()
    session.refresh(db_genre)
    return {"status": 200, "data": db_genre}


@app.patch("/genres/{genre_id}", response_model=GenreRead)
def genre_update(
    genre_id: int, genre: GenreDefault, session: Session = Depends(get_session)
) -> Genre:
    db_genre = session.get(Genre, genre_id)
    if not db_genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    genre_data = genre.model_dump(exclude_unset=True)
    for key, value in genre_data.items():
        setattr(db_genre, key, value)
    session.add(db_genre)
    session.commit()
    session.refresh(db_genre)
    return db_genre


@app.delete("/genres/{genre_id}")
def genre_delete(genre_id: int, session: Session = Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    session.delete(genre)
    session.commit()
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
