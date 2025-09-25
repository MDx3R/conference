from abc import ABC, abstractmethod

from conference.participant.application.dtos.queries.get_user_be_id_query import (
    GetParticipantByIdQuery,
)
from conference.participant.application.dtos.responses.user_dto import ParticipantDTO


class IGetSelfUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetParticipantByIdQuery) -> ParticipantDTO: ...
