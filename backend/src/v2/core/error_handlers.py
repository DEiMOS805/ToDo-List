from pydantic_core import ValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from jwt import InvalidTokenError, ExpiredSignatureError


###############################################################################
#################################### HTTP #####################################
###############################################################################
async def http_exception_handler(
	request: Request,
	exception: HTTPException
) -> JSONResponse:

	return JSONResponse(
		status_code=exception.status_code,
		content={"success": False, "message": exception.detail},
	)


###############################################################################
################################## Pydantic ###################################
###############################################################################
async def validation_exception_handler(
	request: Request,
	exception: ValidationError | RequestValidationError
) -> JSONResponse:

	return JSONResponse(
		status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		content={
			"success": False,
			"message": "Missing or invalid data",
			"details": list(map(
				lambda error: {
					"field": " -> ".join(str(loc) for loc in error["loc"]),
					"message": error["msg"],
					"error": error["type"],
					"input": error.get("input", None)
				},
				exception.errors()
			))
		},
	)


###############################################################################
##################################### JWT #####################################
###############################################################################
async def jwt_exception_handler(
	request: Request,
	exception: InvalidTokenError | ExpiredSignatureError
) -> JSONResponse:

	return JSONResponse(
		status_code=status.HTTP_401_UNAUTHORIZED,
		content={"success": False, "message": str(exception)},
	)
