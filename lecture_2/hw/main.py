from fastapi import FastAPI
from lecture_2.hw.shop_api.item_routes import item_router
from lecture_2.hw.shop_api.cart_routes import cart_router

app = FastAPI(title="Shop API")

app.include_router(item_router)
app.include_router(cart_router)
