from datetime import date
from uuid import uuid4

from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.domain.value_objects.enums import ConferenceStatus
from conference.conference.infrastructure.database.postgres.sqlalchemy.mappers.conference_mapper import (
    ConferenceMapper,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.models.conference_base import (
    ConferenceBase,
)


class TestConferenceMapper:
    def get_conference(self) -> Conference:
        conference_id = uuid4()
        organizer_id = uuid4()
        title = "AI Conference 2025"
        description = ConferenceDescription(
            short_description="Annual AI conference",
            full_description="Comprehensive AI conference",
        )
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=date(2025, 5, 1),
        )
        location = "Moscow"
        max_participants = 100

        return Conference.create(
            conference_id=conference_id,
            title=title,
            description=description,
            dates=dates,
            location=location,
            organizer_id=organizer_id,
            max_participants=max_participants,
        )

    def test_to_persistence(self):
        conference = self.get_conference()
        base = ConferenceMapper.to_persistence(conference)

        assert isinstance(base, ConferenceBase)
        assert base.conference_id == conference.conference_id
        assert base.title == conference.title
        assert base.short_description == conference.description.short_description
        assert base.full_description == conference.description.full_description
        assert base.start_date == conference.dates.start_date
        assert base.end_date == conference.dates.end_date
        assert base.registration_deadline == conference.dates.registration_deadline
        assert base.location == conference.location
        assert base.max_participants == conference.max_participants
        assert base.status == conference.status
        assert base.organizer_id == conference.organizer_id

    def test_to_domain(self):
        conference_id = uuid4()
        organizer_id = uuid4()
        title = "AI Conference 2025"
        short_description = "Annual AI conference"
        full_description = "Comprehensive AI conference"
        start_date = date(2025, 6, 1)
        end_date = date(2025, 6, 3)
        registration_deadline = date(2025, 5, 1)
        location = "Moscow"
        max_participants = 100
        status = ConferenceStatus.DRAFT

        base = ConferenceBase(
            conference_id=conference_id,
            title=title,
            short_description=short_description,
            full_description=full_description,
            start_date=start_date,
            end_date=end_date,
            registration_deadline=registration_deadline,
            location=location,
            max_participants=max_participants,
            status=status,
            organizer_id=organizer_id,
        )

        conference = ConferenceMapper.to_domain(base)

        assert isinstance(conference, Conference)
        assert conference.conference_id == conference_id
        assert conference.title == title
        assert conference.description.short_description == short_description
        assert conference.description.full_description == full_description
        assert conference.dates.start_date == start_date
        assert conference.dates.end_date == end_date
        assert conference.dates.registration_deadline == registration_deadline
        assert conference.location == location
        assert conference.max_participants == max_participants
        assert conference.status == status
        assert conference.organizer_id == organizer_id

    def test_roundtrip_with_optional_fields(self):
        conference = self.get_conference()
        base = ConferenceMapper.to_persistence(conference)
        restored = ConferenceMapper.to_domain(base)

        assert restored == conference

    def test_roundtrip_without_optional_fields(self):
        conference_id = uuid4()
        organizer_id = uuid4()
        description = ConferenceDescription(
            short_description="Test",
            full_description=None,
        )
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 1),
            registration_deadline=None,
        )

        conference = Conference.create(
            conference_id=conference_id,
            title="Simple Conference",
            description=description,
            dates=dates,
            location="Online",
            organizer_id=organizer_id,
            max_participants=None,
        )

        base = ConferenceMapper.to_persistence(conference)
        restored = ConferenceMapper.to_domain(base)

        assert restored == conference
