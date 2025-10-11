from os import getenv
from logging import Logger
from dotenv import load_dotenv
from pydantic_core import ValidationError
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from .src.v2.core.config import *
from .src.v2.core.error_handlers import *
from .src.v2.core.database import db_config
from .src.v2.core.schemas import BaseResponse
from .src.v2.core.logging import setup_logging

from .src.v2.todos.router import router as todos_router
from .src.v2.users.router import router as users_router


###############################################################################
################################# Instances ###################################
###############################################################################
load_dotenv(DOTENV_ABSPATH)
logger: Logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
	# ON STARTUP
	logger.info("Verifying secret keys...")
	if not all([
		getenv("DB_URL", None),
		getenv("JWT_SECRET", None),
		getenv("JWT_ALGORITHM", None),
		getenv("FERNET_SECRET", None)
	]):
		raise ValueError("One or more required environment variables are missing")

	logger.info("Initializing database tables...")
	db_config.create_db_and_tables()
	logger.info("Database tables initialized successfully!")

	yield

	# ON SHUTDOWN

app = FastAPI(
	title="ToDo List Backend Service",
	summary="A backend service to manage ToDo Lists",
	version=APP_VERSION,
	lifespan=lifespan
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)


###############################################################################
############################### Route Handlers ################################
###############################################################################
app.include_router(router=todos_router)
app.include_router(router=users_router)


###############################################################################
############################### Error Handlers ################################
###############################################################################
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(InvalidTokenError, jwt_exception_handler)
app.add_exception_handler(ExpiredSignatureError, jwt_exception_handler)


###############################################################################
#################################### Root #####################################
###############################################################################
@app.get(path=PROJECT_PATHS_PREFIX)
async def root() -> JSONResponse:
	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content=BaseResponse(
			success=True,
			message="Welcome to ToDo-List backend service!",
			version=app.version
		).model_dump()
	)
