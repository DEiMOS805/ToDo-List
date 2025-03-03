from sqlmodel import select
from typing import Any, Annotated
from fastapi.responses import JSONResponse, Response
from fastapi import APIRouter, Path, Query, Body, HTTPException, status

from ..resources.functions import encrypt
from ..resources.dependencies import SessionDep
from ..resources.models import User, UserPublic, UserCreate, UserUpdate


router = APIRouter()


@router.get("/", response_model=dict[str, Any])
async def get_users(
	session: SessionDep,
	offset: Annotated[int, Query(ge=0)] = 0,
	limit: Annotated[int, Query(ge=1)] = 10
) -> Response | JSONResponse:

	users = session.exec(select(User).offset(offset).limit(limit)).all()
	if not users:
		return Response(status_code=status.HTTP_204_NO_CONTENT)

	users = list(map(lambda user: UserPublic(**user.model_dump()).model_dump(), users))

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "Items retrieved successfully!",
			"items": users,
		}
	)


@router.post("/", response_model=dict[str, Any])
async def create_user(user: UserCreate, session: SessionDep) -> JSONResponse:
	user_db: User = User.model_validate(user)

	encrypted_pwd: bytes = encrypt(user.password)
	user_db.password = encrypted_pwd

	session.add(user_db)
	session.commit()
	session.refresh(user_db)

	return JSONResponse(
		status_code=status.HTTP_201_CREATED,
		content={
			"status": "Success",
			"message": "User created successfully!",
			"user": UserPublic(**user_db.model_dump()).model_dump()
		}
	)


@router.get("/{user_id}", response_model=dict[str, Any])
async def get_user(
	user_id: Annotated[int, Path(gt=0)],
	session: SessionDep
) -> JSONResponse:

	user: User | None = session.get(User, user_id)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"User with id {user_id} not found!"
		)

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "User retrieved successfully!",
			"user": UserPublic(**user.model_dump()).model_dump()
		}
	)


@router.patch("/{user_id}", response_model=dict[str, Any])
async def patch_user(
	user_id: Annotated[int, Path(gt=0)],
	user: Annotated[UserUpdate, Body()],
	session: SessionDep
) -> JSONResponse:

	user_db: User | None = session.get(User, user_id)
	if not user_db:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"User with id {user_id} not found!"
		)

	user_data: dict[str, Any] = user.model_dump(exclude_unset=True)

	if not user_data:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="No data provided to update user!"
		)

	user_db.sqlmodel_update(user_data)
	session.add(user_db)
	session.commit()
	session.refresh(user_db)

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "User patched successfully!",
			"user": UserPublic(**user_db.model_dump()).model_dump()
		}
	)


@router.delete("/{user_id}", response_model=dict[str, Any])
async def delete_user(
	user_id: Annotated[int, Path(gt=0)],
	session: SessionDep
) -> JSONResponse:

	user: User | None = session.get(User, user_id)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"User with id {user_id} not found!"
		)

	session.delete(user)
	session.commit()

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "User deleted successfully!"
		}
	)
