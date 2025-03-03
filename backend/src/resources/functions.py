from os import getenv
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from .config import DOTENV_ABSPATH


load_dotenv(DOTENV_ABSPATH)


def encrypt(string: str) -> bytes:
	encoded: bytes = string.encode()
	f: Fernet = Fernet(str(getenv("FERNET_SECRET")).encode())
	return f.encrypt(encoded)


def decrypt(bytes_str: bytes) -> str:
	f: Fernet = Fernet(str(getenv("FERNET_SECRET")).encode())
	decrypted: bytes = f.decrypt(bytes_str)
	return decrypted.decode()
