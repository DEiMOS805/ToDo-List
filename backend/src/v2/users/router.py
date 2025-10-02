from logging import Logger, getLogger
from fastapi.responses import JSONResponse
from typing import Any, Optional, Annotated
from fastapi import APIRouter, Query, Path, Body, status, Depends, HTTPException

from .config import *
from .schemas import *
from .service import Service
from .models import UserPublic
from .dependencies import get_service

from .. core.config import *
from .. core.schemas import *
from .. core.service import *


logger: Logger = getLogger(f"{LOGGING_PROJECT_NAME}.{__name__.split('.')[-1]}")
router = APIRouter(prefix=f"/{ROUTER_PREFIX}", tags=["Users"])


@router.post(
	path='/',
	summary="Creates a new user",
	response_model=dict[str, Any],
	status_code=status.HTTP_201_CREATED,
	responses=get_model_schema_for_docs(
		model=BaseResponse,
		responses={
			200: "Request completed successfully",
			201: "User created successfully",
			409: "Conflict: User already exists",
			422: "Unprocessable Entity: Validation Error",
			500: "Internal Server Error"
		}
	)
)
async def create_user(
	request: CreateUserRequest,
	service: Service = Depends(get_service)
) -> JSONResponse:
	try:
		logger.info("Received request to create user")
		response: UserPublic | JSONResponse = await service.create(request)

		if isinstance(response, JSONResponse):
			return response

		return make_response(
			logger=logger,
			status_code=status.HTTP_201_CREATED,
			message="User created successfully",
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
	summary="Gets all users",
	response_model=dict[str, Any],
	status_code=status.HTTP_200_OK,
	responses=get_model_schema_for_docs(
		model=BaseResponse,
		responses={
			200: "Retrieved users successfully",
			204: "No content: No users found",
			500: "Internal Server Error"
		}
	)
)
async def get_all_users(
	offset: Annotated[int, Query(ge=0)] = PAGINATION_OFFSET,
	limit: Annotated[int, Query(ge=1)] = PAGINATION_LIMIT,
	service: Service = Depends(get_service)
) -> JSONResponse:
	try:
		logger.info("Received request to get all users")
		response: list[Optional[UserPublic]] | JSONResponse = await service.get_all(
			offset=offset,
			limit=limit
		)

		if isinstance(response, JSONResponse):
			return response

		if not response:
			return make_response(
				logger=logger,
				status_code=status.HTTP_204_NO_CONTENT,
				message="No users found",
				data={"users": []}
			)

		return make_response(
			logger=logger,
			status_code=status.HTTP_200_OK,
			message="Retrieved users successfully",
			data={
				"users": [
					user.model_dump(mode="json")
					for user in response
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
	path="/{id}",
	summary="Gets user by ID",
	response_model=dict[str, Any],
	status_code=status.HTTP_200_OK,
	responses=get_model_schema_for_docs(
		model=BaseResponse,
		responses={
			200: "User retrieved successfully",
			404: "User not found",
			422: "Unprocessable Entity: Validation Error",
			500: "Internal Server Error"
		}
	)
)
async def get_user(
	id: Annotated[int, Path(gt=0)],
	service: Service = Depends(get_service)
) -> JSONResponse:

	try:
		logger.info(f"Received request to get user by ID: {id}")
		response: UserPublic | JSONResponse = await service.get(id)

		if isinstance(response, JSONResponse):
			return response

		return JSONResponse(
			status_code=status.HTTP_200_OK,
			content=BaseResponse(
				message="User retrieved successfully!",
				data=response.model_dump(mode="json")
			).model_dump()
		)

	except HTTPException as http_error:
		raise http_error

	except Exception as error:
		return make_error_response(
			logger=logger,
			type=type(error).__name__,
			error=error
		)


@router.patch(
	path="/{id}",
	summary="Updates user by ID",
	response_model=dict[str, Any],
	status_code=status.HTTP_200_OK,
	responses=get_model_schema_for_docs(
		model=BaseResponse,
		responses={
			200: "User updated successfully",
			404: "User not found",
			422: "Unprocessable Entity: Validation Error",
			500: "Internal Server Error"
		}
	)
)
async def patch_user(
	id: Annotated[int, Path(gt=0)],
	request: PatchUserRequest,
	service: Service = Depends(get_service)
) -> JSONResponse:

	try:
		logger.info(f"Received request to update user with ID: {id}")
		response: UserPublic | JSONResponse = await service.patch(id, request)

		if isinstance(response, JSONResponse):
			return response

		return JSONResponse(
			status_code=status.HTTP_200_OK,
			content=BaseResponse(
				message="User updated successfully!",
				data=response.model_dump(mode="json")
			).model_dump()
		)

	except Exception as error:
		return make_error_response(
			logger=logger,
			type=type(error).__name__,
			error=error
		)


@router.delete(
	path="/{id}",
	summary="Deletes user by ID",
	response_model=dict[str, Any],
	status_code=status.HTTP_200_OK,
	responses=get_model_schema_for_docs(
		model=BaseResponse,
		responses={
			200: "User updated successfully",
			404: "User not found",
			422: "Unprocessable Entity: Validation Error",
			500: "Internal Server Error"
		}
	)
)
async def delete_user(
	id: Annotated[int, Path(gt=0)],
	service: Service = Depends(get_service)
) -> JSONResponse:

	try:
		logger.info(f"Received request to delete user with ID: {id}")
		response: bool | JSONResponse = await service.delete(id)

		if isinstance(response, JSONResponse):
			return response

		return JSONResponse(
			status_code=status.HTTP_200_OK,
			content=BaseResponse(
				message="User deleted successfully!",
				data={"id": id}
			).model_dump()
		)

	except Exception as error:
		return make_error_response(
			logger=logger,
			type=type(error).__name__,
			error=error
		)
