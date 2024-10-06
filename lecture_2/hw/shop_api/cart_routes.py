from http import HTTPStatus
from fastapi import APIRouter, FastAPI, HTTPException, Query, Response
from lecture_2.hw import store
from typing import Annotated, List
from pydantic import NonNegativeInt, PositiveInt, PositiveFloat
from lecture_2.hw.store.models import CartResponse

cart_router = APIRouter(prefix="/cart")


@cart_router.post(
    "",
    status_code=HTTPStatus.CREATED,
)
async def post_cart(response: Response) -> CartResponse:
    created_cart = store.add_cart()
    response.headers["location"] = f"/cart/{created_cart.id}"
    return CartResponse.from_cart(created_cart)


@cart_router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested cart as one was not found",
        },
    },
)
async def get_cart(id: int) -> CartResponse:
    cart = store.get_cart(id)
    if not cart:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /cart/{id} was not found",
        )

    return CartResponse.from_cart(cart)


@cart_router.get("", status_code=HTTPStatus.OK)
async def get_carts(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[PositiveFloat, Query()] = None,
    max_price: Annotated[PositiveFloat, Query()] = None,
    min_quantity: Annotated[NonNegativeInt, Query()] = None,
    max_quantity: Annotated[NonNegativeInt, Query()] = None,
) -> List[CartResponse]:
    carts = store.get_carts(
        offset, limit, min_price, max_price, min_quantity, max_quantity
    )
    return [CartResponse.from_cart(cart) for cart in carts]


@cart_router.post(
    "/{cart_id}/add/{item_id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully added requested items to cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to find requested cart or item",
        },
    },
)
async def add_item_to_cart(cart_id: int, item_id: int) -> CartResponse:
    cart = store.get_cart(cart_id)
    if cart is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"Cart with ID {cart_id} not found"
        )
    item = store.get_item(item_id)
    if item is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"Item with ID {item_id} not found"
        )
    updated_cart = store.add_item_to_cart(cart_id, item_id)
    return CartResponse.from_cart(updated_cart)
