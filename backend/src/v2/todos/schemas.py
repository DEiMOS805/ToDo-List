from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from .. core.config import SCHEMAS_CONFIG


###############################################################################
################################## Requests ###################################
###############################################################################
class CreateTodoRequest(BaseModel):
	model_config: ConfigDict = SCHEMAS_CONFIG

	description: str = Field(max_length=100)
	done: bool = Field(default=False)
	is_favorite: Optional[bool] = Field(default=False)
	remind_at: Optional[str] = Field(default=None)
	expired_at: Optional[str] = Field(default=None)


class PatchTodoRequest(BaseModel):
	model_config: ConfigDict = SCHEMAS_CONFIG

	description: Optional[str] = Field(default=None, max_length=100)
	done: Optional[bool] = Field(default=None)
	is_favorite: Optional[bool] = Field(default=None)
	remind_at: Optional[str] = Field(default=None)
	expired_at: Optional[str] = Field(default=None)
