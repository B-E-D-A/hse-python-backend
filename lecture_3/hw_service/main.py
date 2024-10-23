from fastapi import FastAPI
# from fastapi.routing import Route
from hw_service.shop_api.item_routes import item_router
from hw_service.shop_api.cart_routes import cart_router
from prometheus_fastapi_instrumentator import Instrumentator
from http import HTTPStatus
from fastapi import APIRouter, FastAPI, HTTPException, Query, Response
from hw_service import store
from hw_service.store.models import CartResponse


app = FastAPI(title="Shop API")

Instrumentator().instrument(app).expose(app)
app.include_router(item_router)
app.include_router(cart_router)



