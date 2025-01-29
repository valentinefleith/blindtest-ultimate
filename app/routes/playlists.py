from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Playlist, PlaylistSong, User
from app.routes.users import get_current_user
from app.schemas import PlaylistResponse, DeezerTrack

router = APIRouter()


@router.get("/playlists/", response_model=PlaylistResponse)
def get_user_playlist(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get the authenticated user's playlist. Creates one if it doesn't exist."""
    playlist = db.query(Playlist).filter(Playlist.user_id == current_user.id).first()

    if not playlist:
        # Auto-création de la playlist si l'utilisateur n'en a pas encore
        playlist = Playlist(user_id=current_user.id)
        db.add(playlist)
        db.commit()
        db.refresh(playlist)

    return playlist


@router.post("/playlists/songs/", response_model=DeezerTrack)
def add_song_to_playlist(
    song: DeezerTrack,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a song from Deezer to the authenticated user's playlist."""
    playlist = db.query(Playlist).filter(Playlist.user_id == current_user.id).first()

    # Si l'utilisateur n'a pas de playlist, on la crée automatiquement
    if not playlist:
        playlist = Playlist(user_id=current_user.id)
        db.add(playlist)
        db.commit()
        db.refresh(playlist)

    # Vérifier si la chanson existe déjà
    existing_song = (
        db.query(PlaylistSong)
        .filter(
            PlaylistSong.playlist_id == playlist.id,
            PlaylistSong.deezer_track_id == song.deezer_track_id,
        )
        .first()
    )
    if existing_song:
        raise HTTPException(
            status_code=400, detail=f"'{song.title}' is already in your playlist"
        )

    # Ajout de la chanson
    new_song = PlaylistSong(
        playlist_id=playlist.id,
        deezer_track_id=song.deezer_track_id,
        title=song.title,
        artist=song.artist,
        preview_url=song.preview_url,
        album_cover=song.album_cover,
    )
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song


@router.delete("/playlists/songs/{deezer_track_id}")
def remove_song_from_playlist(
    deezer_track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a song from the authenticated user's playlist using its Deezer ID."""
    playlist = db.query(Playlist).filter(Playlist.user_id == current_user.id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    song = (
        db.query(PlaylistSong)
        .filter(
            PlaylistSong.playlist_id == playlist.id,
            PlaylistSong.deezer_track_id == deezer_track_id,
        )
        .first()
    )
    if not song:
        raise HTTPException(status_code=404, detail="Song not found in your playlist")

    db.delete(song)
    db.commit()
    return {"message": f"'{song.title}' removed from your playlist"}
