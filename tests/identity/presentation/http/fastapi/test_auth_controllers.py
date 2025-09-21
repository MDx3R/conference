from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from idp.auth.application.dtos.commands.login_command import LoginCommand
from idp.auth.application.dtos.commands.logout_command import LogoutCommand
from idp.auth.application.dtos.commands.refresh_token_command import (
    RefreshTokenCommand,
)
from idp.auth.application.dtos.models.auth_tokens import AuthTokens
from idp.auth.application.exceptions import InvalidPasswordError, InvalidUsernameError
from idp.auth.application.interfaces.usecases.command.login_use_case import (
    ILoginUseCase,
)
from idp.auth.application.interfaces.usecases.command.logout_use_case import (
    ILogoutUseCase,
)
from idp.auth.application.interfaces.usecases.command.refresh_token_use_case import (
    IRefreshTokenUseCase,
)
from idp.auth.presentation.http.fastapi.controllers import auth_router
from idp.identity.presentation.http.fastapi.auth import (
    oauth2_scheme_no_error,
)


@pytest.mark.asyncio
class TestAuthController:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = FastAPI()
        self.app.include_router(auth_router)
        self.client: TestClient = TestClient(self.app)

        self.login_use_case = AsyncMock(spec=ILoginUseCase)
        self.logout_use_case = AsyncMock(spec=ILogoutUseCase)
        self.refresh_token_use_case = AsyncMock(spec=IRefreshTokenUseCase)

        self.app.dependency_overrides[ILoginUseCase] = lambda: self.login_use_case
        self.app.dependency_overrides[ILogoutUseCase] = lambda: self.logout_use_case
        self.app.dependency_overrides[IRefreshTokenUseCase] = (
            lambda: self.refresh_token_use_case
        )

    async def test_login_success(self):
        # Arrange
        username = "testuser"
        password = "testpass"
        user_id = uuid4()
        mock_response = AuthTokens(
            user_id,
            access_token="access_token",
            refresh_token="refresh_token",
        )
        self.login_use_case.execute.return_value = mock_response

        # Act
        response = self.client.post(
            "/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "user_id": str(user_id),
            "access_token": "access_token",
            "refresh_token": "refresh_token",
        }
        self.login_use_case.execute.assert_awaited_once_with(
            LoginCommand(username=username, password=password)
        )

    async def test_login_unauthenticated_required(self):
        # Arrange
        username = "testuser"
        password = "testpass"

        # Act
        response = self.client.post(
            "/login",
            data={"username": username, "password": password},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": "Bearer authenticated_token",  # Token
            },
        )

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "You are already logged in"}

    async def test_login_invalid_username(self):
        # Arrange
        username = "invalid_username"
        password = "testpass"

        self.login_use_case.execute.side_effect = InvalidUsernameError(username)

        # Act
        response = self.client.post(
            "/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"]["error"] == "InvalidUsernameError"

    async def test_login_invalid_password(self):
        # Arrange
        username = "valid_username"
        password = "invalid_pass"

        self.login_use_case.execute.side_effect = InvalidPasswordError(uuid4())

        # Act
        response = self.client.post(
            "/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"]["error"] == "InvalidPasswordError"

    async def test_logout_success(self):
        # Arrange
        token = "valid_token"
        self.logout_use_case.execute.return_value = None

        # Act
        response = self.client.post(
            "/logout", headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()
        self.logout_use_case.execute.assert_awaited_once_with(
            LogoutCommand(refresh_token=token)
        )

    async def test_logout_unauthenticated_fails(self):
        # Act
        response = self.client.post("/logout")  # No token

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Authentication required"}

    async def test_refresh_success(self):
        # Arrange
        token = "valid_refresh_token"
        user_id = uuid4()
        mock_response = AuthTokens(
            user_id,
            access_token="new_access_token",
            refresh_token="new_refresh_token",
        )
        self.refresh_token_use_case.execute.return_value = mock_response

        # Act
        response = self.client.post(
            "/refresh", headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "user_id": str(user_id),
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
        }
        self.refresh_token_use_case.execute.assert_awaited_once_with(
            RefreshTokenCommand(token)
        )

    async def test_refresh_unauthenticated_fails(self):
        # Arrange
        self.app.dependency_overrides[oauth2_scheme_no_error] = lambda: None  # No token

        # Act
        response = self.client.post("/refresh")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Authentication required"}
