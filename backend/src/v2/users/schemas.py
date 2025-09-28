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


###############################################################################
################################# Responses ###################################
###############################################################################
