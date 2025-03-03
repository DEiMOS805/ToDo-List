from sqlmodel import select
from typing import Any, Annotated
from fastapi.responses import JSONResponse, Response
from fastapi import APIRouter, Query, Path, Body, HTTPException, status

from ..resources.dependencies import SessionDep
from ..resources.models import ItemBase, Item, ItemUpdate


router = APIRouter()


@router.get("/", response_model=dict[str, Any])
async def get_items(
	session: SessionDep,
	offset: Annotated[int, Query(ge=0)] = 0,
	limit: Annotated[int, Query(ge=1)] = 10
) -> Response | JSONResponse:

	items = session.exec(select(Item).offset(offset).limit(limit)).all()
	if not items:
		return Response(status_code=status.HTTP_204_NO_CONTENT)

	items = list(map(lambda item: item.model_dump(), items))

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "Items retrieved successfully!",
			"items": items,
		}
	)


@router.post("/", response_model=dict[str, Any])
async def create_item(item: ItemBase, session: SessionDep) -> JSONResponse:
	db_item: Item = Item.model_validate(item)
	session.add(db_item)
	session.commit()
	session.refresh(db_item)

	return JSONResponse(
		status_code=status.HTTP_201_CREATED,
		content={
			"status": "Success",
			"message": "Item created successfully!",
			"item": db_item.model_dump(),
		}
	)


@router.get("/{item_id}", response_model=dict[str, Any])
async def get_item(
	item_id: Annotated[int, Path(gt=0)],
	session: SessionDep
) -> JSONResponse:

	item: Item | None = session.get(Item, item_id)
	if not item:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Item with id {item_id} not found!"
		)

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "Item retrieved successfully!",
			"item": item.model_dump(),
		}
	)


@router.patch("/{item_id}", response_model=dict[str, Any])
async def patch_item(
	item_id: Annotated[int, Path(gt=0)],
	item: Annotated[ItemUpdate, Body()],
	session: SessionDep
) -> JSONResponse:

	item_db: Item | None = session.get(Item, item_id)
	if not item_db:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Item with id {item_id} not found!"
		)

	item_data: dict[str, Any] = item.model_dump(exclude_unset=True)

	if not item_data:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="No data provided to update item!"
		)

	item_db.sqlmodel_update(item_data)
	session.add(item_db)
	session.commit()
	session.refresh(item_db)

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "Item patched successfully!",
			"item": item_db.model_dump(),
		}
	)


@router.delete("/{item_id}", response_model=dict[str, Any])
async def delete_item(
	item_id: Annotated[int, Path(gt=0)],
	session: SessionDep
) -> JSONResponse:

	item: Item | None = session.get(Item, item_id)
	if not item:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Item with id {item_id} not found!"
		)

	session.delete(item)
	session.commit()

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={
			"status": "Success",
			"message": "Item deleted successfully!"
		}
	)
