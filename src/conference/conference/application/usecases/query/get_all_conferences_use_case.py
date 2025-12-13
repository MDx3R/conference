from conference.conference.application.dtos.queries.get_all_conferences_query import (
    GetAllConferencesQuery,
)
from conference.conference.application.dtos.responses.conference_dto import (
    ConferenceDTO,
)
from conference.conference.application.interfaces.repositories.conference_read_repository import (
    IConferenceReadRepository,
)
from conference.conference.application.interfaces.usecases.query.get_all_conferences_use_case import (
    IGetAllConferencesUseCase,
)


class GetAllConferencesUseCase(IGetAllConferencesUseCase):
    def __init__(self, conference_read_repository: IConferenceReadRepository) -> None:
        self._conference_read_repository = conference_read_repository

    async def execute(self, query: GetAllConferencesQuery) -> list[ConferenceDTO]:
        conferences = await self._conference_read_repository.get_all(
            status=query.status, organizer_id=query.organizer_id
        )
        return [ConferenceDTO.from_read_model(conference) for conference in conferences]
