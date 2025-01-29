import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base
from app.models import User
from app.routes.auth import create_jwt_token
from sqlalchemy.orm import sessionmaker

client = TestClient(app)

# Create a test database session
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Creates a fresh database for each test."""
    Base.metadata.drop_all(bind=engine)  # Drop all tables before test
    Base.metadata.create_all(bind=engine)  # Recreate tables
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_users_me_authenticated(db_session):
    """Test accessing /users/me with a valid JWT token"""
    # Create a test user
    test_user = User(
        username="testuser", email="test@example.com", password="hashedpassword"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    # Generate a JWT token for this user
    token = create_jwt_token({"user_id": test_user.id})

    # Make a request with the token
    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_users_me_unauthenticated():
    """Test accessing /users/me without a token (should return 401)"""
    response = client.get("/api/users/me")
    assert response.status_code == 401  # Unauthorized
    assert response.json() == {"detail": "Not authenticated"}


def test_users_me_invalid_token():
    """Test accessing /users/me with an invalid JWT token"""
    response = client.get(
        "/api/users/me", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401  # Unauthorized
    assert response.json() == {"detail": "Could not validate credentials"}
