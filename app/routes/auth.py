from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from app.database import get_db
from app.schemas import TokenData
from app.models import User
from app.utils import verify_password

router = APIRouter(tags=["Authentification"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "coiffeur"
ALGORITM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITM)
    return encoded_jwt


def verify_jwt_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITM])
        id = str(payload.get("user_id"))
        if id is None:
            raise credentials_exception
        tokens_data = TokenData(id=id)
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    return tokens_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    tokendata = verify_jwt_token(token, credentials_exception)
    user = db.query(User).filter(User.id == tokendata.id).first()
    return user


@router.post("/login")
def login(
    user_cred: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == user_cred.username).first()
    if not user or not verify_password(user_cred.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )
    access_token = create_jwt_token(data={"user_id": user.id, "username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
