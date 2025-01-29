from fastapi import APIRouter, HTTPException
from fastapi import Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Playlist
from app.schemas import UserCreate, UserResponse
from app.utils import hash_password
from app.routes.auth import get_curr_user

router = APIRouter()


@router.post(
    "/users/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
def create_users(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    existing_email = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nom d'utilisateur est déjà pris.",
        )
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'adresse email est déjà utilisée.",
        )

    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, username=user.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_playlist = Playlist(user_id=new_user.id)
    db.add(new_playlist)
    db.commit()
    db.refresh(new_playlist)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "created_at": new_user.created_at,
        "message": "Utilisateur créé avec succès",
    }


@router.get("/users/me")
def get_current_user(
    current_user: User = Depends(get_curr_user), db: Session = Depends(get_db)
):
    return current_user


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return {"id": user.id, "username": user.username}
    return {"error": "User not found"}
