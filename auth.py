import bcrypt


def hash_password(password):
    password_bytes = password.encode("utf-8")
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt=bcrypt.gensalt())
    hashed_password_str = hashed_password_bytes.decode(
        "utf-8"
    )  # bytes -> str necessary bc my DB requires password_hash to be a str type
    return hashed_password_str
