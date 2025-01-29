import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.database import engine, Base
from app.models import PlaylistSong
from sqlalchemy.orm import sessionmaker

client = TestClient(app)

# Configuration d'une base de test
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Crée une nouvelle base de test propre à chaque test"""
    Base.metadata.drop_all(bind=engine)  # Supprime toutes les tables
    Base.metadata.create_all(bind=engine)  # Les recrée
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_token(db_session):
    """Crée un utilisateur et retourne un token JWT valide"""
    response = client.post(
        "/api/users/register",
        json={
            "username": "testuser",
            "password": "securepassword",
            "email": "testuser@example.com",
        },
    )
    assert response.status_code == 201  # Vérifier que l'utilisateur est bien créé

    login_response = client.post(
        "/api/login", data={"username": "testuser", "password": "securepassword"}
    )
    assert login_response.status_code == 200  # Vérifier que la connexion fonctionne

    return login_response.json()["access_token"]


def test_search_tracks():
    """Test de la recherche de morceaux via l'API Deezer (mockée)"""
    mock_response = {
        "data": [
            {
                "id": 3135556,
                "title": "Lose Yourself",
                "artist": {"name": "Eminem"},
                "preview": "https://cdns-preview-9.dzcdn.net/stream/c-6e41b8d.mp3",
                "album": {
                    "cover_medium": "https://api.deezer.com/album/119606/cover_medium.jpg"
                },
            }
        ]
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        response = client.get("/api/search?query=eminem%20lose%20yourself")
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["deezer_track_id"] == 3135556
        assert data[0]["title"] == "Lose Yourself"
        assert data[0]["artist"] == "Eminem"
        assert (
            data[0]["preview_url"]
            == "https://cdns-preview-9.dzcdn.net/stream/c-6e41b8d.mp3"
        )
        assert (
            data[0]["album_cover"]
            == "https://api.deezer.com/album/119606/cover_medium.jpg"
        )


def test_add_song_from_deezer(db_session, auth_token):
    """Vérifie qu'une chanson trouvée via Deezer peut être ajoutée à la playlist"""
    song_data = {
        "deezer_track_id": 3135556,
        "title": "Lose Yourself",
        "artist": "Eminem",
        "preview_url": "https://cdns-preview-9.dzcdn.net/stream/c-6e41b8d.mp3",
        "album_cover": "https://api.deezer.com/album/119606/cover_medium.jpg",
    }

    response = client.post(
        "/api/playlists/songs/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=song_data,
    )

    assert response.status_code == 200  # L'ajout doit réussir
    song_response = response.json()
    assert song_response["deezer_track_id"] == song_data["deezer_track_id"]
    assert song_response["title"] == song_data["title"]
    assert song_response["artist"] == song_data["artist"]
    assert song_response["preview_url"] == song_data["preview_url"]

    # Vérifier en base que la chanson est bien ajoutée
    playlist_song = (
        db_session.query(PlaylistSong)
        .filter(PlaylistSong.deezer_track_id == song_data["deezer_track_id"])
        .first()
    )
    assert playlist_song is not None
    assert playlist_song.title == song_data["title"]
