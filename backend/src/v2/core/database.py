from os import getenv
from typing import Any
from typing import Generator
from sqlalchemy import Engine
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

from .config import *


load_dotenv(DOTENV_ABSPATH)


class DatabaseConfig:
	def __init__(self) -> None:
		self.database_url: str = getenv("DB_URL", None)
		if not self.database_url:
			raise ValueError("Database URL not found in environment variables.")

		connect_args: dict = {}
		if self.database_url.startswith("sqlite"):
			connect_args: dict[str, Any] = DB_CONNECT_ARGS

		self.engine: Engine = create_engine(
			self.database_url,
			connect_args=connect_args,
			echo=False  # Set to False in production
		)

	def create_db_and_tables(self) -> None:
		SQLModel.metadata.create_all(self.engine)

	def get_session(self) -> Generator[Session, Any, None]:
		with Session(self.engine) as session:
			yield session


db_config = DatabaseConfig()
