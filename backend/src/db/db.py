from typing import Any, Generator

from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine

from ..resources.config import DB_URL, DB_CONNECT_ARGS


engine: Engine = create_engine(DB_URL, connect_args=DB_CONNECT_ARGS, echo=True)


def create_db_and_tables() -> None:
	SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, Any, None]:
	with Session(engine) as session:
		yield session
