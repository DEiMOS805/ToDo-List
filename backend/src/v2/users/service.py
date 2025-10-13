from os import getenv
from jwt import encode
from fastapi import status
from typing import Optional
from dotenv import load_dotenv
from logging import Logger, getLogger
from datetime import datetime, timedelta

from .models import UserCreate, UserPublic
from .repository import UserRepositoryInterface
from .schemas import CreateUserRequest, AuthUserResponse

from .config import *

from ..core.config import *
from ..core.service import *


load_dotenv(DOTENV_ABSPATH)
logger: Logger = getLogger(f"{LOGGING_PROJECT_NAME}.{'.'.join(__name__.split('.')[-2:])}")


class UserService:
	def __init__(self, repository: UserRepositoryInterface) -> None:
		self.repository: UserRepositoryInterface = repository

	async def create_access_token(self, user_data: dict) -> AuthUserResponse:
		logger.info("Creating access token")
		to_encode: dict[str, Any] = user_data.copy()

		token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
		expire: datetime = datetime.now() + token_expire
		to_encode.update({"exp": expire})

		encoded_jwt: str = encode(
			payload=to_encode,
			key=str(getenv("JWT_SECRET")),
			algorithm=str(getenv("JWT_ALGORITHM"))
		)
		response: AuthUserResponse = AuthUserResponse(access_token=encoded_jwt)
		logger.debug(f"Access token created successfully: {response.model_dump()}")
		return response

	async def create(self, user_request: CreateUserRequest) -> UserPublic | JSONResponse:
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
				message=f"User with email {user_request.email} already exists"
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
				error=f"Internal server error while creating user: {error}"
			)

	async def auth(self, username: str, password: str) -> AuthUserResponse | JSONResponse:
		try:
			user: Optional[UserPublic] = await self.repository.get_by_username(username)
			if not user:
				logger.warning(f"User {username} not found")
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_404_NOT_FOUND,
					message=f"User {username} not found",
				)

			if not await self.repository._verify_password(password, user.password_hash):
				logger.warning(f"Authentication failed for user {username}: Incorrect password")
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_401_UNAUTHORIZED,
					message="Incorrect username or password",
				)

			auth: AuthUserResponse = await self.create_access_token(
				user_data={
					"id": user.id
				}
			)
			logger.info(f"User {username} authenticated successfully")
			return auth

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=f"Internal server error while updating user with id {id}: {error}"
			)

	async def get_all(
		self,
		current_user: UserPublic,
		offset: int = PAGINATION_OFFSET,
		limit: int = PAGINATION_LIMIT
	) -> list[UserPublic] | JSONResponse:
		"""Get all users with pagination: offset and limit"""
		logger.info(f"Retrieving users with offset={offset}, limit={limit}")

		# Business rule: Check if user is admin
		user: Optional[UserPublic] = await self.repository.get(current_user.id)
		if not user.is_admin:
			logger.error(f"User with ID {id} is not an admin")
			return make_response(
				logger=logger,
				success=False,
				status_code=status.HTTP_403_FORBIDDEN,
				message=f"Given user does not have the necessary rights for this operation",
			)

		try:
			users: list[UserPublic] = await self.repository.get_all(
				offset=offset,
				limit=limit
			)
			logger.info(f"Retrieved {len(users)} users")
			return users

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=f"Internal server error while retrieving users: {error}"
			)

	async def get(self, current_user: UserPublic, user_id: int) -> Optional[UserPublic]:
		logger.info(f"Retrieving user with ID: {user_id}")

		try:
			# Business rule: Check if current user is trying to access their own data or is admin
			if not current_user.is_admin and current_user.id != user_id:
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_403_FORBIDDEN,
					message=f"Given user does not have the necessary rights for this operation",
				)

			user: Optional[UserPublic] = await self.repository.get(user_id)
			if not user:
				logger.warning(f"User with ID {user_id} not found")
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_404_NOT_FOUND,
					message=f"User with ID {user_id} not found",
				)

			logger.info(f"User with ID {user_id} retrieved successfully: {user.username}")
			return user

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=f"Internal server error while retrieving user with id {user_id}: {error}"
			)

	async def patch(
		self,
		current_user: UserPublic,
		user_id: int,
		user_data: dict[str, Any]
	) -> Optional[UserPublic]:
		logger.info(f"Updating user with ID: {user_id}")

		try:
			# Business rule: Check if current user is trying to access their own data or is admin
			if not current_user.is_admin and current_user.id != user_id:
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_403_FORBIDDEN,
					message=f"Given user does not have the necessary rights for this operation",
				)

			# Business rule: Check if user already exists by email
			if await self.repository.exists_by_email(user_data.email):
				logger.warning(f"User creation failed: Email '{user_data.email}' already exists")
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_409_CONFLICT,
					message=f"User with email {user_data.email} already exists"
				)

			user: Optional[UserPublic] = await self.repository.get(user_id)
			if not user:
				logger.warning(f"User with ID {user_id} not found")
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_404_NOT_FOUND,
					message=f"User with ID {user_id} not found",
				)

			user_data: dict[str, Any] = user_data.model_dump(exclude_unset=True)
			user: Optional[UserPublic] = await self.repository.patch(user_id, user_data)

			logger.info(f"User with ID {user_id} updated successfully: {user.username}")
			return user

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=f"Internal server error while updating user with id {user_id}: {error}"
			)

	async def delete(self, current_user: UserPublic, user_id: int) -> bool | JSONResponse:
		logger.info(f"Deleting user with ID: {user_id}")

		try:
			# Business rule: Check if current user is trying to access their own data or is admin
			if not current_user.is_admin and current_user.id != user_id:
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_403_FORBIDDEN,
					message=f"Given user does not have the necessary rights for this operation",
				)

			user: Optional[UserPublic] = await self.repository.get(user_id)
			if not user:
				logger.warning(f"User with ID {user_id} not found")
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_404_NOT_FOUND,
					message=f"User with ID {user_id} not found",
				)

			result: bool = await self.repository.delete(user_id)
			if not result:
				logger.error(f"Failed to delete user with ID {user_id}")
				return make_response(
					logger=logger,
					success=False,
					status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
					message=f"Failed to delete user with ID {user_id}",
				)

			logger.info(f"User with ID {user_id} deleted successfully")
			return True

		except Exception as error:
			return make_error_response(
				logger=logger,
				type=type(error).__name__,
				error=f"Internal server error while updating user with id {user_id}: {error}"
			)
