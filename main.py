# TODO: should I move routes into their own folders?
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection
from pydantic import BaseModel, field_validator
import psycopg2

# creates an empty instance of FastAPI app which will hold all the routes
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows requests from any origin (fine for local dev)
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "welcome! habit tracker is alive"}


# validates user payload data before anything else runs in the route
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


# TODO: add real password hashing
@app.post("/users", status_code=201)
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

        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING user_id;",
            (username, password),
        )

        new_user_id = cursor.fetchone()[
            0
        ]  # returns first value in tuple which is user_id
        conn.commit()  # makes insert change permanent

        return {"user_id": new_user_id, "username": username}
    except psycopg2.Error as e:
        return {"error": "unable to create new user due to database error"}, 500
    finally:
        cursor.close()
        conn.close()


@app.post("/habits")
def create_habit():
    try:

        return {"message": "habit successfully created!"}
    except:
        return {"message": "something went wrong!"}
