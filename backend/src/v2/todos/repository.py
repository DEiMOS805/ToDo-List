from typing import Optional
from datetime import datetime
from sqlalchemy import and_, Update
from abc import ABC, abstractmethod
from logging import Logger, getLogger
from sqlmodel import Session, select, update

from .config import *
from .models import *

from .. core.config import *


logger: Logger = getLogger(f"{LOGGING_PROJECT_NAME}.{'.'.join(__name__.split('.')[-2:])}")



class ToDoRepositoryInterface(ABC):
	"""
	Repository interface following DDD principles.
	This defines the contract for user persistence operations.
	"""

	@abstractmethod
	async def create(self, todo_id: int, todo_data: ToDoBase) -> ToDo:
		pass

	@abstractmethod
	async def get_all(self, skip: int = PAGINATION_OFFSET, limit: int = PAGINATION_LIMIT) -> list[Optional[ToDo]]:
		pass

	@abstractmethod
	async def get_all_user(self, user_id: int, skip: int = PAGINATION_OFFSET, limit: int = PAGINATION_LIMIT) -> list[Optional[ToDo]]:
		pass

	@abstractmethod
	async def get(self, todo_id: int, user_id: int) -> Optional[ToDo]:
		pass

	@abstractmethod
	async def patch(self, todo_id: int, todo_data: dict) -> ToDo:
		pass

	@abstractmethod
	async def delete(self, todo_id: int) -> bool:
		pass


class ToDoSqlRepository(ToDoRepositoryInterface):
	"""
	SQLAlchemy implementation of RepositoryInterface.
	This is the infrastructure layer implementation.
	"""

	def __init__(self, session: Session) -> None:
		self.session: Session = session

	async def create(self, todo_id: int, data: ToDoBase) -> ToDo:
		logger.info(f"Creating todo in DB")

		db_todo = ToDo(user_id=todo_id, **data.model_dump())

		self.session.add(db_todo)
		self.session.commit()
		self.session.refresh(db_todo)

		return db_todo

	async def get_all(
		self,
		offset: int = PAGINATION_OFFSET,
		limit: int = PAGINATION_LIMIT
	) -> list[Optional[ToDo]]:

		logger.info(f"Retrieving all todos from DB with offset={offset} and limit={limit}")
		statement = select(ToDo).offset(offset).limit(limit)
		todos = self.session.exec(statement).all()
		return todos

	async def get_all_user(
		self,
		user_id: int,
		offset: int = PAGINATION_OFFSET,
		limit: int = PAGINATION_LIMIT
	) -> list[Optional[ToDo]]:

		logger.info(f"Retrieving all todos for user {user_id} from DB with offset={offset} and limit={limit}")
		statement = select(ToDo) \
			.where(ToDo.user_id == user_id) \
			.offset(offset) \
			.limit(limit)
		todos = self.session.exec(statement).all()
		return todos

	async def get(self, todo_id: int, user_id: int) -> Optional[ToDo]:
		logger.info(f"Retrieving todo with ID: {todo_id} from DB")
		statement = select(ToDo).where(
			and_(
				ToDo.id == todo_id,
				ToDo.user_id == user_id,
			)
		)
		todo: Optional[ToDo] = self.session.exec(statement).first()

		if todo:
			return todo
		return None

	async def patch(self, todo_id: int, todo_data: dict[str, Any]) -> ToDo:
		logger.info(f"Updating todo with ID: {todo_id} in DB")

		values: dict[str, Any] = {
			"updated_at": datetime.now(),
			**todo_data
		}

		logger.info(f"Values to update: {values}")

		statement: Update = update(ToDo).where(ToDo.id == todo_id).values(**values)
		self.session.exec(statement)
		self.session.commit()

		statement = select(ToDo).where(ToDo.id == todo_id)
		return self.session.exec(statement).first()

	async def delete(self, todo_id: int) -> bool:
		logger.info(f"Deleting todo with ID: {todo_id} in DB")
		statement = select(ToDo).where(ToDo.id == todo_id)
		todo = self.session.exec(statement).first()

		if not todo:
			return False

		self.session.delete(todo)
		self.session.commit()
		return True
