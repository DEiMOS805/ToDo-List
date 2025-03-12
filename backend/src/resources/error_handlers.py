from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


###############################################################################
#################################### HTTP #####################################
###############################################################################
async def http_exception_handler(
	request: Request,
	exception: HTTPException
) -> JSONResponse:

	return JSONResponse(
		status_code=exception.status_code,
		content={"status": "Failed", "message": exception.detail},
	)


###############################################################################
################################### Database ##################################
###############################################################################
async def integrity_error_handler(
	request: Request,
	exception: IntegrityError
) -> JSONResponse:

	message = str(exception.orig)
	if "email" in message:
		message = (
			"The email address you entered is already in use. "
			"Please use a different email."
		)

	return JSONResponse(
		status_code=400,
		content={"status": "Failed", "message": message},
	)
