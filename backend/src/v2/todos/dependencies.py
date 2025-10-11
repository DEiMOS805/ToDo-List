from fastapi import Depends
from sqlmodel import Session
from typing import Any, Generator

from .service import ToDoService
from .repository import ToDoRepositoryInterface, ToDoSqlRepository

from ..core.database import db_config


###############################################################################
################################### Database ##################################
###############################################################################
def get_db_session() -> Generator[Session, Any, None]:
	yield from db_config.get_session()


def get_repository(
	session: Session = Depends(get_db_session)
) -> ToDoRepositoryInterface:

	return ToDoSqlRepository(session)


def get_service(
	repository: ToDoRepositoryInterface = Depends(get_repository),
) -> ToDoService:

	return ToDoService(repository)
