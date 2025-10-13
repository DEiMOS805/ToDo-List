from sqlmodel import select
from datetime import datetime
from typing import Any, Annotated, Sequence
from fastapi.responses import JSONResponse, Response
from fastapi import APIRouter, Query, Path, Body, Depends, HTTPException, status

from src.resources.models import User, ToDoCreate, ToDo, ToDoUpdate
from src.resources.functions import format_todo_response, map_todo_list
from src.resources.dependencies import SessionDep, get_current_active_user


router = APIRouter()


@router.post("/users/{user_id}/todos", response_model=dict[str, Any])
async def create_todo(
	user_id: Annotated[int, Path(gt=0)],
	current_user: Annotated[User, Depends(get_current_active_user)],
	session: SessionDep,
	todo: ToDoCreate
) -> JSONResponse:

	if not current_user.is_admin and current_user.id != user_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Given user does not have the necessary rights for this operation!"
		)

	ToDoCreate.model_validate(todo)

	user_db: User | None = session.get(User, user_id)
	if not user_db:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"User with id {user_id} not found!"
		)

	new_reminder_datetime: datetime | None = None
	new_expiration_datetime: datetime | None = None

	try:
		if todo.reminder_datetime:
			new_reminder_datetime = datetime.fromisoformat(todo.reminder_datetime)
		if todo.expiration_datetime:
			new_expiration_datetime = datetime.fromisoformat(todo.expiration_datetime)

		if new_reminder_datetime and new_expiration_datetime and new_reminder_datetime > new_expiration_datetime:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Reminder datetime cannot be after expiration datetime."
			)

	except ValueError as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"Invalid date format: {str(e)}. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."
		)

	new_todo: ToDo = ToDo(
		user_id=user_db.id,
		description=todo.description,
		done=todo.done,
		is_favorite=todo.is_favorite,
		reminder_datetime=new_reminder_datetime if todo.reminder_datetime else None,
		expiration_datetime=new_expiration_datetime
	)
	session.add(new_todo)
	session.commit()
	session.refresh(new_todo)

	return JSONResponse(
		status_code=status.HTTP_201_CREATED,
		content={
			"status": "Success",
			"message": "To-do created successfully!",
			"todo": format_todo_response(new_todo)
		}
	)


@router.get("/todos", response_model=dict[str, Any])
async def get_todos(
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

	todos: Sequence[ToDo] = session.exec(
		select(ToDo).offset(offset).limit(limit)
	).all()
	if not todos:
		return Response(status_code=status.HTTP_204_NO_CONTENT)

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "To-dos retrieved successfully!",
			"todos": map_todo_list(todos),
		}
	)


@router.get("/users/{user_id}/todos", response_model=dict[str, Any])
async def get_user_todos(
	user_id: Annotated[int, Path(gt=0)],
	current_user: Annotated[User, Depends(get_current_active_user)],
	session: SessionDep,
	offset: Annotated[int, Query(ge=0)] = 0,
	limit: Annotated[int, Query(ge=1)] = 10
) -> Response | JSONResponse:

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

	if not user.todos:
		return Response(status_code=status.HTTP_204_NO_CONTENT)

	todos: list[dict[str, Any]] = map_todo_list(user.todos)
	todos = todos[offset:offset + limit]

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "To-dos retrieved successfully!",
			"todos": todos,
		}
	)


@router.get("/users/{user_id}/todos/{todo_id}", response_model=dict[str, Any])
async def get_todo(
	user_id: Annotated[int, Path(gt=0)],
	todo_id: Annotated[int, Path(gt=0)],
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

	todo: ToDo | None = session.exec(select(ToDo). \
		where(ToDo.id == todo_id).where(ToDo.user_id == user_id)
	).first()
	if not todo:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"To-do with id {todo_id} for user with id {user_id} not found!"
		)

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "To-do retrieved successfully!",
			"todo": format_todo_response(todo)
		}
	)


@router.patch("/users/{user_id}/todos/{todo_id}", response_model=dict[str, Any])
async def patch_todo(
	user_id: Annotated[int, Path(gt=0)],
	todo_id: Annotated[int, Path(gt=0)],
	session: SessionDep,
	current_user: Annotated[User, Depends(get_current_active_user)],
	todo: Annotated[ToDoUpdate, Body()]
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

	todo_db: ToDo | None = session.exec(select(ToDo). \
		where(ToDo.id == todo_id).where(ToDo.user_id == user_id)
	).first()
	if not todo_db:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"To-do with id {todo_id} for user with id {user_id} not found!"
		)

	ToDoUpdate.model_validate(todo)

	change_flag: bool = False
	if todo.description and todo.description != todo_db.description:
		change_flag = True
		todo_db.description = todo.description
	if todo.done and todo.done != todo_db.done:
		change_flag = True
		todo_db.done = todo.done
	if todo.is_favorite and todo.is_favorite != todo_db.is_favorite:
		change_flag = True
		todo_db.is_favorite = todo.is_favorite
	if todo.reminder_datetime and todo.reminder_datetime != todo_db.reminder_datetime:
		change_flag = True
		todo_db.reminder_datetime = datetime.fromisoformat(todo.reminder_datetime)
	if todo.expiration_datetime and todo.expiration_datetime != todo_db.expiration_datetime:
		change_flag = True
		todo_db.expiration_datetime = datetime.fromisoformat(todo.expiration_datetime)

	if change_flag:
		todo_db.write_datetime = datetime.now()

	session.add(todo_db)
	session.commit()
	session.refresh(todo_db)

	return JSONResponse(
		status_code=status.HTTP_201_CREATED,
		content={
			"status": "Success",
			"message": "To-do patched successfully!",
			"todo": format_todo_response(todo_db)
		}
	)


@router.delete("/users/{user_id}/todos/{todo_id}", response_model=dict[str, Any])
async def delete_todo(
	user_id: Annotated[int, Path(gt=0)],
	todo_id: Annotated[int, Path(gt=0)],
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

	todo: ToDo | None = session.exec(select(ToDo). \
		where(ToDo.id == todo_id).where(ToDo.user_id == user_id)
	).first()
	if not todo:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"To-do with id {todo_id} for user with id {user_id} not found!"
		)

	session.delete(todo)
	session.commit()

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "To-do deleted successfully!"
		}
	)
