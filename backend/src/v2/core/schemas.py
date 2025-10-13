from typing import Any
from pydantic import BaseModel, Field

from .config import APP_VERSION


class ExceptionError(BaseModel):
	type: str = Field(min_length=1, max_length=16, description="The type of Exception")
	message: str = Field(min_length=1, max_length=512, description="A message describing the error")


class BaseResponse(BaseModel):
	success: bool = Field(default=True, description="Indicates if the request was successful")
	message: str = Field(min_length=1, max_length=100, description="A message providing additional information about the response")
	data: dict[str, Any] | None = Field(default=None, description="The data returned by the request, if any")
	error: ExceptionError | None = Field(default=None, description="Error dictionary if the request failed")
	version: str = Field(default=APP_VERSION, description="API version")
