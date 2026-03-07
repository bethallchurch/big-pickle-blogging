from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import auth, articles, health

app = FastAPI()

app.include_router(health.router)
app.include_router(articles.router)
app.include_router(auth.router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
