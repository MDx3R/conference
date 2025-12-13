from uuid import UUID

from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.interfaces.conference_factory import (
    ConferenceFactoryDTO,
    IConferenceFactory,
)
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)


class ConferenceFactory(IConferenceFactory):
    def create(
        self,
        conference_id: UUID,
        data: ConferenceFactoryDTO,
    ) -> Conference:
        description = ConferenceDescription(
            short_description=data.short_description,
            full_description=data.full_description,
        )

        dates = ConferenceDates(
            start_date=data.start_date,
            end_date=data.end_date,
            registration_deadline=data.registration_deadline,
        )

        return Conference.create(
            conference_id=conference_id,
            title=data.title,
            description=description,
            dates=dates,
            location=data.location,
            organizer_id=data.organizer_id,
            max_participants=data.max_participants,
        )
