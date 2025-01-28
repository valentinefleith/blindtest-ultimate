from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return {"id": user.id, "username": user.username}
    return {"error": "User not found"}


@router.post("/users")
def create_users():
    return {"message": "User created"}
