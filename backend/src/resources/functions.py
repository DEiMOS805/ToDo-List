from os import getenv
from jwt import encode
from typing import Any
from sqlmodel import select
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from datetime import datetime, timedelta, timezone

from src.resources.models import User
from src.resources.dependencies import SessionDep
from src.resources.config import DOTENV_ABSPATH, ALGORITHM


load_dotenv(DOTENV_ABSPATH)


###############################################################################
##################################### User ####################################
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
