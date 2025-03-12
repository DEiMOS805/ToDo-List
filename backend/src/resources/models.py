from datetime import datetime
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship


###############################################################################
################################### User ######################################
###############################################################################
class UserBase(SQLModel):
	username: str = Field(max_length=20)
	email: EmailStr = Field(max_length=50, unique=True)
	disabled: bool = Field(default=False)
	is_admin: bool = Field(default=False)


class User(UserBase, table=True):
	__tablename__ = "users"

	id: int | None = Field(default=None, primary_key=True)
	password: bytes
	write_datetime: datetime = Field(default_factory=datetime.now)
	creation_datetime: datetime = Field(default_factory=datetime.now)

	todos: list["ToDo"] = Relationship(back_populates="users")


class UserPublic(UserBase):
	id: int = Field(gt=0)
	write_datetime: str
	creation_datetime: str


class UserCreate(UserBase):
	model_config = {"extra": "forbid"}

	password: str = Field(max_length=20)


class UserUpdate(SQLModel):
	username: str | None = Field(default=None, max_length=20)
	email: EmailStr | None = Field(default=None, max_length=50, unique=True)
	password: str | None = Field(default=None, max_length=20)
	disabled: bool | None = Field(default=None)
	is_admin: bool | None = Field(default=None)


###############################################################################
################################## To-Dos #####################################
###############################################################################
class ToDoBase(SQLModel):
	description: str = Field(max_length=100)
	done: bool = Field(default=False)
	is_favorite: bool = Field(default=False)


class ToDo(ToDoBase, table=True):
	__tablename__ = "todos"

	id: int | None = Field(default=None, primary_key=True)
	user_id: int | None = Field(default=None, foreign_key="users.id")
	reminder_datetime: datetime | None = Field(default=None, nullable=True)
	expiration_datetime: datetime | None = Field(default=None, nullable=True)
	write_datetime: datetime = Field(default_factory=datetime.now)
	creation_datetime: datetime = Field(default_factory=datetime.now)

	users: User | None = Relationship(back_populates="todos")


class ToDoCreate(ToDoBase):
	model_config = {"extra": "forbid"}

	reminder_datetime: str | None = Field(default=None)
	expiration_datetime: str | None = Field(default=None)


class ToDoUpdate(SQLModel):
	description: str | None = Field(default=None, max_length=100)
	done: bool | None = False
	is_favorite: bool | None = False
	reminder_datetime: str | None = None
	expiration_datetime: str | None = None
