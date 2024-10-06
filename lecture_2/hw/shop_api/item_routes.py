from http import HTTPStatus
from typing import Any, Annotated, List
from fastapi import APIRouter, FastAPI, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt, PositiveFloat
from lecture_2.hw import store
from lecture_2.hw.store.models import ItemResponse, ItemRequest

item_router = APIRouter(prefix="/item")


@item_router.post(
    "",
    status_code=HTTPStatus.CREATED,
)
async def post_item(item: ItemRequest, response: Response) -> ItemResponse:
    new_item = store.add_item(item.name, item.price)
    response.headers["location"] = f"/item/{new_item.id}"
    return ItemResponse.from_item(new_item)


@item_router.get(
    "/{id}",
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested item as one was not found",
        },
    },
)
async def get_item(id: int) -> ItemResponse:
    item = store.get_item(id)
    if not item or item.deleted:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /item/{id} was not found",
        )

    return ItemResponse.from_item(item)


@item_router.get("")
async def get_items(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[PositiveFloat, Query()] = None,
    max_price: Annotated[PositiveFloat, Query()] = None,
    show_deleted: Annotated[bool, Query()] = False,
) -> List[ItemResponse]:
    items = store.get_items(offset, limit, min_price, max_price, show_deleted)
    return [ItemResponse.from_item(item) for item in items]


@item_router.put(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested item as one was not found",
        },
    },
)
async def put_item(item: ItemRequest, id: int) -> ItemResponse:
    if not store.get_item(id):
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /item/{id} was not found",
        )
    changed_item = store.change_item(item, id)
    return ItemResponse.from_item(changed_item)


@item_router.patch(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully modified item",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Failed to modify item as one was not found",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Failed to modify item as there are unexpected fields in update data",
        },
    },
)
async def path_item(id: int, item_info: dict[str, Any]) -> ItemResponse:
    item = store.get_item(id)
    if item.deleted == True:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Requested resource /item/{id} is deleted",
        )
    if item_info is None:
        raise HTTPException(HTTPStatus.NOT_MODIFIED)
    unexpected_fields = set(item_info.keys()) - {"name", "price"}
    if unexpected_fields:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=f"Unexpected fields in update data: {', '.join(unexpected_fields)}",
        )
    patched_item = store.patch_item(
        id,
        ItemRequest(
            name=item_info.get("name", None), price=item_info.get("price", None)
        ),
    )
    if patched_item is None:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Requested resource /item/{id} was not found",
        )
    return ItemResponse.from_item(patched_item)


@item_router.delete(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully changed requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Not found requested item",
        },
    },
)
async def delete_item(id: int) -> ItemResponse:
    item = store.get_item(id)
    if not item:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /item/{id} was not found",
        )
    deleted_item = store.delete_item(id)
    return ItemResponse.from_item(deleted_item)
