from typing import TextIO
from pytz import timezone
from datetime import datetime
from logging import Formatter, LogRecord, Logger, getLogger, StreamHandler

from .config import *


class TZFormatter(Formatter):
	def __init__(
		self,
		fmt: str | None = None,
		datefmt: str | None = None,
		tz: str = "America/Mexico_City"
	) -> None:

		super().__init__(fmt=fmt, datefmt=datefmt)
		self.tz = timezone(tz)

	def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str:
		dt: datetime = datetime.fromtimestamp(record.created, self.tz)
		return dt.strftime(datefmt) if datefmt else dt.isoformat()


def setup_logging() -> Logger:
	logger: Logger = getLogger(LOGGING_PROJECT_NAME)
	logger.setLevel(LOGGING_LEVEL)

	handler: StreamHandler[TextIO] = StreamHandler()
	formatter = TZFormatter(fmt=LOGGING_FORMAT, datefmt=DATETIME_FORMAT)
	handler.setFormatter(formatter)

	# Avoid adding multiple handlers if the logger is imported multiple times
	if not logger.hasHandlers():
		logger.addHandler(handler)

	return logger
