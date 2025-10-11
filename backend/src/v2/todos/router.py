from logging import Logger, getLogger
from fastapi.responses import JSONResponse
from typing import Any, Optional, Annotated
from fastapi import APIRouter, Path, Query, status, Depends

from .config import *
from .schemas import *
from .models import ToDo
from .service import ToDoService
from .dependencies import get_service

from .. core.config import *
from .. core.schemas import *
from .. core.service import *

from .. users.models import UserPublic
from .. users.dependencies import get_current_active_user


logger: Logger = getLogger(f"{LOGGING_PROJECT_NAME}.{'.'.join(__name__.split('.')[-2:])}")
router = APIRouter(prefix=f"/{ROUTER_PREFIX}", tags=["ToDos"])


@router.post(
	path='/',
	summary="Creates a new ToDo for a user",
	response_model=dict[str, Any],
	status_code=status.HTTP_201_CREATED,
	responses=get_model_schema_for_docs(
		model=BaseResponse,
		responses={
			200: "Request completed successfully",
			201: "ToDo created successfully",
			422: "Unprocessable Entity: Validation Error",
			500: "Internal Server Error"
		}
	)
)
async def create_todo(
	request: CreateTodoRequest,
	service: ToDoService = Depends(get_service),
	current_user: UserPublic = Depends(get_current_active_user)
) -> JSONResponse:

	try:
		logger.info("Received request to create todo")
		response: ToDo | JSONResponse = await service.create(
			user_id=current_user.id,
			todo_data=request
		)

		if isinstance(response, JSONResponse):
			return response

		return make_response(
			logger=logger,
			status_code=status.HTTP_201_CREATED,
			message="ToDo created successfully",
			data=response.model_dump(mode="json")
		)

	except Exception as error:
		return make_error_response(
			logger=logger,
			type=type(error).__name__,
			error=error
		)


@router.get(
	path='/',
	summary="Gets all ToDos",
	response_model=dict[str, Any],
	status_code=status.HTTP_200_OK,
	responses=get_model_schema_for_docs(
		model=BaseResponse,
		responses={
			200: "Retrieved ToDos successfully",
			204: "No content: No ToDos found",
			403: "Forbidden: User does not have access rights",
			500: "Internal Server Error"
		}
	)
)
async def get_all_todos(
	offset: Annotated[int, Query(ge=0)] = PAGINATION_OFFSET,
	limit: Annotated[int, Query(ge=1)] = PAGINATION_LIMIT,
	service: ToDoService = Depends(get_service),
	current_user: UserPublic = Depends(get_current_active_user)
) -> JSONResponse:

	try:
		logger.info("Received request to get all todos")
		response: list[Optional[ToDo]] | JSONResponse = await service.get_all(
			offset=offset,
			limit=limit,
			current_user=current_user
		)

		if isinstance(response, JSONResponse):
			return response

		if not response:
			return make_response(
				logger=logger,
				status_code=status.HTTP_204_NO_CONTENT,
				message="No todos found",
				data={"todos": []}
			)

		return make_response(
			logger=logger,
			status_code=status.HTTP_200_OK,
			message="ToDos retrieved successfully",
			data={
				"todos": [
					todo.model_dump(mode="json")
					for todo in response
				],
				"count": len(response)
			}
		)

	except Exception as error:
		return make_error_response(
			logger=logger,
			type=type(error).__name__,
			error=error
		)


@router.get(
	path="/users/{user_id}",
	summary="Gets all given user's ToDos",
	response_model=dict[str, Any],
	status_code=status.HTTP_200_OK,
	responses=get_model_schema_for_docs(
		model=BaseResponse,
		responses={
			200: "Retrieved ToDos successfully",
			204: "No content: No ToDos found",
			403: "Forbidden: User does not have access rights",
			500: "Internal Server Error"
		}
	)
)
async def get_all_user_todos(
	user_id: Annotated[int, Path(gt=0)],
	offset: Annotated[int, Query(ge=0)] = PAGINATION_OFFSET,
	limit: Annotated[int, Query(ge=1)] = PAGINATION_LIMIT,
	service: ToDoService = Depends(get_service),
	current_user: UserPublic = Depends(get_current_active_user)
) -> JSONResponse:

	try:
		logger.info(f"Received request to get all todos for user with ID: {user_id}")
		response: list[Optional[ToDo]] | JSONResponse = await service.get_all_user(
			id=user_id,
			current_user=current_user,
			offset=offset,
			limit=limit
		)

		if isinstance(response, JSONResponse):
			return response

		if not response:
			return make_response(
				logger=logger,
				status_code=status.HTTP_204_NO_CONTENT,
				message="No todos found",
				data={"todos": []}
			)

		return make_response(
			logger=logger,
			status_code=status.HTTP_200_OK,
			message="Retrieved todos successfully",
			data={
				"todos": [
					todo.model_dump(mode="json")
					for todo in response
				],
				"count": len(response)
			}
		)

	except Exception as error:
		return make_error_response(
			logger=logger,
			type=type(error).__name__,
			error=error
		)


@router.get(
	path="/{todo_id}/users/{user_id}",
	summary="Gets given ToDo ID for given user ID",
	response_model=dict[str, Any],
	status_code=status.HTTP_200_OK,
	responses=get_model_schema_for_docs(
		model=BaseResponse,
		responses={
			200: "Retrieved ToDo successfully",
			403: "Forbidden: User does not have access rights",
			404: "Not Found",
			500: "Internal Server Error"
		}
	)
)
async def get_todo(
	todo_id: Annotated[int, Path(gt=0)],
	user_id: Annotated[int, Path(gt=0)],
	service: ToDoService = Depends(get_service),
	current_user: UserPublic = Depends(get_current_active_user)
) -> JSONResponse:

	try:
		logger.info(f"Received request to get ToDo with ID: {todo_id} for user with ID: {user_id}")
		response: Optional[ToDo] | JSONResponse = await service.get(
			todo_id=todo_id,
			user_id=user_id,
			current_user=current_user
		)

		if isinstance(response, JSONResponse):
			return response

		if not response:
			return make_response(
				logger=logger,
				status_code=status.HTTP_404_NOT_FOUND,
				message="ToDo not found",
				data={"todo": None}
			)

		return make_response(
			logger=logger,
			status_code=status.HTTP_200_OK,
			message="Retrieved ToDo successfully",
			data={"todo": response.model_dump(mode="json")}
		)

	except Exception as error:
		return make_error_response(
			logger=logger,
			type=type(error).__name__,
			error=error
		)


@router.patch(
	path="/{todo_id}/users/{user_id}",
	summary="Updates given ToDo ID for given user ID",
	response_model=dict[str, Any],
	status_code=status.HTTP_201_CREATED,
	responses=get_model_schema_for_docs(
		model=BaseResponse,
		responses={
			201: "ToDo updated successfully",
			403: "Forbidden: User does not have access rights",
			404: "Not Found",
			500: "Internal Server Error"
		}
	)
)
async def patch_todo(
	todo_id: Annotated[int, Path(gt=0)],
	user_id: Annotated[int, Path(gt=0)],
	request: PatchTodoRequest,
	service: ToDoService = Depends(get_service),
	current_user: UserPublic = Depends(get_current_active_user)
) -> JSONResponse:

	try:
		logger.info(f"Received request to patch ToDo with ID: {todo_id} for user with ID: {user_id}")
		response: Optional[ToDo] | JSONResponse = await service.patch(
			todo_id=todo_id,
			todo_data=request,
			user_id=user_id,
			current_user=current_user
		)

		if isinstance(response, JSONResponse):
			return response

		if not response:
			return make_response(
				logger=logger,
				status_code=status.HTTP_404_NOT_FOUND,
				message="ToDo not found",
				data={"todo": None}
			)

		return make_response(
			logger=logger,
			status_code=status.HTTP_201_CREATED,
			message="ToDo updated successfully",
			data={"todo": response.model_dump(mode="json")}
		)

	except Exception as error:
		return make_error_response(
			logger=logger,
			type=type(error).__name__,
			error=error
		)


@router.delete(
	path="/{todo_id}/users/{user_id}",
	summary="Deletes given ToDo ID for given user ID",
	response_model=dict[str, Any],
	status_code=status.HTTP_201_CREATED,
	responses=get_model_schema_for_docs(
		model=BaseResponse,
		responses={
			200: "ToDo deleted successfully",
			403: "Forbidden: User does not have access rights",
			404: "Not Found",
			500: "Internal Server Error"
		}
	)
)
async def delete_todo(
	todo_id: Annotated[int, Path(gt=0)],
	user_id: Annotated[int, Path(gt=0)],
	service: ToDoService = Depends(get_service),
	current_user: UserPublic = Depends(get_current_active_user)
) -> JSONResponse:

	try:
		logger.info(f"Received request to delete ToDo with ID: {todo_id} for user with ID: {user_id}")
		response: Optional[ToDo] | JSONResponse = await service.delete(
			todo_id=todo_id,
			user_id=user_id,
			current_user=current_user
		)

		if isinstance(response, JSONResponse):
			return response

		if not response:
			return make_response(
				logger=logger,
				status_code=status.HTTP_404_NOT_FOUND,
				message="ToDo not found",
				data={"todo": None}
			)

		return make_response(
			logger=logger,
			status_code=status.HTTP_200_OK,
			message="ToDo deleted successfully",
			data={"id": todo_id}
		)

	except Exception as error:
		return make_error_response(
			logger=logger,
			type=type(error).__name__,
			error=error
		)
