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


# Créer la base de test
Base.metadata.create_all(bind=engine)


def test_read_user(db_session):
    # Ajouter un utilisateur test
    new_user = User(username="testuser", password="1234")
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    # Tester la route GET /api/users/{user_id}
    response = client.get(f"/api/users/{new_user.id}")

    assert response.status_code == 200
    assert response.json() == {"id": new_user.id, "username": "testuser"}
