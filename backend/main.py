from fastapi import HTTPException

from src import app
from src.routers import items, users
from src.resources.error_handlers import http_exception_handler


############################### Route Handlers ################################
app.include_router(router=items.router, tags=["Items"])
app.include_router(router=users.router, prefix="/users", tags=["Users"])

############################### Error Handlers ################################
app.add_exception_handler(HTTPException, http_exception_handler)


@app.get("/")
async def root() -> dict[str, str]:
	return {"message": "Hello To-Do List!"}
