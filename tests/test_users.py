import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base
from app.models import User
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
