from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr

from .. core.config import SCHEMAS_CONFIG


###############################################################################
################################## Requests ###################################
###############################################################################
class CreateUserRequest(BaseModel):
	model_config: ConfigDict = SCHEMAS_CONFIG

	username: str = Field(min_length=1, max_length=64)
	email: EmailStr = Field(max_length=64)
	password: str = Field(min_length=8, max_length=64)
	is_admin: bool = Field(default=False)


class PatchUserRequest(BaseModel):
	model_config: ConfigDict = SCHEMAS_CONFIG

	username: Optional[str] = Field(default=None, max_length=64)
	email: Optional[EmailStr] = Field(default=None, max_length=64)
	password: Optional[str] = Field(default=None, max_length=64)
	is_admin: Optional[bool] = Field(default=None)
	is_active: Optional[bool] = Field(default=None)


###############################################################################
################################# Responses ###################################
###############################################################################
class AuthUserResponse(BaseModel):
	access_token: str
	token_type: str = Field(default="Bearer")
