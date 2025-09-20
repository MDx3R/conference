from unittest.mock import Mock
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from sso.domain.value_objects.username import Username
from user.domain.entity.user import User
from user.domain.factories.user_factory import UserFactory


class TestUserFactory:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()

        self.uuid_generator = Mock(spec=IUUIDGenerator)
        self.uuid_generator.create.return_value = self.user_id

        self.factory = UserFactory(self.uuid_generator)

    def test_create_success(self) -> None:
        # Arrange
        username = "testuser"

        # Act
        result = self.factory.create(username)

        # Assert
        assert result == User(self.user_id, Username(username))

    def test_create_no_name_fails(self) -> None:
        with pytest.raises(InvariantViolationError):
            self.factory.create("")
