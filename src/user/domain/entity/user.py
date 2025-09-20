from dataclasses import dataclass
from typing import Self
from uuid import UUID

from user.domain.value_objects.password import Password
from user.domain.value_objects.username import Username


@dataclass
class User:
    user_id: UUID
    username: Username
    password: Password

    @classmethod
    def create(cls, user_id: UUID, username: str, password: str) -> Self:
        return cls(
            user_id=user_id, username=Username(username), password=Password(password)
        )
