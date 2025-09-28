from os import getenv
from typing import Annotated
from dotenv import load_dotenv
from sqlmodel import Session, select
from jwt import decode, InvalidTokenError
from fastapi import Depends, HTTPException, status

from src import oauth2_scheme
from src.db.db import get_session
from src.resources.models import User
from src.resources.config import DOTENV_ABSPATH, ALGORITHM


load_dotenv(DOTENV_ABSPATH)


###############################################################################
################################### Database ##################################
###############################################################################
SessionDep = Annotated[Session, Depends(get_session)]


###############################################################################
##################################### Auth ####################################
###############################################################################
async def get_current_user(
	session: SessionDep,
	token: Annotated[str, Depends(oauth2_scheme)]
) -> User:

	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	try:
		payload = decode(
			token,
			str(getenv("JWT_SECRET")),
			algorithms=[ALGORITHM]
		)

		username = payload.get("sub")
		if username is None:
			raise credentials_exception

	except InvalidTokenError:
		raise credentials_exception

	user: User | None = session.exec(
        select(User).where(User.username == username)
    ).first()
	if user is None:
		raise credentials_exception

	return user


async def get_current_active_user(
	current_user: Annotated[User, Depends(get_current_user)]
) -> User:

	if current_user.disabled:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Inactive user"
		)

	return current_user
