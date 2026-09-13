import bcrypt
from auth import hash_password


def verify_password(password, hashed_password):
    return bcrypt.checkpw(password, hashed_password)


def test_hash_and_verify_correct_password():
    password = "password123"
    hashed_password = hash_password(password)
    assert verify_password(password.encode("utf-8"), hashed_password.encode("utf-8"))


def test_hash_and_verify_incorrect_password():
    password = "password123"
    hashed_password = hash_password(password)
    assert not verify_password(
        "wrongpassword".encode("utf-8"), hashed_password.encode("utf-8")
    )
