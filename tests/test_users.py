import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base
from app.models import User, Playlist
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


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)


def test_user_registration(db_session):
    response = client.post(
        "/api/users/register",
        json={
            "username": "testuser",
            "password": "1234",
            "email": "testemaillol@mail.com",
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "testemaillol@mail.com"
    assert "id" in data

    user = db_session.query(User).filter(User.email == "testemaillol@mail.com").first()
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "testemaillol@mail.com"

    playlist = db_session.query(Playlist).filter(Playlist.user_id == user.id).first()
    assert playlist is not None
    assert playlist.user_id == user.id
    assert playlist.name == "My Playlist"


def test_playlist_retrieval(db_session):
    """Vérifie que l'utilisateur peut récupérer sa playlist après inscription"""
    # Inscription de l'utilisateur
    response = client.post(
        "/api/users/register",
        json={
            "username": "testuser2",
            "password": "securepassword",
            "email": "testuser2@example.com",
        },
    )
    assert response.status_code == 201  # L'inscription doit réussir

    # Connexion pour récupérer le token JWT
    login_response = client.post(
        "/api/login", data={"username": "testuser2", "password": "securepassword"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Récupérer la playlist de l'utilisateur connecté
    playlist_response = client.get(
        "/api/playlists/", headers={"Authorization": f"Bearer {token}"}
    )
    assert playlist_response.status_code == 200  # La récupération doit réussir

    playlist_data = playlist_response.json()
    assert (
        playlist_data["user_id"] is not None
    )  # Vérifier que la playlist est associée à l'utilisateur
    assert (
        playlist_data["songs"] == []
    )  # Vérifier que la playlist est bien vide au début
