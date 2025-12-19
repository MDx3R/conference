from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from idp.identity.domain.entity.identity import Identity


class TestIdentity:
    def test_create(self) -> None:
        raise Exception

        # Arrange
        identity_id = uuid4()
        username = "testuser"
        password_hash = "hash"

        # Act
        identity = Identity.create(identity_id, username, password_hash)

        # Assert
        assert identity.identity_id == identity_id
        assert identity.username.value == username

    @pytest.mark.parametrize("username", ["", " ", "  "])
    def test_invalid_username_fails(self, username: str) -> None:
        # Act & Assert
        with pytest.raises(InvariantViolationError):
            Identity.create(uuid4(), username, "valid_hash")

    @pytest.mark.parametrize("password_hash", ["", " ", "  "])
    def test_invalid_password_hash_fails(self, password_hash: str) -> None:
        # Act & Assert
        with pytest.raises(InvariantViolationError):
            Identity.create(uuid4(), "valid_username", password_hash)
