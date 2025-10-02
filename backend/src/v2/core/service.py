from json import dumps
from typing import Any
from logging import Logger
from fastapi import status
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from .config import RESPONSE_INDENT
from .schemas import BaseResponse, ExceptionError


###############################################################################
#################################### Docs #####################################
###############################################################################
def get_model_schema_for_docs(
	model: BaseModel,
	responses: dict[int, str]
) -> dict[int, dict[str, Any]]:
	"""
	Utility function to get the JSON schema of a Pydantic response model for
	documentation purposes.

	Args:
		model: The Pydantic model class.
	Returns:
		dict: The JSON schema of the model.
	"""
	result: dict[int, dict[str, Any]] = {}
	example: dict[str, Any] = model.model_json_schema().get("properties", {})

	for status_code, description in responses.items():
		if status_code in [204, 304]:
			result[status_code] = {"description": description}
			continue

		result[status_code] = {
			"description": description,
			"model": model,
			"content": {
				"application/json": {
					"example": example
				}
			}
		}
	return result


###############################################################################
################################# Responses ###################################
###############################################################################
def make_response(
	logger: Logger,
	status_code: int,
	message: str,
	success: bool = True,
	error: dict[str, Any] | None = None,
	data: dict[str, Any] | None = None
) -> JSONResponse:
	"""
	Utility function to create a standardized response.

	Args:
		logger: The logger instance to log the error.
		status_code: The HTTP status code for the response.
		message: A custom message for the completed request.
		success: Whether the request was successful or not.

	Returns:
		dict: A dictionary representing the request response.
	"""

	response: dict[str, Any] = BaseResponse(
		success=success,
		message=message,
		data=data,
		error=ExceptionError(
			type=error.get("type", "UnknownError"),
			message=error.get("message", "An error occurred")
		) if error else None
	).model_dump()
	logger.info(f"Returning response: {dumps(response, indent=RESPONSE_INDENT)}")

	return JSONResponse(
		status_code=status_code,
		content=response
	)

def make_error_response(
	logger: Logger,
	type: str | Exception,
	error: str,
	message: str = "An error occurred while processing the request",
	status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> JSONResponse:
	"""
	Utility function to create a standardized error response.

	Args:
		logger: The logger instance to log the error.
		error: The exception that was raised.
		message: A custom message for the error response or
			the raised exception message.
		status_code: The HTTP status code for the response.

	Returns:
		dict: A dictionary representing the error response.
			Defaults to 500: Internal Server Error.
	"""
	logger.exception(f"{error}: {message}")
	response: dict[str, Any] = BaseResponse(
		success=False,
		message=message,
		error=ExceptionError(
			type=type,
			message=str(error)
		)
	).model_dump()
	logger.exception(f"Returning response: {dumps(response, indent=RESPONSE_INDENT)}")

	return JSONResponse(
		status_code=status_code,
		content=response
	)
