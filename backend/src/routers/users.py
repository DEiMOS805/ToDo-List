from sqlmodel import select
from datetime import timedelta
from typing import Any, Annotated, Sequence
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Path, Query, Body, Depends, HTTPException, status

from src.resources.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.resources.models import User, UserPublic, UserCreate, UserUpdate
from src.resources.dependencies import SessionDep, get_current_active_user
from src.resources.functions import encrypt, create_access_token, authenticate_user


router = APIRouter()


@router.post("/", response_model=dict[str, Any])
async def create_user(user: UserCreate, session: SessionDep) -> JSONResponse:
	user_db: User = User.model_validate(user)

	encrypted_password: bytes = encrypt(user.password)
	user_db.password = encrypted_password

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


@router.post("/auth", response_model=dict[str, Any])
async def auth_user(
	session: SessionDep,
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> JSONResponse:

	user: User | bool = authenticate_user(
		session,
		form_data.username,
		form_data.password
	)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password!",
			headers={"WWW-Authenticate": "Bearer"},
		)

	token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	token = create_access_token(
		data={"sub": user.username},
		expires_delta=token_expire
	)

	return JSONResponse(
		status_code=status.HTTP_201_CREATED,
		content={
			"status": "Success",
			"message": "Access token created successfully!",
			"access_token": token,
			"token_type": "Bearer"
		}
	)


@router.get("/", response_model=dict[str, Any])
async def get_users(
	current_user: Annotated[User, Depends(get_current_active_user)],
	session: SessionDep,
	offset: Annotated[int, Query(ge=0)] = 0,
	limit: Annotated[int, Query(ge=1)] = 10
) -> Response | JSONResponse:

	if not current_user.is_admin:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Given user does not have the necessary rights for this operation!"
		)

	users: Sequence[User] = session.exec(
		select(User).offset(offset).limit(limit)
	).all()
	users_list = list(
		map(
			lambda user: UserPublic(**user.model_dump()).model_dump(),
			users
		)
	)

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "Items retrieved successfully!",
			"items": users_list,
		}
	)


@router.get("/{user_id}", response_model=dict[str, Any])
async def get_user(
	user_id: Annotated[int, Path(gt=0)],
	current_user: Annotated[User, Depends(get_current_active_user)],
	session: SessionDep
) -> JSONResponse:

	if not current_user.is_admin and current_user.id != user_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Given user does not have the necessary rights for this operation!"
		)

	user_db: User | None = session.get(User, user_id)
	if not user_db:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"User with id {user_id} not found!"
		)

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "User retrieved successfully!",
			"user": UserPublic(**user_db.model_dump()).model_dump()
		}
	)


@router.patch("/{user_id}", response_model=dict[str, Any])
async def patch_user(
	user_id: Annotated[int, Path(gt=0)],
	current_user: Annotated[User, Depends(get_current_active_user)],
	user: Annotated[UserUpdate, Body()],
	session: SessionDep
) -> JSONResponse:

	if not current_user.is_admin and current_user.id != user_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Given user does not have the necessary rights for this operation!"
		)

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
	current_user: Annotated[User, Depends(get_current_active_user)],
	session: SessionDep
) -> JSONResponse:

	if not current_user.is_admin and current_user.id != user_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Given user does not have the necessary rights for this operation!"
		)

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
