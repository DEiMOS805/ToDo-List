from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine

from src.resources.config import DB_URL, DB_CONNECT_ARGS


engine: Engine = create_engine(DB_URL, connect_args=DB_CONNECT_ARGS)


def create_db_and_tables() -> None:
	SQLModel.metadata.create_all(engine)


def get_session():
	with Session(engine) as session:
		yield session
