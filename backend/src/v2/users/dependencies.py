from os import getenv
from jwt import decode
from sqlmodel import Session
from dotenv import load_dotenv
from typing import Any, Generator, Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from .service import UserService
from .models import UserPublic
from .repository import UserRepositoryInterface, UserSqlRepository

from ..core.database import db_config
from ..core.config import DOTENV_ABSPATH


load_dotenv(DOTENV_ABSPATH)


###############################################################################
################################### Database ##################################
###############################################################################
def get_db_session() -> Generator[Session, Any, None]:
	yield from db_config.get_session()


def get_repository(
	session: Session = Depends(get_db_session)
) -> UserRepositoryInterface:

	return UserSqlRepository(session)


def get_service(
	repository: UserRepositoryInterface = Depends(get_repository)
) -> UserService:

	return UserService(repository)


###############################################################################
############################### Authentication ################################
###############################################################################
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

async def get_current_active_user(
	service: UserService = Depends(get_service),
	token: str = Depends(oauth2_scheme)
) -> UserPublic:

	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	payload: dict[str, Any] = decode(
		token,
		str(getenv("JWT_SECRET")),
		algorithms=[str(getenv("JWT_ALGORITHM"))]
	)

	user_id: int = payload.get("id")
	if user_id is None:
		raise credentials_exception

	user: Optional[UserPublic] = await service.repository.get(user_id)
	if user is None:
		raise credentials_exception

	return user
