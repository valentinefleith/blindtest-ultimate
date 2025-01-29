from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Un utilisateur a UNE seule playlist
    playlist = relationship("Playlist", back_populates="user", uselist=False)


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String, default="My Playlist", nullable=False)

    user = relationship("User", back_populates="playlist")
    songs = relationship(
        "PlaylistSong", back_populates="playlist", cascade="all, delete-orphan"
    )


class PlaylistSong(Base):
    __tablename__ = "playlist_songs"

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(
        Integer,
        ForeignKey("playlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    deezer_track_id = Column(Integer, nullable=False, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    preview_url = Column(String, nullable=True)
    album_cover = Column(String, nullable=True)

    playlist = relationship("Playlist", back_populates="songs")
