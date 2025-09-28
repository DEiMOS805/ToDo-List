from os import getcwd
from typing import Any
from os.path import join
from logging import DEBUG


###############################################################################
################################ Project paths ################################
###############################################################################
PROJECT_DIR_ABSPATH: str = getcwd()
DOTENV_ABSPATH: str = join(PROJECT_DIR_ABSPATH, ".env")
SRC_ABSPATH: str = join(PROJECT_DIR_ABSPATH, "src")
V1_ABSPATH: str = join(SRC_ABSPATH, "v1")
V2_ABSPATH: str = join(SRC_ABSPATH, "v2")
CORE_ABSPATH: str = join(SRC_ABSPATH, "core")
DB_DIR_PATH: str = join(CORE_ABSPATH, "db")


###############################################################################
#################################### Links ####################################
###############################################################################
PROJECT_PATHS_PREFIX: str = '/'


###############################################################################
################################## Variables ##################################
###############################################################################
# Formats
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

# Logging
LOGGING_PROJECT_NAME: str = "ToDo-List"
LOGGING_LEVEL: int = DEBUG
LOGGING_FORMAT: str = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"

# Database
DB_CONNECT_ARGS: dict[str, Any] = {"check_same_thread": False}

# Schemas
SCHEMAS_CONFIG: dict[str, Any] = {"extra": "forbid"}

# Responses
RESPONSE_INDENT: int = 4
