from __future__ import annotations
from typing import List
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional


@dataclass(slots=True)
class CartItem:
    id: int
    name: str
    quantity: int
    available: bool
    
@dataclass(slots=True)
class Cart:
    id: int
    items: List[CartItem] = None
    price: float = 0
    
@dataclass(slots=True)
class Item:
    id: int
    name: str
    price: float
    deleted: bool = False
    
class CartResponse(BaseModel):
    id: int
    items: List[CartItem] = None
    price: float = 0
    
    @staticmethod
    def from_cart(cart: Cart) -> CartResponse:
        return CartResponse(
            id = cart.id,
            items = cart.items,
            price = cart.price,
        )

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False
    
    @staticmethod
    def from_item(item: Item) -> ItemResponse:
        return ItemResponse(
            id = item.id,
            name = item.name,
            price = item.price,
            deleted = item.deleted
        )
        
class ItemRequest(BaseModel):
    name: Optional[str]
    price: Optional[float]