from fastapi import status
from typing import Optional
from logging import Logger, getLogger

from .config import *
from .models import *
from .schemas import *
from .repository import ToDoRepositoryInterface

from ..core.config import *
from ..core.service import *

from .. users.models import UserPublic


logger: Logger = getLogger(f"{LOGGING_PROJECT_NAME}.{'.'.join(__name__.split('.')[-2:])}")


class ToDoService:
	def __init__(self, repository: ToDoRepositoryInterface) -> None:
		self.repository: ToDoRepositoryInterface = repository

	async def create(self, user_id: int, todo_data: CreateTodoRequest) -> ToDo | JSONResponse:
		"""
		Create a new todo with business logic validation.
		This is the application service that orchestrates domain operations.
		"""
		logger.info(f"Creating todo: {todo_data}")

		try:
			response: ToDo = await self.repository.create(user_id, todo_data)
			logger.info(f"Todo created successfully with ID: {response.id}")
			return response

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=f"Internal server error while creating todo: {error}"
			)

	async def get_all(
		self,
		current_user: UserPublic,
		offset: int = PAGINATION_OFFSET,
		limit: int = PAGINATION_LIMIT,
	) -> list[ToDo] | JSONResponse:
		"""Get all todos with pagination: offset and limit"""
		logger.info(f"Retrieving todos with offset={offset}, limit={limit}")

		# Business rule: Check if user is admin
		if not current_user.is_admin:
			logger.error(f"User with ID {current_user.id} is not an admin")
			return make_response(
				logger=logger,
				success=False,
				status_code=status.HTTP_403_FORBIDDEN,
				message=f"Given user does not have the necessary rights for this operation",
			)

		try:
			todos: list[ToDo] = await self.repository.get_all(
				offset=offset,
				limit=limit
			)
			logger.info(f"Retrieved {len(todos)} todos")
			return todos

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=f"Internal server error while retrieving todos: {error}"
			)

	async def get_all_user(
		self,
		id: int,
		current_user: UserPublic,
		offset: int = PAGINATION_OFFSET,
		limit: int = PAGINATION_LIMIT,
	) -> list[ToDo] | JSONResponse:
		"""Get all given user's todos with pagination: offset and limit"""
		logger.info(f"Retrieving todos for user {id} with offset={offset}, limit={limit}")

		# Business rule: Check if user is admin
		if not current_user.is_admin and current_user.id != id:
			return make_response(
				logger=logger,
				success=False,
				status_code=status.HTTP_403_FORBIDDEN,
				message=f"Given user does not have the necessary rights for this operation",
			)

		try:
			todos: list[ToDo] = await self.repository.get_all_user(
				id=id,
				offset=offset,
				limit=limit
			)
			logger.info(f"Retrieved {len(todos)} todos")
			return todos

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=f"Internal server error while retrieving todos: {error}"
			)

	async def get(
		self,
		todo_id: int,
		user_id: int,
		current_user: UserPublic,
	) -> ToDo | JSONResponse:
		"""Get given ToDo's ID for given user's ID"""
		logger.info(f"Retrieving todo with ID {todo_id} for user with ID {user_id}")

		# Business rule: Check if user is admin
		if not current_user.is_admin and current_user.id != user_id:
			return make_response(
				logger=logger,
				success=False,
				status_code=status.HTTP_403_FORBIDDEN,
				message=f"Given user does not have the necessary rights for this operation",
			)

		try:
			todo: ToDo | JSONResponse = await self.repository.get(
				todo_id=todo_id,
				user_id=user_id
			)
			logger.info(f"Retrieved todo: {todo}")
			return todo

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=f"Internal server error while retrieving todo: {error}"
			)

	async def patch(
		self,
		todo_id: int,
		todo_data: PatchTodoRequest,
		user_id: int,
		current_user: UserPublic
	) -> ToDo | JSONResponse:
		"""Update given ToDo's ID for given user's ID"""
		logger.info(f"Updating todo with ID {todo_id} for user with ID {user_id}")

		try:
			# Business rule: Check if user is admin
			if not current_user.is_admin and current_user.id != user_id:
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_403_FORBIDDEN,
					message=f"Given user does not have the necessary rights for this operation",
				)

			todo: Optional[ToDo] = await self.repository.get(
				todo_id=todo_id,
				user_id=user_id
			)
			if not todo:
				logger.warning(f"Todo with ID {todo_id} not found")
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_404_NOT_FOUND,
					message=f"Todo with ID {todo_id} not found",
				)

			todo: ToDo | JSONResponse = await self.repository.patch(
				todo_id=todo_id,
				todo_data=todo_data.model_dump(exclude_unset=True)
			)
			logger.info(f"Updated todo: {todo}")
			return todo

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=f"Internal server error while updating todo: {error}"
			)


	async def delete(
		self,
		todo_id: int,
		user_id: int,
		current_user: UserPublic
	) -> bool | JSONResponse:
		logger.info(f"Deleting todo with ID: {todo_id} for user with ID: {user_id}")

		try:
			# Business rule: Check if current user is trying to access their own data or is admin
			if not current_user.is_admin and current_user.id != id:
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_403_FORBIDDEN,
					message=f"Given user does not have the necessary rights for this operation",
				)

			todo: Optional[ToDo] = await self.repository.get(
				todo_id=todo_id,
				user_id=user_id
			)
			if not todo:
				logger.warning(f"Todo with ID {todo_id} not found")
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_404_NOT_FOUND,
					message=f"Todo with ID {todo_id} not found",
				)

			result: bool = await self.repository.delete(todo_id)
			if not result:
				logger.error(f"Failed to delete todo with ID {todo_id}")
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
					message=f"Failed to delete ToDo with ID {todo_id}",
				)

			logger.info(f"ToDo with ID {todo_id} deleted successfully")
			return True

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=f"Internal server error while deleting ToDo with id {todo_id}: {error}"
			)
