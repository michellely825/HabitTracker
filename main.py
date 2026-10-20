from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, habits
from database import get_connection
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
def health_check():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1;")
        return {"status": "ok", "message": "DB connection is alive"}
    except psycopg2.Error as e:
        print(f"Health check DB error: {e}")
        return {"status": "bad", "message": "DB error occurred"}
    finally:
        cursor.close()
        conn.close()


app.include_router(users.router)
app.include_router(habits.router)
