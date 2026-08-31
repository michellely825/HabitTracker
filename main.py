from fastapi import FastAPI

# creates an empty instance of FastAPI app which will hold all the routes
app = FastAPI()


# TODO: should I move these routes into their own folders?
@app.get("/")
def root():
    return {"message": "welcome! habit tracker is alive"}


@app.post("/")
def create_habit():
    try:

        return {"message": "habit successfully created!"}
    except:
        return {"message": "something went wrong!"}
