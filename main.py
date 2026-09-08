# TODO: should I move routes into their own folders?
from fastapi import FastAPI, HTTPException
from database import get_connection
from pydantic import BaseModel, field_validator

# creates an empty instance of FastAPI app which will hold all the routes
app = FastAPI()


class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 5:
            raise ValueError("password must be at least 5 characters")
        if not any(char.isdigit() for char in value):
            raise ValueError("password must contain at least one digit")
        return value


@app.get("/")
def root():
    return {"message": "welcome! habit tracker is alive"}


@app.post("/users")
def create_user(user: UserCreate):
    username = user.username
    password = user.password
    conn = get_connection()  # opens fresh connection
    cursor = conn.cursor()  # creates cursor that runs SQL query

    try:
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

        # if it's a SELECT: result = cursor.fetchone() or fetchall()
        # if it's an INSERT/UPDATE/DELETE: conn.commit()

        return {}, 201
    except someSpecificError as e:
        return {"error": "unable to create new user"}, 400
    finally:
        cursor.close()
        conn.close()


@app.post("/habits")
def create_habit():
    try:

        return {"message": "habit successfully created!"}
    except:
        return {"message": "something went wrong!"}
