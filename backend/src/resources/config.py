from typing import Any

from os import getcwd
from os.path import join

###############################################################################
################################ Project paths ################################
###############################################################################
PROJECT_DIR_ABSPATH: str = getcwd()
SRC_ABS_PATH: str = join(PROJECT_DIR_ABSPATH, "src")
DB_DIR_PATH: str = join(SRC_ABS_PATH, "db")
DOTENV_ABSPATH: str = join(PROJECT_DIR_ABSPATH, ".env")

###############################################################################
########################### Database configuration ############################
###############################################################################
DB_FILENAME: str = "database.db"
DB_URL: str = f"sqlite:///{join(DB_DIR_PATH, DB_FILENAME)}"
DB_CONNECT_ARGS: dict[str, Any] = {"check_same_thread": False}

###############################################################################
############################ Security configuration ###########################
###############################################################################
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
