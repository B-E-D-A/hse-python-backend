import base64
from unittest.mock import AsyncMock
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel, SecretStr

from fastapi.testclient import TestClient
from lecture_4.demo_service.core.users import UserRole, password_is_longer_than_8
from lecture_4.demo_service.api.utils import initialize, user_service
from datetime import datetime
from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import UserService, UserInfo, UserRole


@pytest_asyncio.fixture
async def app() -> FastAPI:
    app = create_app()
    async with initialize(app):
        yield app


@pytest_asyncio.fixture
async def client(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://lecture4test") as client:
        yield client


@pytest.mark.parametrize(
    "request_data, expected_status, error_detail",
    [
        (
            {
                "username": "successful_user",
                "name": "Business Man",
                "birthdate": "2000-03-27T00:00:00Z",
                "password": "Qwerty1234567",
            },
            200,
            "username is already taken",
        ),
        (
            {
                "username": "bad_user_1",
                "name": "Just User",
                "birthdate": "2000-03-27T00:00:00Z",
                "password": "onlyletters",
            },
            400,
            "invalid password",
        ),
        (
            {
                "username": "bad_user_2",
                "name": "Another user",
                "birthdate": "2000-03-27T00:00:00Z",
                "password": "short",
            },
            400,
            "invalid password",
        ),
    ],
)
@pytest.mark.asyncio
async def test_register_user(
    client: AsyncClient, request_data, expected_status, error_detail
):
    response = await client.post("/user-register", json=request_data)
    assert response.status_code == expected_status
    if response.status_code != 200:
        assert response.json()["detail"] == error_detail

    if request_data["name"] == "Business Man":
        same_request_data = {
            "username": "successful_user",
            "name": "Fake Business Man",
            "birthdate": "2000-03-27T00:00:00Z",
            "password": "Qwerty1234567",
        }
        response_2 = await client.post("/user-register", json=same_request_data)
        assert response_2.status_code == 400
        assert response_2.json()["detail"] == error_detail


def get_admin_secret(username: str, password: str) -> dict:
    return {
        "Authorization": f"Basic {base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")}"
    }


@pytest.mark.parametrize(
    "request_data, expected_status, error_detail",
    [
        ({"id": 2}, 200, None),
        ({"username": "testuser"}, 200, None),
        ({"id": 2, "username": "testuser"}, 400, "both id and username are provided"),
        ({"author_role": UserRole.USER}, 400, "neither id nor username are provided"),
    ],
)
@pytest.mark.asyncio
async def test_get_user(
    client: AsyncClient, request_data, expected_status, error_detail
):

    user_data = {
        "username": "testuser",
        "name": "Human",
        "birthdate": "2000-03-27T00:00:00Z",
        "password": "Qwerty1234567",
    }
    await client.post("/user-register", json=user_data)
    response = await client.post(
        "/user-get",
        params=request_data,
        headers={"Authorization": "Basic dGVzdHVzZXI6UXdlcnR5MTIzNDU2Nw=="},
    )
    assert response.status_code == expected_status

    if response.status_code != 200:
        assert response.json()["detail"] == error_detail


@pytest.mark.parametrize(
    "request_data, expected_status, error_detail",
    [
        ({"id": 3}, 404, "Not Found"),
        ({"username": "unknownuser"}, 404, "Not Found"),
    ],
)
@pytest.mark.asyncio
async def test_get_unknown_user(
    client: AsyncClient, request_data, expected_status, error_detail
):
    response = await client.post(
        "/user-get",
        params=request_data,
        headers=get_admin_secret("admin", "superSecretAdminPassword123"),
    )

    print(response.json())
    assert response.status_code == expected_status

    if response.status_code != 200:
        assert response.json()["detail"] == error_detail


@pytest.mark.parametrize(
    "header_data, expected_status",
    [
        ({"Authorization": "Basic SoMeWRONGLet5Er35s"}, 401),
        (get_admin_secret("admin", "WrongSecretAdminPassword123"), 401),
    ],
)
@pytest.mark.asyncio
async def test_failed_authorization(client: AsyncClient, header_data, expected_status):
    response = await client.post(
        "/user-get",
        params={},
        headers=header_data,
    )
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "request_data, expected_status, error_detail",
    [
        ({"id": 2}, 200, None),
        ({"id": 100}, 400, "user not found"),
    ],
)
@pytest.mark.asyncio
async def test_promote_user(
    client: AsyncClient, request_data, expected_status, error_detail
):
    user_data = {
        "username": "testuser",
        "name": "Human",
        "birthdate": "2000-03-27T00:00:00Z",
        "password": "Qwerty1234567",
    }
    await client.post("/user-register", json=user_data)

    response = await client.post(
        "/user-promote",
        params=request_data,
        headers=get_admin_secret("admin", "superSecretAdminPassword123"),
    )

    assert response.status_code == expected_status

    if response.status_code != 200:
        assert response.json()["detail"] == error_detail


@pytest.mark.asyncio
async def test_promote_user_not_by_admin(
    client: AsyncClient,
):
    user_data = {
        "username": "testuser",
        "name": "Human",
        "birthdate": "2000-03-27T00:00:00Z",
        "password": "Qwerty1234567",
    }
    await client.post("/user-register", json=user_data)

    response = await client.post(
        "/user-promote",
        params={"id": 1},
        headers={"Authorization": "Basic dGVzdHVzZXI6UXdlcnR5MTIzNDU2Nw=="},
    )
    assert response.status_code == 403
