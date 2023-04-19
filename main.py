from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
# app.mount("/", StaticFiles(directory="public", html = True), name="static")

@app.get("/test")
def test():
    return {"text":"page"}