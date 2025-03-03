from typing import Annotated
from sqlmodel import Session
from fastapi import Depends, HTTPException, status

from ..db.db import get_session


SessionDep = Annotated[Session, Depends(get_session)]


# async def verify_item_id(item_id: int) -> int:
# 	if not (1 <= item_id <= len(fake_items)):
# 		raise HTTPException(
# 			status_code=status.HTTP_404_NOT_FOUND,
# 			detail=f"Item with id {item_id} not found!"
# 		)

# 	return item_id


# async def verify_user_id(user_id: int) -> int:
# 	if not (1 <= user_id <= len(fake_users)):
# 		raise HTTPException(
# 			status_code=status.HTTP_404_NOT_FOUND,
# 			detail=f"User with id {user_id} not found!"
# 		)

# 	return user_id
