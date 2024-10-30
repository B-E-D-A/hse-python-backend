import math
import json
from http import HTTPStatus
from typing import Any, Awaitable, Callable

async def send_status_code(send, status_code):
    await send({
        "type": "http.response.start",
        "status": status_code,
        "headers": [
            [b"content-type", b"application/json"],
        ],
    })

async def send_body(send, data):
    await send({
        "type": "http.response.body",
        "body": json.dumps(data).encode(),
    })

async def app(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    assert scope["type"] == "http"    

    if scope["path"] == "/factorial" and scope["method"] == "GET":
        query_params = scope["query_string"].decode();
        if not query_params:
            await send_status_code(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            await send_body(send, "Missing value for n, must be provided as a query parameter")
            return
        try:
            n = int(query_params.split("=")[1]);
            if n < 0:
                await send_status_code(send, HTTPStatus.BAD_REQUEST)
                await send_body(send, "Invalid value for n, must be non-negative")
                return

            result = math.factorial(n)
            await send_status_code(send, 200)
            await send_body(send, {"result": result})
        except ValueError:
            await send_status_code(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            await send_body(send, "Invalid value for n, must be an integer")
            return

    elif scope["path"].startswith("/fibonacci/") and scope["method"] == "GET":
        n = scope["path"].split("/")[2]
        try:
            n = int(n)
            if n < 0:
                await send_status_code(send, HTTPStatus.BAD_REQUEST)
                await send_body(send, "Invalid value for n, must be non-negative")
                return
            a, b = 0, 1
            for _ in range(n):
                a, b = b, a + b
            await send_status_code(send, 200)
            await send_body(send, {"result": b})
        except ValueError:
            await send_status_code(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            await send_body(send, "Invalid value for n, must be an integer")
            return

    elif scope["path"] == "/mean" and scope["method"] == "GET":
        request = await receive()
        if len(request["body"]) == 0:
            await send_status_code(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            await send_body(send, "Request body is empty, provide a list of numbers")
            return
        try: 
            data = json.loads(request["body"])
            if len(data) == 0:
                await send_status_code(send, HTTPStatus.BAD_REQUEST)
                await send_body(send, "Request body must contain a non-empty list of numbers")
                return
            await send_status_code(send, 200)
            await send_body(send, {"result": sum(data) / len(data)})
        except ValueError:
            await send_status_code(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            await send_body(send, "Invalid value for data, must be a JSON array of numbers")
            return

    else:
        await send_status_code(send, HTTPStatus.NOT_FOUND)
        await send_body(send, "Endpoint not found")
