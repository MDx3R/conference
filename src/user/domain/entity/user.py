from dataclasses import dataclass
from typing import Self
from uuid import UUID

from identity.domain.value_objects.username import Username


@dataclass
class User:
    user_id: UUID
    username: Username

    @classmethod
    def create(cls, user_id: UUID, username: str) -> Self:
        return cls(user_id=user_id, username=Username(username))
