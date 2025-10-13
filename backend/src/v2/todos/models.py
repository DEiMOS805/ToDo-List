from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from .. users.models import User


class ToDoBase(SQLModel):
	description: str = Field(max_length=100)
	done: bool = Field(default=False)
	is_favorite: bool = Field(default=False)
	remind_at: Optional[datetime] = Field(default=None)
	expired_at: Optional[datetime] = Field(default=None)


class ToDo(ToDoBase, table=True):
	__tablename__ = "todos"

	id: Optional[int] = Field(default=None, primary_key=True)
	user_id: Optional[int] = Field(default=None, foreign_key="users.id")
	created_at: datetime = Field(default_factory=datetime.now)
	updated_at: datetime = Field(default_factory=datetime.now)

	users: Optional[User] = Relationship(back_populates="todos")
