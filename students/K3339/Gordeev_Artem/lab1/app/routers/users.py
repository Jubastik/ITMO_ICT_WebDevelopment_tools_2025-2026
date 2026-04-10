from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models.user import (
    User, UserRead, UserReadWithBooks, UserUpdate, UserPasswordChange,
)
from app.auth.dependencies import get_current_user
from app.auth.utils import verify_password, hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserRead])
def users_list(session: Session = Depends(get_session)) -> List[User]:
    """Получение списка всех пользователей."""
    return session.exec(select(User)).all()


@router.get("/{user_id}", response_model=UserReadWithBooks)
def user_get(user_id: int, session: Session = Depends(get_session)) -> User:
    """Получение пользователя по id с вложенными книгами."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.patch("/me", response_model=UserRead)
def user_update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> User:
    """Обновление профиля текущего пользователя."""
    update_dict = user_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(current_user, key, value)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.post("/me/change-password")
def user_change_password(
    passwords: UserPasswordChange,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """Смена пароля текущего пользователя."""
    if not verify_password(passwords.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль",
        )
    current_user.hashed_password = hash_password(passwords.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Пароль успешно изменён"}


@router.delete("/{user_id}")
def user_delete(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Удаление пользователя (только самого себя)."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Можно удалить только свой аккаунт",
        )
    session.delete(current_user)
    session.commit()
    return {"ok": True}
