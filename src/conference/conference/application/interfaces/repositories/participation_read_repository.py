from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from conference.conference.application.read_models.participation_read_model import (
    ParticipationReadModel,
)
from conference.conference.application.read_models.participation_with_participant_read_model import (
    ParticipationWithParticipantReadModel,
)


class IParticipationReadRepository(ABC):
    @abstractmethod
    async def get_by_id(
        self, conference_id: UUID, participant_id: UUID
    ) -> ParticipationReadModel: ...

    @abstractmethod
    async def get_all_by_conference(
        self, conference_id: UUID
    ) -> list[ParticipationReadModel]: ...

    @abstractmethod
    async def get_filtered(  # noqa: PLR0913
        self,
        conference_id: UUID,
        invitation_date: date | None = None,
        fee_paid: bool | None = None,
        fee_payment_date_from: date | None = None,
        fee_payment_date_to: date | None = None,
        city: str | None = None,
        needs_hotel: bool | None = None,
        has_submission: bool | None = None,
    ) -> list[ParticipationWithParticipantReadModel]: ...
