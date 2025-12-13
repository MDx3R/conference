from conference.conference.application.dtos.queries.get_participants_query import (
    GetParticipantsQuery,
)
from conference.conference.application.dtos.responses.participation_with_participant_dto import (
    ParticipationWithParticipantDTO,
)
from conference.conference.application.interfaces.repositories.participation_read_repository import (
    IParticipationReadRepository,
)
from conference.conference.application.interfaces.usecases.query.get_participants_use_case import (
    IGetParticipantsUseCase,
)


class GetParticipantsUseCase(IGetParticipantsUseCase):
    def __init__(
        self, participation_read_repository: IParticipationReadRepository
    ) -> None:
        self._participation_read_repository = participation_read_repository

    async def execute(
        self, query: GetParticipantsQuery
    ) -> list[ParticipationWithParticipantDTO]:
        participations = await self._participation_read_repository.get_filtered(
            conference_id=query.conference_id,
            invitation_date=query.invitation_date,
            fee_paid=query.fee_paid,
            fee_payment_date_from=query.fee_payment_date_from,
            fee_payment_date_to=query.fee_payment_date_to,
            city=query.city,
            needs_hotel=query.needs_hotel,
            has_submission=query.has_submission,
        )

        return [
            ParticipationWithParticipantDTO.from_read_model(p) for p in participations
        ]
