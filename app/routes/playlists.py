from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Playlist, PlaylistSong, User
from app.routes.users import get_current_user
from app.schemas import PlaylistResponse, PlaylistSongRequest

router = APIRouter()


@router.post("/playlists/", response_model=PlaylistResponse)
def create_playlist(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Create an empty playlist for the authenticated user"""
    existing_playlist = (
        db.query(Playlist).filter(Playlist.user_id == current_user.id).first()
    )
    if existing_playlist:
        return existing_playlist  # Return existing playlist if already created

    playlist = Playlist(user_id=current_user.id)
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


@router.post("/playlists/songs/")
def add_song_to_playlist(
    song: PlaylistSongRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a song to the authenticated user's playlist"""
    playlist = db.query(Playlist).filter(Playlist.user_id == current_user.id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    new_song = PlaylistSong(
        playlist_id=playlist.id,
        deezer_track_id=song.deezer_track_id,
        title=song.title,
        artist=song.artist,
        preview_url=song.preview_url,
    )
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song


@router.get("/playlists/", response_model=PlaylistResponse)
def get_user_playlist(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get the authenticated user's playlist"""
    playlist = db.query(Playlist).filter(Playlist.user_id == current_user.id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist


@router.delete("/playlists/songs/{song_id}")
def remove_song_from_playlist(
    song_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a song from the authenticated user's playlist"""
    song = (
        db.query(PlaylistSong)
        .join(Playlist)
        .filter(Playlist.user_id == current_user.id, PlaylistSong.id == song_id)
        .first()
    )
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    db.delete(song)
    db.commit()
    return {"message": "Song removed"}
