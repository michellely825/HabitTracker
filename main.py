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
    conn = None  # preassigns conn in the scenario where get_connection fails and conn & cursor are not assigned but closed in finally block
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        return {"status": "ok", "message": "DB connection is alive"}
    except psycopg2.OperationalError as e:  # e.g. if postgres is down, unreachable etc
        print(f"Health check connection error: {e}")
        return {"status": "bad", "message": "Could not connect to database"}
    except psycopg2.Error as e:  # e.g. bad SQL syntax
        print(f"Health check DB error: {e}")
        return {"status": "bad", "message": "Database error occurred"}
    finally:  # finally always runs before an exception is allowed to continue propagating further — regardless of whether anything ever catches it.
        if conn:  # only closes objs if they were successfully created
            cursor.close()
            conn.close()


app.include_router(users.router)
app.include_router(habits.router)
