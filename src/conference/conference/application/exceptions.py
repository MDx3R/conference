from uuid import UUID

from common.application.exceptions import ApplicationError, NotFoundError


class ConferenceNotFoundError(NotFoundError):
    pass


class ConferenceFullError(ApplicationError):
    def __init__(self, conference_id: UUID) -> None:
        super().__init__(f"Conference {conference_id} has reached maximum capacity")
        self.conference_id = conference_id


class ConferenceNotAcceptingParticipantsError(ApplicationError):
    def __init__(self, conference_id: UUID, status: str) -> None:
        super().__init__(
            f"Conference {conference_id} is not accepting participants (status: {status})"
        )
        self.conference_id = conference_id
        self.status = status


class ParticipationNotFoundError(NotFoundError):
    pass


class ParticipantAlreadyRegisteredError(ApplicationError):
    def __init__(self, conference_id: UUID, participant_id: UUID) -> None:
        super().__init__(
            f"Participant {participant_id} is already registered for conference {conference_id}"
        )
        self.conference_id = conference_id
        self.participant_id = participant_id
