import requests
from fastapi import APIRouter, HTTPException
from app.schemas import DeezerTrack

router = APIRouter()


@router.get("/songs/search", response_model=list[DeezerTrack])
def search_songs(q: str):
    """Search for songs using the Deezer API."""
    url = f"https://api.deezer.com/search?q={q}"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error fetching data from Deezer")

    data = response.json().get("data", [])

    # Format the response to match your `DeezerTrack` schema
    results = [
        {
            "deezer_track_id": song["id"],
            "title": song["title"],
            "artist": song["artist"]["name"],
            "preview_url": song["preview"],
            "album_cover": song["album"]["cover"],
        }
        for song in data
    ]

    return results
