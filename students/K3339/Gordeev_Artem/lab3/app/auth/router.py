from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User, UserCreate, UserRead
from app.auth.utils import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


class TokenResponse(UserRead):
    """Ответ с JWT-токеном при логине / регистрации."""
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, session: Session = Depends(get_session)) -> User:
    """Регистрация нового пользователя.

    Проверяет уникальность username и email, хэширует пароль и сохраняет
    пользователя в БД.
    """
    # Проверяем уникальность
    existing = session.exec(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username или email уже существует",
        )

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        bio=user_data.bio,
        birth_date=user_data.birth_date,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


class LoginRequest(UserRead):
    """Тело запроса для логина."""
    pass


from pydantic import BaseModel  # noqa: E402


class LoginBody(BaseModel):
    """Тело запроса для логина."""
    username: str
    password: str


@router.post("/login")
def login(body: LoginBody, session: Session = Depends(get_session)) -> dict:
    """Авторизация пользователя (получение JWT-токена).

    Принимает username и password, проверяет и возвращает access_token.
    """
    user = session.exec(select(User).where(User.username == body.username)).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    """Получение информации о текущем аутентифицированном пользователе."""
    return current_user
