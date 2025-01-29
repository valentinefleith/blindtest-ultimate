from fastapi import APIRouter
from fastapi import Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.utils import hash_password
from app.routes.auth import get_current_user

router = APIRouter()


@router.post(
    "/users/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
def create_users(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, username=user.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users/me")
def get_current_user(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return current_user


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return {"id": user.id, "username": user.username}
    return {"error": "User not found"}
