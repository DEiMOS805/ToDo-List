from fastapi import Depends
from sqlmodel import Session
from typing import Any, Generator

from .service import Service
from .repository import RepositoryInterface, SqlRepository

from ..core.database import db_config


def get_db_session() -> Generator[Session, Any, None]:
	yield from db_config.get_session()


def get_repository(
	session: Session = Depends(get_db_session)
) -> RepositoryInterface:

	return SqlRepository(session)


def get_service(
	repository: RepositoryInterface = Depends(get_repository)
) -> Service:

	return Service(repository)
