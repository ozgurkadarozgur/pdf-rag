from fastapi import FastAPI

from app.database import init_db
from app.router import router

init_db()

app = FastAPI()

app.include_router(router)