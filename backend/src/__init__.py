from fastapi import FastAPI

from .db.db import create_db_and_tables


app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
	create_db_and_tables()
