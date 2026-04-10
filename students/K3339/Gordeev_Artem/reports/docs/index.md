# Лабораторная работа 1. Буккросинг API на FastAPI

**Студент:** Гордеев Артём  
**Группа:** K3339  
**Тема:** Разработка веб-приложения для буккросинга  

## Описание

Реализовано серверное приложение на FastAPI для обмена книгами между пользователями (буккросинг). Приложение позволяет:

- Создавать профили пользователей с авторизацией по JWT
- Добавлять книги в виртуальную библиотеку
- Искать книги других пользователей
- Отправлять и принимать запросы на обмен книгами
- Просматривать историю обменов

## Ссылки на практики

- [Практика 1.1 — Базовое приложение на FastAPI](https://github.com/Jubastik/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3339/Gordeev_Artem/practices/1.1)
- [Практика 1.2 — SQLModel + PostgreSQL](https://github.com/Jubastik/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3339/Gordeev_Artem/practices/1.2)
- [Практика 1.3 — Alembic + .env + .gitignore](https://github.com/Jubastik/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3339/Gordeev_Artem/practices/1.3)

---

## Модель данных

Реализовано **6 таблиц**:

| Таблица | Описание |
|---|---|
| `User` | Пользователи системы |
| `Book` | Книги пользователей |
| `Genre` | Жанры книг |
| `BookGenreLink` | Связь many-to-many между Book и Genre (с доп. полем `note`) |
| `ExchangeRequest` | Запросы на обмен книгами |
| `ExchangeHistory` | История состоявшихся обменов |

### Связи

- **One-to-many:** User → Book (пользователь владеет книгами)
- **One-to-many:** User → ExchangeRequest (отправленные/полученные запросы)
- **Many-to-many:** Book ↔ Genre (через BookGenreLink)
- **One-to-many:** ExchangeRequest → ExchangeHistory

### Ассоциативная сущность

`BookGenreLink` содержит дополнительное поле `note`, характеризующее связь (например, «основной жанр», «второстепенный жанр»).

---

## Модели (SQLModel)

### User

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    birth_date: Optional[date] = None

    books: List["Book"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    sent_requests: List["ExchangeRequest"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[ExchangeRequest.sender_id]",
        },
    )
    received_requests: List["ExchangeRequest"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[ExchangeRequest.receiver_id]",
        },
    )
```

### Book

```python
class Book(BookDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner: Optional["User"] = Relationship(back_populates="books")
    genres: List["Genre"] = Relationship(
        back_populates="books", link_model=BookGenreLink
    )
```

### Genre

```python
class Genre(GenreDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    books: List["Book"] = Relationship(
        back_populates="genres", link_model=BookGenreLink
    )
```

### BookGenreLink (ассоциативная таблица)

```python
class BookGenreLink(SQLModel, table=True):
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
```

### ExchangeRequest

```python
class ExchangeRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    sender_book_id: int = Field(foreign_key="book.id")
    receiver_book_id: int = Field(foreign_key="book.id")
    status: ExchangeStatus = Field(default=ExchangeStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = None

    sender: Optional["User"] = Relationship(back_populates="sent_requests", ...)
    receiver: Optional["User"] = Relationship(back_populates="received_requests", ...)
    sender_book: Optional["Book"] = Relationship(...)
    receiver_book: Optional["Book"] = Relationship(...)
    history: Optional["ExchangeHistory"] = Relationship(back_populates="request")
```

### ExchangeHistory

```python
class ExchangeHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="exchangerequest.id")
    exchanged_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    request: Optional[ExchangeRequest] = Relationship(back_populates="history")
```

---

## Подключение к БД

PostgreSQL поднимается через Docker Compose:

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: bookcrossing_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
```

Подключение в приложении (`app/database.py`):

```python
from sqlmodel import SQLModel, Session, create_engine
from app.config import settings

engine = create_engine(settings.DB_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

Переменные окружения (`.env`):

```
DB_URL=postgresql://postgres:postgres@localhost:5432/bookcrossing_db
SECRET_KEY=super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Эндпоинты API

### Auth (авторизация)

| Метод | Путь | Описание |
|---|---|---|
| POST | `/auth/register` | Регистрация нового пользователя |
| POST | `/auth/login` | Авторизация (получение JWT-токена) |
| GET | `/auth/me` | Информация о текущем пользователе (по токену) |

### Users (пользователи)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/users/` | Список всех пользователей |
| GET | `/users/{user_id}` | Пользователь по id (с вложенными книгами) |
| PATCH | `/users/me` | Обновление профиля (авторизованный) |
| POST | `/users/me/change-password` | Смена пароля |
| DELETE | `/users/{user_id}` | Удаление аккаунта (только самого себя) |

### Books (книги)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/books/` | Список книг (фильтрация, поиск) |
| GET | `/books/{book_id}` | Книга по id (с вложенными жанрами) |
| POST | `/books/` | Добавление книги (авторизованный) |
| PATCH | `/books/{book_id}` | Обновление книги (только владелец) |
| DELETE | `/books/{book_id}` | Удаление книги (только владелец) |
| POST | `/books/{book_id}/genres/{genre_id}` | Добавление жанра к книге |
| DELETE | `/books/{book_id}/genres/{genre_id}` | Удаление жанра у книги |

### Genres (жанры)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/genres/` | Список жанров |
| GET | `/genres/{genre_id}` | Жанр по id |
| POST | `/genres/` | Создание жанра |
| PATCH | `/genres/{genre_id}` | Обновление жанра |
| DELETE | `/genres/{genre_id}` | Удаление жанра |

### Exchanges (обмен)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/exchanges/requests` | Мои запросы на обмен |
| GET | `/exchanges/requests/{request_id}` | Запрос по id |
| POST | `/exchanges/requests` | Создание запроса на обмен |
| PATCH | `/exchanges/requests/{request_id}` | Подтверждение/отклонение запроса |
| DELETE | `/exchanges/requests/{request_id}` | Удаление запроса (pending) |
| GET | `/exchanges/history` | История обменов |

---

## Аутентификация

JWT-аутентификация реализована **вручную** (без сторонних библиотек):

- **Хэширование паролей** — bcrypt через passlib
- **Генерация JWT** — python-jose (HS256)
- **Dependency** — `get_current_user` извлекает токен из заголовка `Authorization: Bearer <token>`

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    username = payload.get("sub")
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user
```

---

## Миграции (Alembic)

Alembic настроен с автогенерацией миграций. URL базы данных передаётся из `.env`:

```python
# migrations/env.py
load_dotenv()
config.set_main_option("sqlalchemy.url", os.getenv("DB_URL"))
target_metadata = sqlmodel.SQLModel.metadata
```

Команды:

```bash
# Создание миграции
alembic revision --autogenerate -m "initial tables"

# Применение миграций
alembic upgrade head
```

---

## Структура проекта

```
lab1/
├── .env                    # Переменные окружения
├── .gitignore
├── alembic.ini             # Конфигурация Alembic
├── docker-compose.yml      # PostgreSQL в Docker
├── requirements.txt
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app + роутеры
│   ├── config.py           # Настройки из .env
│   ├── database.py         # Подключение к БД
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py       # /auth/register, /auth/login, /auth/me
│   │   ├── utils.py        # JWT, хэширование паролей
│   │   └── dependencies.py # get_current_user
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py         # User, UserCreate, UserRead...
│   │   ├── book.py         # Book, BookDefault, BookReadWithGenres...
│   │   ├── genre.py        # Genre, GenreDefault, GenreRead
│   │   ├── links.py        # BookGenreLink (ассоциативная)
│   │   └── exchange.py     # ExchangeRequest, ExchangeHistory
│   └── routers/
│       ├── __init__.py
│       ├── users.py        # CRUD пользователей
│       ├── books.py        # CRUD книг + жанры
│       ├── genres.py       # CRUD жанров
│       └── exchanges.py    # Запросы на обмен + история
```

---

## Запуск

```bash
# 1. Поднять PostgreSQL
docker compose up -d

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать и применить миграции
alembic revision --autogenerate -m "initial tables"
alembic upgrade head

# 4. Запустить сервер
uvicorn app.main:app --reload
```

Документация API доступна по адресу: `http://127.0.0.1:8000/docs`
