from uuid import UUID

from common.application.exceptions import ApplicationError, NotFoundError


class IdentityNotFoundError(NotFoundError):
    pass


class UsernameAlreadyTakenError(ApplicationError):
    def __init__(self, username: str):
        super().__init__(f"Username '{username}' is already taken by another user.")
        self.username = username


class InvalidPasswordError(ApplicationError):
    def __init__(self, identity_id: UUID) -> None:
        super().__init__(f"Invalid password for user {identity_id}")
        self.identity_id = identity_id


class InvalidUsernameError(ApplicationError):
    def __init__(self, username: str) -> None:
        super().__init__(f"Invalid username: {username}")
        self.username = username


class TokenExpiredError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Token expired")


class TokenRevokedError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Token revoked")


class InvalidTokenError(ApplicationError):
    def __init__(self, message: str = "Invalid token") -> None:
        super().__init__(message)
