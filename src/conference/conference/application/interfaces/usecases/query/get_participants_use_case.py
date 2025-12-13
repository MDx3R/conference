from abc import ABC, abstractmethod

from conference.conference.application.dtos.queries.get_participants_query import (
    GetParticipantsQuery,
)
from conference.conference.application.dtos.responses.participation_with_participant_dto import (
    ParticipationWithParticipantDTO,
)


class IGetParticipantsUseCase(ABC):
    @abstractmethod
    async def execute(
        self, query: GetParticipantsQuery
    ) -> list[ParticipationWithParticipantDTO]: ...
