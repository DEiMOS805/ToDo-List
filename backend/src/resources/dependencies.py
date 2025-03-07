from fastapi import Depends
from typing import Annotated
from sqlmodel import Session

from ..db.db import get_session


SessionDep = Annotated[Session, Depends(get_session)]
