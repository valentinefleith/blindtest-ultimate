import requests
from fastapi import APIRouter, HTTPException, Query
from app.schemas import DeezerTrack

router = APIRouter()

DEEZER_API_URL = "https://api.deezer.com/search"


@router.get("/search", response_model=list[DeezerTrack])
def search_tracks(
    query: str = Query(..., description="Le titre, artiste ou album à rechercher"),
    limit: int = Query(10, description="Nombre maximum de résultats à retourner"),
):
    """Recherche des morceaux sur Deezer en fonction du titre, artiste ou album"""
    response = requests.get(DEEZER_API_URL, params={"q": query, "limit": limit})

    if response.status_code != 200:
        raise HTTPException(
            status_code=500, detail="Erreur lors de l'accès à l'API Deezer"
        )

    data = response.json().get("data", [])

    # On extrait seulement les champs nécessaires
    tracks = [
        DeezerTrack(
            deezer_track_id=track["id"],
            title=track["title"],
            artist=track["artist"]["name"],
            preview_url=track.get("preview", None),
            album_cover=track["album"]["cover_medium"],
        )
        for track in data
    ]

    return tracks
