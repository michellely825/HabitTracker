from fastapi import FastAPI

# creates an empty instance of FastAPI app which will hold all the routes
app = FastAPI()


@app.get("/")
def root():
    return {"message": "welcome! habit tracker is alive"}


@app.get("/habits")
def get_habits():
    return
