from lecture_2.hw.store.models import Cart, Item, CartItem, ItemRequest
from typing import Iterable, List

carts = dict[int, Cart]()
items = dict[int, Item]()


def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1


cart_id_generator = int_id_generator()
item_id_generator = int_id_generator()


def get_item(id: int) -> Item | None:
    if id not in items:
        return None
    return Item(id, items[id].name, items[id].price, items[id].deleted)


def get_items(
    offset: int = 0,
    limit: int = 10,
    min_price: float = None,
    max_price: float = None,
    show_deleted: bool = False,
):
    filtered_items = list(items.values())

    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]
    if not show_deleted:
        filtered_items = [item for item in filtered_items if not item.deleted]

    return filtered_items[offset : offset + limit]


def get_cart(id: int) -> Cart | None:
    if id not in carts:
        return None
    return Cart(id, carts[id].items, carts[id].price)


def get_carts(
    offset: int = 0,
    limit: int = 10,
    min_price: float = None,
    max_price: float = None,
    min_quantity: int = None,
    max_quantity: int = None,
) -> List[Cart]:
    filtered_carts = list(carts.values())

    if min_price is not None:
        filtered_carts = [cart for cart in filtered_carts if cart.price >= min_price]
    if max_price is not None:
        filtered_carts = [cart for cart in filtered_carts if cart.price <= max_price]
    if min_quantity is not None:
        filtered_carts = [
            cart
            for cart in filtered_carts
            if sum(item.quantity for item in cart.items) >= min_quantity
        ]
    if max_quantity is not None:
        filtered_carts = [
            cart
            for cart in filtered_carts
            if sum(item.quantity for item in cart.items) <= max_quantity
        ]

    return filtered_carts[offset : offset + limit]


def add_item_to_cart(cart_id: int, item_id: int):
    cart = get_cart(cart_id)
    item = get_item(item_id)
    cart_item = next((ci for ci in cart.items if ci.id == item_id), None)
    if cart_item:
        cart_item.quantity += 1
    else:
        cart.items.append(
            CartItem(id=item_id, name=item.name, quantity=1, available=not item.deleted)
        )
    cart.price += item.price
    carts[cart_id] = cart
    return cart


def delete_item(id: int) -> Item:
    item = items[id]
    item.deleted = True
    items[id] = item
    return item


def patch_item(id: int, patch_item: ItemRequest):
    if id not in items:
        return None
    if patch_item.name is not None:
        items[id].name = patch_item.name
    if patch_item.price is not None:
        items[id].price = patch_item.price
    return Item(
        id=id, name=items[id].name, price=items[id].price, deleted=items[id].deleted
    )


def add_cart() -> Cart:
    id = next(cart_id_generator)
    new_cart = Cart(id, [], 0)
    carts[id] = new_cart
    return new_cart


def add_item(name: str = "", price: float = 0) -> Item:
    id = next(item_id_generator)
    new_item = Item(id=id, name=name, price=price)
    items[id] = new_item
    return new_item


def change_item(json: ItemRequest, id: int) -> Item:
    if json.name is not None:
        items[id].name = json.name
    if json.price is not None:
        items[id].price = json.price
    return items[id]
