from os import getenv
from jwt import encode
from sqlmodel import select
from dotenv import load_dotenv
from typing import Any, Sequence
from cryptography.fernet import Fernet
from datetime import datetime, timedelta, timezone

from src.resources.models import User, ToDo
from src.resources.dependencies import SessionDep
from src.resources.config import DOTENV_ABSPATH, ALGORITHM


load_dotenv(DOTENV_ABSPATH)


###############################################################################
#################################### Users ####################################
###############################################################################
def encrypt(string: str) -> bytes:
	encoded: bytes = string.encode()
	f: Fernet = Fernet(str(getenv("FERNET_SECRET")).encode())
	return f.encrypt(encoded)


def decrypt(bytes_str: bytes) -> str:
	f: Fernet = Fernet(str(getenv("FERNET_SECRET")).encode())
	decrypted: bytes = f.decrypt(bytes_str)
	return decrypted.decode()


def verify_password(password: str, hashed_password: bytes) -> bool:
    return password == decrypt(hashed_password)


def authenticate_user(
    session: SessionDep,
    username: str,
    password: str
) -> User | bool:

    user: User | None = session.exec(
        select(User).where(User.username == username)
    ).first()

    if not user:
        return False
    if not verify_password(password, user.password):
        return False

    return user


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None
) -> str:

    to_encode: dict[str, Any] = data.copy()

    if expires_delta:
        expire: datetime = datetime.now(timezone.utc) + expires_delta
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    return encode(to_encode, str(getenv("JWT_SECRET")), algorithm=ALGORITHM)


###############################################################################
################################## To-Dos #####################################
###############################################################################
def format_todo_response(todo: ToDo) -> dict[str, Any]:
    return {
        **todo.model_dump(),
        "reminder_datetime": (
            todo.reminder_datetime.isoformat()
            if todo.reminder_datetime else None
        ),
        "expiration_datetime": (
            todo.expiration_datetime.isoformat()
            if todo.expiration_datetime
            else None
        ),
        "write_datetime": todo.write_datetime.isoformat(),
        "creation_datetime": todo.creation_datetime.isoformat(),
    }


def map_todo_list(todo_list: Sequence[ToDo]) -> list[dict[str, Any]]:
    return list(
		map(
			lambda todo: {
				**todo.model_dump(),
				"reminder_datetime": (
					todo.reminder_datetime.isoformat()
					if todo.reminder_datetime
					else None
				),
				"expiration_datetime": (
					todo.expiration_datetime.isoformat()
					if todo.expiration_datetime
					else None
				),
				"write_datetime": todo.write_datetime.isoformat(),
				"creation_datetime": todo.creation_datetime.isoformat(),
			},
			todo_list
		)
	)
