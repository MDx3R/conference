from abc import ABC, abstractmethod

from conference.conference.application.dtos.queries.get_all_conferences_query import (
    GetAllConferencesQuery,
)
from conference.conference.application.dtos.responses.conference_dto import (
    ConferenceDTO,
)


class IGetAllConferencesUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetAllConferencesQuery) -> list[ConferenceDTO]: ...
