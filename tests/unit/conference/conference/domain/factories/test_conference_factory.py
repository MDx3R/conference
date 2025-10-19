from datetime import date
from uuid import uuid4

from conference.conference.domain.factories.conference_factory import ConferenceFactory
from conference.conference.domain.interfaces.conference_factory import (
    ConferenceFactoryDTO,
)
from conference.conference.domain.value_objects.enums import ConferenceStatus


class TestConferenceFactory:
    def test_create_conference_with_all_fields(self) -> None:
        factory = ConferenceFactory()
        conference_id = uuid4()
        organizer_id = uuid4()
        title = "AI Conference 2025"
        short_description = "Annual AI conference"
        full_description = "Comprehensive AI conference covering latest trends"
        start_date = date(2025, 6, 1)
        end_date = date(2025, 6, 3)
        registration_deadline = date(2025, 5, 1)
        location = "Moscow"
        max_participants = 100

        dto = ConferenceFactoryDTO(
            title=title,
            short_description=short_description,
            full_description=full_description,
            start_date=start_date,
            end_date=end_date,
            registration_deadline=registration_deadline,
            location=location,
            max_participants=max_participants,
            organizer_id=organizer_id,
        )

        conference = factory.create(conference_id=conference_id, data=dto)

        assert conference.conference_id == conference_id
        assert conference.title == title
        assert conference.description.short_description == short_description
        assert conference.description.full_description == full_description
        assert conference.dates.start_date == start_date
        assert conference.dates.end_date == end_date
        assert conference.dates.registration_deadline == registration_deadline
        assert conference.location == location
        assert conference.max_participants == max_participants
        assert conference.organizer_id == organizer_id
        assert conference.status == ConferenceStatus.DRAFT

    def test_create_conference_without_optional_fields(self) -> None:
        factory = ConferenceFactory()
        conference_id = uuid4()
        organizer_id = uuid4()

        dto = ConferenceFactoryDTO(
            title="Simple Conference",
            short_description="Simple description",
            full_description=None,
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 1),
            registration_deadline=None,
            location="Online",
            max_participants=None,
            organizer_id=organizer_id,
        )

        conference = factory.create(conference_id=conference_id, data=dto)

        assert conference.description.full_description is None
        assert conference.dates.registration_deadline is None
        assert conference.max_participants is None
