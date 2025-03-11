from pydantic import EmailStr, BaseModel
from sqlmodel import SQLModel, Field, Relationship


###############################################################################
################################### User ######################################
###############################################################################
class UserBase(SQLModel):
	username: str = Field(max_length=20)
	email: EmailStr = Field(max_length=50)
	disabled: bool = Field(default=False)
	is_admin: bool = Field(default=False)


class User(UserBase, table=True):
	__tablename__ = "users"

	id: int | None = Field(default=None, primary_key=True)
	password: bytes
	items: list["Item"] = Relationship(back_populates="users")


class UserPublic(UserBase):
	id: int = Field(gt=0)


class UserCreate(UserBase):
	model_config = {"extra": "forbid"}
	password: str = Field(max_length=20)


class UserUpdate(SQLModel):
	username: str | None = Field(default=None, max_length=20)
	email: EmailStr | None = Field(default=None, max_length=50)
	password: str | None = Field(default=None, max_length=20)
	disabled: bool | None = Field(default=None)
	is_admin: bool | None = Field(default=None)


###############################################################################
################################## To-Dos #####################################
###############################################################################
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


###############################################################################
################################## Token ######################################
###############################################################################
class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	username: str | None = None
	is_admin: bool | None = None
