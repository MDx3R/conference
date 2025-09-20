from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from user.domain.entity.user import User


class TestUser:
    def test_create(self) -> None:
        # Arrange
        user_id = uuid4()
        username = "testuser"

        # Act
        user = User.create(user_id, username)

        # Assert
        assert user.user_id == user_id
        assert user.username.value == username

    @pytest.mark.parametrize("username", ["", " ", "  "])
    def test_invalid_username_fails(self, username: str) -> None:
        # Act
        with pytest.raises(InvariantViolationError):
            User.create(uuid4(), username)
