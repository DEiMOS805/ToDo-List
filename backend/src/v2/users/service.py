from logging import Logger, getLogger
from fastapi import HTTPException, status

from .schemas import CreateUserRequest
from .models import UserCreate, UserPublic
from .repository import RepositoryInterface

from ..core.config import *
from ..core.service import *


logger: Logger = getLogger(f"{LOGGING_PROJECT_NAME}.{__name__.split('.')[-1]}")


class Service:
	def __init__(self, repository: RepositoryInterface) -> None:
		self.repository: RepositoryInterface = repository

	async def create_user(
		self,
		user_request: CreateUserRequest
	) -> UserPublic | JSONResponse:
		"""
		Create a new user with business logic validation.
		This is the application service that orchestrates domain operations.
		"""
		logger.info(
			"Creating user: "
			f"username={user_request.username}, email={user_request.email}"
		)

		# Business rule: Check if user already exists by username
		if await self.repository.exists_by_username(user_request.username):
			logger.warning(f"User creation failed: Username '{user_request.username}' already exists")
			return make_response(
				logger=logger,
				success=False,
				status_code=status.HTTP_409_CONFLICT,
				message=f"User {user_request.username} already exists",
			)

		# Business rule: Check if user already exists by email
		if await self.repository.exists_by_email(user_request.email):
			logger.warning(f"User creation failed: Email '{user_request.email}' already exists")
			return make_response(
				logger=logger,
				success=False,
				status_code=status.HTTP_409_CONFLICT,
				message=f"Email {user_request.email} already exists"
			)

		user: UserCreate = UserCreate(
			username=user_request.username,
			email=user_request.email,
			password=user_request.password,
			is_admin=user_request.is_admin
		)

		try:
			response: UserPublic = await self.repository.create(user)
			logger.info(f"User created successfully with ID: {response.id}")
			return response

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=error
			)

	# async def get_user_by_id(self, user_id: int) -> UserResponse | None:
	# 	"""Get user by ID"""
	# 	logger.info(f"Retrieving user with ID: {user_id}")

	# 	try:
	# 		user = await self.repository.get_by_id(user_id)
	# 		if not user:
	# 			logger.warning(f"User with ID {user_id} not found")
	# 			raise HTTPException(
	# 				status_code=status.HTTP_404_NOT_FOUND,
	# 				detail=f"User with ID {user_id} not found"
	# 			)

	# 		logger.info(f"User retrieved successfully: {user.username}")
	# 		return user

	# 	except HTTPException:
	# 		raise
	# 	except Exception as error:
	# 		logger.exception(f"Exception retrieving user: {error}")
	# 		raise HTTPException(
	# 			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
	# 			detail="Internal server error while retrieving user"
	# 		)

	# async def get_user_by_username(self, username: str) -> UserResponse | None:
	# 	"""Get user by username"""
	# 	logger.info(f"Retrieving user with username: {username}")

	# 	try:
	# 		user = await self.repository.get_by_username(username)
	# 		if not user:
	# 			logger.warning(f"User with username '{username}' not found")
	# 			raise HTTPException(
	# 				status_code=status.HTTP_404_NOT_FOUND,
	# 				detail=f"User with username '{username}' not found"
	# 			)

	# 		logger.info(f"User retrieved successfully: {user.username}")
	# 		return user

	# 	except HTTPException:
	# 		raise
	# 	except Exception as error:
	# 		logger.exception(f"Exception retrieving user: {error}")
	# 		raise HTTPException(
	# 			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
	# 			detail="Internal server error while retrieving user"
	# 		)

	# async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[UserResponse]:
	# 	"""Get all users with pagination"""
	# 	logger.info(f"Retrieving users with skip={skip}, limit={limit}")

	# 	try:
	# 		users = await self.repository.get_all(skip=skip, limit=limit)
	# 		logger.info(f"Retrieved {len(users)} users")
	# 		return users

	# 	except Exception as error:
	# 		logger.exception(f"Exception retrieving users: {error}")
	# 		raise HTTPException(
	# 			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
	# 			detail="Internal server error while retrieving users"
	# 		)
