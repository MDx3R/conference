from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from idp.identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from idp.identity.application.exceptions import UsernameAlreadyTakenError
from idp.identity.application.interfaces.usecases.command.create_identity_use_case import (
    ICreateIdentityUseCase,
)
from idp.identity.presentation.http.fastapi.controllers import identity_router


@pytest.mark.asyncio
class TestIdentityController:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = FastAPI()
        self.app.include_router(identity_router)
        self.client: TestClient = TestClient(self.app)

        self.create_identity_use_case = AsyncMock(spec=ICreateIdentityUseCase)

        self.app.dependency_overrides[ICreateIdentityUseCase] = (
            lambda: self.create_identity_use_case
        )

    async def test_register_success(self):
        # Arrange
        username = "testuser"
        password = "testpass"
        user_id = uuid4()

        self.create_identity_use_case.execute.return_value = user_id

        # Act
        response = self.client.post(
            "/register",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": str(user_id)}

        self.create_identity_use_case.execute.assert_awaited_once_with(
            CreateIdentityCommand(username=username, password=password)
        )

    async def test_register_unauthenticated_required(self):
        # Arrange
        username = "testuser"
        password = "testpass"

        # Act
        response = self.client.post(
            "/register",
            json={"username": username, "password": password},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer authenticated_token",  # Token
            },
        )

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "You are already logged in"}

    async def test_login_taken_username(self):
        # Arrange
        username = "invalid_username"
        password = "testpass"

        self.create_identity_use_case.execute.side_effect = UsernameAlreadyTakenError(
            username
        )

        # Act
        response = self.client.post(
            "/register",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"]["error"] == "UsernameAlreadyTakenError"
