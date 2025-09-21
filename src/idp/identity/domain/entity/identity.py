from dataclasses import dataclass
from typing import Self
from uuid import UUID

from idp.identity.domain.value_objects.password import Password
from idp.identity.domain.value_objects.username import Username


@dataclass
class Identity:
    identity_id: UUID
    username: Username
    password: Password

    @classmethod
    def create(cls, identity_id: UUID, username: str, password: str) -> Self:
        return cls(
            identity_id=identity_id,
            username=Username(username),
            password=Password(password),
        )
