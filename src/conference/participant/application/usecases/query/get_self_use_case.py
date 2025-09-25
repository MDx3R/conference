from conference.participant.application.dtos.queries.get_user_be_id_query import (
    GetParticipantByIdQuery,
)
from conference.participant.application.dtos.responses.user_dto import ParticipantDTO
from conference.participant.application.interfaces.repositories.participant_read_repository import (
    IParticipantReadRepository,
)
from conference.participant.application.interfaces.usecases.query.get_self_use_case import (
    IGetSelfUseCase,
)


class GetSelfUseCase(IGetSelfUseCase):
    def __init__(self, user_repository: IParticipantReadRepository) -> None:
        self.user_repository = user_repository

    async def execute(self, query: GetParticipantByIdQuery) -> ParticipantDTO:
        participant = await self.user_repository.get_by_id(query.user_id)
        return ParticipantDTO.from_user(participant)
