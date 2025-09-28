from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from .. users.models import User


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
