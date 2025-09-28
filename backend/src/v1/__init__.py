from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from src.db.db import create_db_and_tables


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


@app.on_event("startup")
def on_startup() -> None:
	create_db_and_tables()
