"""
Tests the users API endpoints.
"""

from fastapi.testclient import TestClient

from soposerve.api.models.users import (
    CreateUserResponse,
    ReadUserResponse,
    UpdateUserResponse,
)
from soposerve.service.users import Privilege


def test_create_user_that_exists(test_api_client: TestClient, test_api_user: str):
    response = test_api_client.put(
        f"/users/create/{test_api_user}",
        json={
            "privileges": [Privilege.DOWNLOAD.value, Privilege.LIST.value]
        }
    )

    assert response.status_code == 409

def test_read_user(test_api_client: TestClient, test_api_user: str):
    response = test_api_client.get(f"/users/read/{test_api_user}")

    assert response.status_code == 200
    validated = ReadUserResponse.model_validate(response.json())

    assert validated.name == test_api_user

def test_update_user(test_api_client: TestClient, test_api_user: str):
    response = test_api_client.post(
        f"/users/update/{test_api_user}",
        json={
            "privileges": [Privilege.UPLOAD.value],
            "refresh_key": True
        }
    )

    assert response.status_code == 200
    validated = UpdateUserResponse.model_validate(response.json())
    assert validated.api_key is not None

    response = test_api_client.post(
        f"/users/update/{test_api_user}",
        json={
            "privileges": [Privilege.LIST.value],
            "refresh_key": False
        }
    )

    assert response.status_code == 200
    validated = CreateUserResponse.model_validate(response.json())
    assert validated.api_key is None


