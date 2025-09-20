from unittest.mock import Mock
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from identity.domain.entity.identity import Identity
from identity.domain.factories.identity_factory import IdentityFactory
from identity.domain.value_objects.password import Password
from identity.domain.value_objects.username import Username


class TestIdentityFactory:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()

        self.uuid_generator = Mock(spec=IUUIDGenerator)
        self.uuid_generator.create.return_value = self.user_id

        self.factory = IdentityFactory(self.uuid_generator)

    def test_create_success(self) -> None:
        # Arrange
        username = "testuser"
        password_hash = "hash"

        # Act
        result = self.factory.create(username, password_hash)

        # Assert
        assert result == Identity(
            self.user_id, Username(username), Password(password_hash)
        )

    def test_create_no_name_no_pass_fails(self) -> None:
        with pytest.raises(InvariantViolationError):
            self.factory.create("", "hash")
        with pytest.raises(InvariantViolationError):
            self.factory.create("username", "")
        with pytest.raises(InvariantViolationError):
            self.factory.create("", "")
