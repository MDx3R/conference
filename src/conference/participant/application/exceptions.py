from uuid import UUID

from common.application.exceptions import NotFoundError


class ParticipantNotFoundError(NotFoundError):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(user_id)
        self.user_id = user_id
