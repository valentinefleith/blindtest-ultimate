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


class PlaylistSongRequest(BaseModel):
    deezer_track_id: str
    title: str
    artist: str
    preview_url: Optional[str] = None


class PlaylistResponse(BaseModel):
    id: int
    user_id: int
    name: str
    songs: list[PlaylistSongRequest] = []

    model_config = ConfigDict(from_attributes=True)
