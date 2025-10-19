from abc import ABC, abstractmethod

from conference.conference.application.dtos.queries.get_conference_by_id_query import (
    GetConferenceByIdQuery,
)
from conference.conference.application.dtos.responses.conference_dto import (
    ConferenceDTO,
)


class IGetConferenceByIdUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetConferenceByIdQuery) -> ConferenceDTO: ...
