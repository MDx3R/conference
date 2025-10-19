from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.models.conference_base import (
    ConferenceBase,
)


class ConferenceMapper:
    @classmethod
    def to_domain(cls, base: ConferenceBase) -> Conference:
        description = ConferenceDescription(
            short_description=base.short_description,
            full_description=base.full_description,
        )

        dates = ConferenceDates(
            start_date=base.start_date,
            end_date=base.end_date,
            registration_deadline=base.registration_deadline,
        )

        return Conference(
            conference_id=base.conference_id,
            title=base.title,
            description=description,
            dates=dates,
            location=base.location,
            max_participants=base.max_participants,
            status=base.status,
            organizer_id=base.organizer_id,
        )

    @classmethod
    def to_persistence(cls, conference: Conference) -> ConferenceBase:
        return ConferenceBase(
            conference_id=conference.conference_id,
            title=conference.title,
            short_description=conference.description.short_description,
            full_description=conference.description.full_description,
            start_date=conference.dates.start_date,
            end_date=conference.dates.end_date,
            registration_deadline=conference.dates.registration_deadline,
            location=conference.location,
            max_participants=conference.max_participants,
            status=conference.status,
            organizer_id=conference.organizer_id,
        )
