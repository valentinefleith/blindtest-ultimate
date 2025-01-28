from app.auth import hash_password, verify_password


def test_hash_password():
    """Test if the password is correctly hashed"""
    plain_password = "securepassword123"
    hashed_password = hash_password(plain_password)

    assert isinstance(hashed_password, bytes)  # The hashed password should be in bytes
    assert (
        hashed_password != plain_password.encode()
    )  # It should not be the same as plain text


def test_verify_password():
    """Test password verification"""
    plain_password = "securepassword123"
    hashed_password = hash_password(plain_password)

    assert verify_password(
        plain_password, hashed_password
    )  # Should return True for correct password
    assert not verify_password(
        "wrongpassword", hashed_password
    )  # Should return False for wrong password
