from typing import Optional
from datetime import datetime
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship


class UserBase(SQLModel):
	username: str = Field(max_length=32)
	email: EmailStr = Field(max_length=64, unique=True)
	is_active: bool = Field(default=True)
	is_admin: bool = Field(default=False)


class UserCreate(UserBase):
	password: str = Field(min_length=8, max_length=64)


class User(UserBase, table=True):
	__tablename__ = "users"

	id: Optional[int] = Field(default=None, primary_key=True)
	password_hash: str = Field(max_length=255)
	created_at: datetime = Field(default_factory=datetime.now)
	updated_at: datetime = Field(default_factory=datetime.now)

	todos: list["ToDo"] = Relationship(back_populates="users")


class UserPublic(UserBase):
	id: int = Field(gt=0)
	created_at: datetime
	updated_at: datetime
