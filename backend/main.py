from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src import app
from src.routers import todos, users
from src.resources.error_handlers import http_exception_handler, integrity_error_handler


###############################################################################
############################### Route Handlers ################################
###############################################################################
app.include_router(router=todos.router, tags=["ToDos"])
app.include_router(router=users.router, prefix="/users", tags=["Users"])

###############################################################################
############################### Error Handlers ################################
###############################################################################
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)


@app.get("/")
async def root() -> dict[str, str]:
	return {"message": "Hello To-Do List!"}
