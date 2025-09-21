from uuid import UUID

from common.application.exceptions import ApplicationError


class InvalidPasswordError(ApplicationError):
    def __init__(self, identity_id: UUID) -> None:
        super().__init__(f"Invalid password for user {identity_id}")
        self.identity_id = identity_id


class InvalidUsernameError(ApplicationError):
    def __init__(self, username: str) -> None:
        super().__init__(f"Invalid username: {username}")
        self.username = username
