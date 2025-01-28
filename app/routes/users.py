from fastapi import APIRouter
from fastapi import Depends, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.schemas import UserCreate, UserResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/users/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
def create_users(user: UserCreate, db: Session = Depends(get_db)):
    # TODO hash password here (later)
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return {"id": user.id, "username": user.username}
    return {"error": "User not found"}
