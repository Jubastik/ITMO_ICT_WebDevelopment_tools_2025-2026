import uvicorn
from fastapi import FastAPI
from typing import List
from typing_extensions import TypedDict

from models import (
    User, UserDefault,
    Book, BookDefault,
    Genre, GenreDefault,
    BookCondition,
)

app = FastAPI(title="Bookcrossing Practice 1.1")

temp_users = [
    {
        "id": 1,
        "username": "ivan",
        "email": "ivan@mail.ru",
        "first_name": "Иван",
        "last_name": "Петров",
        "bio": "Люблю классику",
        "books": [],
    },
    {
        "id": 2,
        "username": "maria",
        "email": "maria@mail.ru",
        "first_name": "Мария",
        "last_name": "Сидорова",
        "bio": "Читаю фантастику",
        "books": [],
    },
]

temp_genres = [
    {"id": 1, "name": "Фантастика", "description": "Научная фантастика и фэнтези"},
    {"id": 2, "name": "Классика", "description": "Классическая литература"},
    {"id": 3, "name": "Детектив", "description": "Детективные романы"},
]

temp_books = [
    {
        "id": 1,
        "title": "Мастер и Маргарита",
        "author": "Михаил Булгаков",
        "description": "Роман о визите дьявола в Москву",
        "year": 1967,
        "condition": "good",
        "is_available": True,
        "owner_id": 1,
        "genres": [temp_genres[1]],
    },
    {
        "id": 2,
        "title": "Дюна",
        "author": "Фрэнк Герберт",
        "description": "Эпическая сага о пустынной планете",
        "year": 1965,
        "condition": "new",
        "is_available": True,
        "owner_id": 2,
        "genres": [temp_genres[0]],
    },
]



@app.get("/")
def hello() -> str:
    return "Привет! Это приложение для буккросинга."


@app.get("/users", response_model=List[User])
def users_list() -> List[User]:
    return temp_users


@app.get("/users/{user_id}", response_model=User)
def user_get(user_id: int) -> User:
    for user in temp_users:
        if user.get("id") == user_id:
            return user
    return {"error": "User not found"}


@app.post("/users")
def user_create(user: UserDefault) -> TypedDict("Response", {"status": int, "data": User}):
    new_id = max((u["id"] for u in temp_users), default=0) + 1
    user_dict = user.model_dump()
    user_dict["id"] = new_id
    user_dict["books"] = []
    temp_users.append(user_dict)
    return {"status": 200, "data": user_dict}


@app.put("/users/{user_id}")
def user_update(user_id: int, user: UserDefault) -> List[User]:
    for i, u in enumerate(temp_users):
        if u.get("id") == user_id:
            updated = user.model_dump()
            updated["id"] = user_id
            updated["books"] = u.get("books", [])
            temp_users[i] = updated
    return temp_users


@app.delete("/users/{user_id}")
def user_delete(user_id: int) -> dict:
    for i, u in enumerate(temp_users):
        if u.get("id") == user_id:
            temp_users.pop(i)
            break
    return {"status": 201, "message": "deleted"}



@app.get("/books", response_model=List[Book])
def books_list() -> List[Book]:
    return temp_books


@app.get("/books/{book_id}", response_model=Book)
def book_get(book_id: int) -> Book:
    for book in temp_books:
        if book.get("id") == book_id:
            return book
    return {"error": "Book not found"}


@app.post("/books")
def book_create(book: BookDefault) -> TypedDict("Response", {"status": int, "data": Book}):
    new_id = max((b["id"] for b in temp_books), default=0) + 1
    book_dict = book.model_dump()
    book_dict["id"] = new_id
    book_dict["genres"] = []
    temp_books.append(book_dict)
    return {"status": 200, "data": book_dict}


@app.put("/books/{book_id}")
def book_update(book_id: int, book: BookDefault) -> List[Book]:
    for i, b in enumerate(temp_books):
        if b.get("id") == book_id:
            updated = book.model_dump()
            updated["id"] = book_id
            updated["genres"] = b.get("genres", [])
            temp_books[i] = updated
    return temp_books


@app.delete("/books/{book_id}")
def book_delete(book_id: int) -> dict:
    for i, b in enumerate(temp_books):
        if b.get("id") == book_id:
            temp_books.pop(i)
            break
    return {"status": 201, "message": "deleted"}



@app.get("/genres", response_model=List[Genre])
def genres_list() -> List[Genre]:
    return temp_genres


@app.get("/genres/{genre_id}", response_model=Genre)
def genre_get(genre_id: int) -> Genre:
    for genre in temp_genres:
        if genre.get("id") == genre_id:
            return genre
    return {"error": "Genre not found"}


@app.post("/genres")
def genre_create(genre: GenreDefault) -> TypedDict("Response", {"status": int, "data": Genre}):
    new_id = max((g["id"] for g in temp_genres), default=0) + 1
    genre_dict = genre.model_dump()
    genre_dict["id"] = new_id
    temp_genres.append(genre_dict)
    return {"status": 200, "data": genre_dict}


@app.put("/genres/{genre_id}")
def genre_update(genre_id: int, genre: GenreDefault) -> List[Genre]:
    for i, g in enumerate(temp_genres):
        if g.get("id") == genre_id:
            updated = genre.model_dump()
            updated["id"] = genre_id
            temp_genres[i] = updated
    return temp_genres


@app.delete("/genres/{genre_id}")
def genre_delete(genre_id: int) -> dict:
    for i, g in enumerate(temp_genres):
        if g.get("id") == genre_id:
            temp_genres.pop(i)
            break
    return {"status": 201, "message": "deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
