from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    email: EmailStr
    username: str
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class DeezerTrack(BaseModel):
    """Représente une chanson provenant de Deezer"""

    deezer_track_id: int  # Identifiant Deezer
    title: str
    artist: str
    preview_url: Optional[str] = None  # Peut être null si indisponible
    album_cover: Optional[str] = None  # Peut être null


class PlaylistResponse(BaseModel):
    """Représente la playlist de l'utilisateur avec ses morceaux"""

    id: int
    user_id: int
    name: str
    songs: list[DeezerTrack] = []  # Contient des objets DeezerTrack

    model_config = ConfigDict(from_attributes=True)
