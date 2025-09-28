from typing import Any
from logging import Logger, getLogger
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse

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
	user_request: CreateUserRequest,
	service: Service = Depends(get_service)
) -> JSONResponse:
	try:
		logger.info("Received request to create user")
		user_response: UserPublic | JSONResponse = await service.create_user(user_request)

		if isinstance(user_response, JSONResponse):
			return user_response

		return make_response(
			logger=logger,
			status_code=status.HTTP_201_CREATED,
			message="User created successfully",
			data=user_response.model_dump(mode="json")
		)

	except Exception as error:
		return make_error_response(
			logger=logger,
			type=type(error).__name__,
			error=error
		)


# @router.get(
# 	path='/{user_id}',
# 	summary="Get user by ID",
# 	response_model=dict[str, Any],
# 	responses=get_model_schema_for_docs(
# 		model=BaseResponse,
# 		responses={
# 			200: "User retrieved successfully",
# 			404: "User not found",
# 			500: "Internal Server Error"
# 		}
# 	)
# )
# async def get_user_by_id_endpoint(
# 	user_id: int,
# 	user_service: Service = Depends(get_user_service)
# ):
# 	"""Get user by ID endpoint"""
# 	try:
# 		user_response = await user_service.get_user_by_id(user_id)
# 		return JSONResponse(
# 			status_code=status.HTTP_200_OK,
# 			content=BaseResponse(
# 				message="User retrieved successfully!",
# 				data=user_response.model_dump()
# 			).model_dump()
# 		)

# 	except HTTPException as http_error:
# 		raise http_error
	
# 	except Exception as error:
# 		return make_error_response(
# 			logger=logger,
# 			type=type(error).__name__,
# 			error=error
# 		)


# @router.get(
# 	path='/',
# 	summary="Get all users",
# 	response_model=dict[str, Any],
# 	responses=get_model_schema_for_docs(
# 		model=BaseResponse,
# 		responses={
# 			200: "Users retrieved successfully",
# 			500: "Internal Server Error"
# 		}
# 	)
# )
# async def get_all_users_endpoint(
# 	skip: int = 0,
# 	limit: int = 100,
# 	user_service: UserService = Depends(get_user_service)
# ):
# 	"""Get all users with pagination endpoint"""
# 	try:
# 		users = await user_service.get_all_users(skip=skip, limit=limit)
# 		return JSONResponse(
# 			status_code=status.HTTP_200_OK,
# 			content=BaseResponse(
# 				message="Users retrieved successfully!",
# 				data=[user.model_dump() for user in users]
# 			).model_dump()
# 		)

# 	except Exception as error:
# 		return make_error_response(
# 			logger=logger,
# 			type=type(error).__name__,
# 			error=error
# 		)
