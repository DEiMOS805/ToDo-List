import hashlib
import secrets
from datetime import datetime
from typing import Optional, List
from abc import ABC, abstractmethod
from sqlmodel import Session, select
from logging import Logger, getLogger

from .models import User, UserCreate, UserPublic

from .. core.config import *


logger: Logger = getLogger(f"{LOGGING_PROJECT_NAME}.{__name__.split('.')[-1]}")



class RepositoryInterface(ABC):
	"""
	Repository interface following DDD principles.
	This defines the contract for user persistence operations.
	"""

	@abstractmethod
	async def create(self, user_data: UserCreate) -> UserPublic:
		pass

	@abstractmethod
	async def get_by_id(self, user_id: int) -> Optional[UserPublic]:
		pass

	@abstractmethod
	async def get_by_username(self, username: str) -> Optional[UserPublic]:
		pass

	@abstractmethod
	async def get_by_email(self, email: str) -> Optional[UserPublic]:
		pass

	@abstractmethod
	async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserPublic]:
		pass

	@abstractmethod
	async def update(self, user_id: int, user_data: dict) -> Optional[UserPublic]:
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


class SqlRepository(RepositoryInterface):
	"""
	SQLAlchemy implementation of RepositoryInterface.
	This is the infrastructure layer implementation.
	"""

	def __init__(self, session: Session) -> None:
		self.session: Session = session

	def _hash_password(self, password: str) -> str:
		salt: str = secrets.token_hex(16)
		password_hash: str = hashlib.sha256((password + salt).encode()).hexdigest()
		return f"{salt}${password_hash}"

	def _verify_password(self, password: str, hashed_password: str) -> bool:
		"""Verify password against stored hash"""
		try:
			salt, stored_hash = hashed_password.split('$', 1)
			password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
			return password_hash == stored_hash
		except ValueError:
			return False

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
		logger.debug(f"Creating user in DB")
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

	async def get_by_id(self, user_id: int) -> Optional[UserPublic]:
		"""Get user by ID"""
		statement = select(User).where(User.id == user_id)
		user = self.session.exec(statement).first()

		if user:
			return self._user_to_public(user)
		return None

	async def get_by_username(self, username: str) -> Optional[UserPublic]:
		"""Get user by username"""
		statement = select(User).where(User.username == username)
		user = self.session.exec(statement).first()

		if user:
			return self._user_to_public(user)
		return None

	async def get_by_email(self, email: str) -> Optional[UserPublic]:
		"""Get user by email"""
		statement = select(User).where(User.email == email)
		user = self.session.exec(statement).first()

		if user:
			return self._user_to_public(user)
		return None

	async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserPublic]:
		"""Get all users with pagination"""
		statement = select(User).offset(skip).limit(limit)
		users = self.session.exec(statement).all()

		return [self._user_to_public(user) for user in users]

	async def update(self, user_id: int, user_data: dict) -> Optional[UserPublic]:
		"""Update user"""
		statement = select(User).where(User.id == user_id)
		user = self.session.exec(statement).first()

		if not user:
			return None

		# Update fields
		for key, value in user_data.items():
			if hasattr(user, key) and key != 'id':
				setattr(user, key, value)

		user.updated_at = datetime.utcnow()

		self.session.add(user)
		self.session.commit()
		self.session.refresh(user)

		return self._user_to_public(user)

	async def delete(self, user_id: int) -> bool:
		"""Delete user"""
		statement = select(User).where(User.id == user_id)
		user = self.session.exec(statement).first()

		if not user:
			return False

		self.session.delete(user)
		self.session.commit()
		return True

	async def exists_by_username(self, username: str) -> bool:
		statement = select(User).where(User.username == username)
		user = self.session.exec(statement).first()
		return user is not None

	async def exists_by_email(self, email: str) -> bool:
		statement = select(User).where(User.email == email)
		user = self.session.exec(statement).first()
		return user is not None
