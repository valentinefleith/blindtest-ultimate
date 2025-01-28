from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserLogin
from app.models import User
from app.utils import verify_password

router = APIRouter(tags=["Authentification"])


@router.post("/login")
def login(user_cred: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_cred.username).first()
    if not user or not verify_password(user_cred.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
        )
    return "Success"
