from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship


class UserBase(SQLModel):
	name: str = Field(max_length=20)
	email: EmailStr = Field(max_length=50)


class User(UserBase, table=True):
	__tablename__ = "users"

	id: int | None = Field(default=None, primary_key=True)
	password: bytes
	items: list["Item"] = Relationship(back_populates="users")


class UserPublic(UserBase):
	id: int = Field(gt=0)


class UserCreate(UserBase):
	password: str = Field(max_length=20)


class UserUpdate(SQLModel):
	name: str | None = Field(default=None, max_length=20)
	email: EmailStr | None = Field(default=None, max_length=50)
	password: str | None = Field(default=None, max_length=20)


class ItemBase(SQLModel):
	title: str = Field(max_length=20)
	description: str = Field(max_length=100)
	done: bool = Field(default=False)


class Item(ItemBase, table=True):
	__tablename__ = "items"

	id: int | None = Field(default=None, primary_key=True)
	user_id: int | None = Field(default=None, foreign_key="users.id")
	users: User | None = Relationship(back_populates="items")


class ItemUpdate(SQLModel):
	title: str | None = Field(default=None, max_length=20)
	description: str | None = Field(default=None, max_length=100)
	done: bool | None = False
