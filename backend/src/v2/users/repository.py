from hashlib import sha256
from typing import Optional
from datetime import datetime
from secrets import token_hex
from sqlalchemy import Update
from abc import ABC, abstractmethod
from logging import Logger, getLogger
from sqlmodel import Session, select, update

from .config import *
from .models import User, UserCreate, UserPublic

from .. core.config import *


logger: Logger = getLogger(f"{LOGGING_PROJECT_NAME}.{'.'.join(__name__.split('.')[-2:])}")



class UserRepositoryInterface(ABC):
	"""
	Repository interface following DDD principles.
	This defines the contract for user persistence operations.
	"""

	@abstractmethod
	async def create(self, user_data: UserCreate) -> UserPublic:
		pass

	@abstractmethod
	async def get_all(self, skip: int = PAGINATION_OFFSET, limit: int = PAGINATION_LIMIT) -> list[Optional[UserPublic]]:
		pass

	@abstractmethod
	async def get(self, user_id: int) -> Optional[UserPublic]:
		pass

	@abstractmethod
	async def patch(self, user_id: int, user_data: dict) -> UserPublic:
		pass

	@abstractmethod
	async def delete(self, user_id: int) -> bool:
		pass

	@abstractmethod
	async def exists_by_username(self, username: str) -> bool:
		pass

	@abstractmethod
	async def exists_by_email(self, email: str) -> bool:
		pass


class UserSqlRepository(UserRepositoryInterface):
	"""
	SQLAlchemy implementation of UserRepositoryInterface.
	This is the infrastructure layer implementation.
	"""

	def __init__(self, session: Session) -> None:
		self.session: Session = session

	def _hash_password(self, password: str) -> str:
		salt: str = token_hex(16)
		password_hash: str = sha256((password + salt).encode()).hexdigest()
		return f"{salt}${password_hash}"

	async def _verify_password(self, password: str, hashed_password: str) -> bool:
		try:
			salt, stored_hash = hashed_password.split('$', 1)
			password_hash = sha256((password + salt).encode()).hexdigest()
			return password_hash == stored_hash
		except ValueError:
			return False

	async def exists_by_username(self, username: str) -> bool:
		statement = select(User).where(User.username == username)
		user = self.session.exec(statement).first()
		return user is not None

	async def exists_by_email(self, email: str) -> bool:
		statement = select(User).where(User.email == email)
		user = self.session.exec(statement).first()
		return user is not None

	def _user_to_public(self, user: User) -> UserPublic:
		return UserPublic(
			id=user.id,
			username=user.username,
			email=user.email,
			is_admin=user.is_admin,
			is_active=user.is_active,
			created_at=user.created_at,
			updated_at=user.updated_at
		)

	async def create(self, user_data: UserCreate) -> UserPublic:
		logger.info(f"Creating user in DB")
		hashed_password: str = self._hash_password(user_data.password)

		db_user = User(
			username=user_data.username,
			email=user_data.email,
			password_hash=hashed_password,
			is_admin=user_data.is_admin
		)

		self.session.add(db_user)
		self.session.commit()
		self.session.refresh(db_user)

		return self._user_to_public(db_user)

	async def get_all(
		self,
		offset: int = PAGINATION_OFFSET,
		limit: int = PAGINATION_LIMIT
	) -> list[Optional[UserPublic]]:

		logger.info(f"Retrieving all users from DB with offset={offset} and limit={limit}")
		statement = select(User).offset(offset).limit(limit)
		users = self.session.exec(statement).all()

		return [self._user_to_public(user) for user in users]

	async def get(self, user_id: int) -> Optional[UserPublic]:
		logger.info(f"Retrieving user with ID: {user_id} from DB")
		statement = select(User).where(User.id == user_id)
		user: Optional[User] = self.session.exec(statement).first()

		if user:
			return self._user_to_public(user)
		return None

	async def get_by_username(self, username: str) -> Optional[UserPublic]:
		logger.info(f"Retrieving user with username: {username} from DB")
		statement = select(User).where(User.username == username)
		user: Optional[User] = self.session.exec(statement).first()
		return user or None

	async def patch(self, user_id: int, user_data: dict[str, Any]) -> UserPublic:
		logger.info(f"Updating user with ID: {user_id} in DB")

		values: dict[str, Any] = {
			"updated_at": datetime.now(),
			**user_data
		}
		if "password" in user_data:
			values["password_hash"] = self._hash_password(user_data.pop("password"))

		statement: Update = update(User).where(User.id == user_id).values(**values)
		self.session.exec(statement)
		self.session.commit()

		statement = select(User).where(User.id == user_id)
		user: User = self.session.exec(statement).first()
		return self._user_to_public(user)

	async def delete(self, user_id: int) -> bool:
		logger.info(f"Deleting user with ID: {user_id} in DB")
		statement = select(User).where(User.id == user_id)
		user = self.session.exec(statement).first()

		if not user:
			return False

		self.session.delete(user)
		self.session.commit()
		return True
