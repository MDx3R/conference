from conference.conference.application.dtos.queries.get_conference_by_id_query import (
    GetConferenceByIdQuery,
)
from conference.conference.application.dtos.responses.conference_dto import (
    ConferenceDTO,
)
from conference.conference.application.interfaces.repositories.conference_read_repository import (
    IConferenceReadRepository,
)
from conference.conference.application.interfaces.usecases.query.get_conference_by_id_use_case import (
    IGetConferenceByIdUseCase,
)


class GetConferenceByIdUseCase(IGetConferenceByIdUseCase):
    def __init__(self, conference_read_repository: IConferenceReadRepository) -> None:
        self._conference_read_repository = conference_read_repository

    async def execute(self, query: GetConferenceByIdQuery) -> ConferenceDTO:
        conference = await self._conference_read_repository.get_by_id(
            query.conference_id
        )
        return ConferenceDTO.from_read_model(conference)
