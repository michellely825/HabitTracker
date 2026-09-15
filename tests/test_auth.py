import pytest
from auth import hash_password, verify_password
from main import generate_token, verify_token


def test_hash_and_verify_correct_password():
    password = "password123"
    hashed_password = hash_password(password)
    assert verify_password(password, hashed_password)


def test_hash_and_verify_incorrect_password():
    password = "password123"
    hashed_password = hash_password(password)
    assert not verify_password("wrongpassword", hashed_password)


# # this fx runs before each fx that calls it as a param
# @pytest.fixture
# def payload_param():
#     return {"username": ""}


# def test_generate_token():
#     token = generate_token(payload={"user_id": 1, "username": "user1"})
#     assert verify_token(token) == {"user_id": 1, "username": "user1"}
