from fastapi import FastAPI

from app.database import init_db
from app.auth.router import router as auth_router
from app.routers.users import router as users_router
from app.routers.books import router as books_router
from app.routers.genres import router as genres_router
from app.routers.exchanges import router as exchanges_router

app = FastAPI(
    title="Bookcrossing API",
    description="Веб-приложение для обмена книгами между пользователями",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root() -> dict:
    return {"message": "Добро пожаловать в Bookcrossing API!"}


# Подключение роутеров
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(books_router)
app.include_router(genres_router)
app.include_router(exchanges_router)
