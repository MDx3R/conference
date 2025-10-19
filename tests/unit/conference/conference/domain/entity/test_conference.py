from datetime import date
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError

from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.domain.value_objects.enums import ConferenceStatus


class TestConferenceCreate:
    def test_create_conference_with_valid_data(self) -> None:
        conference_id = uuid4()
        organizer_id = uuid4()
        description = ConferenceDescription(
            short_description="Test conference", full_description=None
        )
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=date(2025, 5, 1),
        )
        max_participants = 100

        conference = Conference.create(
            conference_id=conference_id,
            title="AI Conference 2025",
            description=description,
            dates=dates,
            location="Moscow",
            organizer_id=organizer_id,
            max_participants=max_participants,
        )

        assert conference.conference_id == conference_id
        assert conference.title == "AI Conference 2025"
        assert conference.status == ConferenceStatus.DRAFT
        assert conference.max_participants == max_participants
        assert conference.organizer_id == organizer_id

    def test_create_conference_without_max_participants(self) -> None:
        conference_id = uuid4()
        organizer_id = uuid4()
        description = ConferenceDescription(
            short_description="Test conference", full_description=None
        )
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=None,
        )

        conference = Conference.create(
            conference_id=conference_id,
            title="Open Conference",
            description=description,
            dates=dates,
            location="Online",
            organizer_id=organizer_id,
        )

        assert conference.max_participants is None

    def test_create_conference_with_empty_title_raises_error(self) -> None:
        conference_id = uuid4()
        organizer_id = uuid4()
        description = ConferenceDescription(
            short_description="Test conference", full_description=None
        )
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=None,
        )

        with pytest.raises(InvariantViolationError, match="title cannot be empty"):
            Conference.create(
                conference_id=conference_id,
                title="   ",
                description=description,
                dates=dates,
                location="Moscow",
                organizer_id=organizer_id,
            )

    def test_create_conference_with_negative_max_participants_raises_error(
        self,
    ) -> None:
        conference_id = uuid4()
        organizer_id = uuid4()
        description = ConferenceDescription(
            short_description="Test conference", full_description=None
        )
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=None,
        )

        with pytest.raises(InvariantViolationError, match="must be positive"):
            Conference.create(
                conference_id=conference_id,
                title="Conference",
                description=description,
                dates=dates,
                location="Moscow",
                organizer_id=organizer_id,
                max_participants=-10,
            )

    def test_create_conference_with_zero_max_participants_raises_error(self) -> None:
        conference_id = uuid4()
        organizer_id = uuid4()
        description = ConferenceDescription(
            short_description="Test conference", full_description=None
        )
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=None,
        )

        with pytest.raises(InvariantViolationError, match="must be positive"):
            Conference.create(
                conference_id=conference_id,
                title="Conference",
                description=description,
                dates=dates,
                location="Moscow",
                organizer_id=organizer_id,
                max_participants=0,
            )


class TestConferencePublish:
    def test_publish_draft_conference(self) -> None:
        conference_id = uuid4()
        organizer_id = uuid4()
        description = ConferenceDescription(
            short_description="Test conference", full_description=None
        )
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=None,
        )

        conference = Conference.create(
            conference_id=conference_id,
            title="Conference",
            description=description,
            dates=dates,
            location="Moscow",
            organizer_id=organizer_id,
        )

        conference.publish()

        assert conference.status == ConferenceStatus.ACTIVE

    def test_publish_active_conference_raises_error(self) -> None:
        conference = Conference(
            conference_id=uuid4(),
            title="Conference",
            description=ConferenceDescription(
                short_description="Test", full_description=None
            ),
            dates=ConferenceDates(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 3),
                registration_deadline=None,
            ),
            location="Moscow",
            max_participants=None,
            status=ConferenceStatus.ACTIVE,
            organizer_id=uuid4(),
        )

        with pytest.raises(InvariantViolationError, match="Only draft"):
            conference.publish()


class TestConferenceCancel:
    def test_cancel_active_conference(self) -> None:
        conference = Conference(
            conference_id=uuid4(),
            title="Conference",
            description=ConferenceDescription(
                short_description="Test", full_description=None
            ),
            dates=ConferenceDates(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 3),
                registration_deadline=None,
            ),
            location="Moscow",
            max_participants=None,
            status=ConferenceStatus.ACTIVE,
            organizer_id=uuid4(),
        )

        conference.cancel()

        assert conference.status == ConferenceStatus.CANCELLED

    def test_cancel_draft_conference(self) -> None:
        conference = Conference(
            conference_id=uuid4(),
            title="Conference",
            description=ConferenceDescription(
                short_description="Test", full_description=None
            ),
            dates=ConferenceDates(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 3),
                registration_deadline=None,
            ),
            location="Moscow",
            max_participants=None,
            status=ConferenceStatus.DRAFT,
            organizer_id=uuid4(),
        )

        conference.cancel()

        assert conference.status == ConferenceStatus.CANCELLED

    def test_cancel_completed_conference_raises_error(self) -> None:
        conference = Conference(
            conference_id=uuid4(),
            title="Conference",
            description=ConferenceDescription(
                short_description="Test", full_description=None
            ),
            dates=ConferenceDates(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 3),
                registration_deadline=None,
            ),
            location="Moscow",
            max_participants=None,
            status=ConferenceStatus.COMPLETED,
            organizer_id=uuid4(),
        )

        with pytest.raises(InvariantViolationError, match="Cannot cancel"):
            conference.cancel()

    def test_cancel_already_cancelled_conference_raises_error(self) -> None:
        conference = Conference(
            conference_id=uuid4(),
            title="Conference",
            description=ConferenceDescription(
                short_description="Test", full_description=None
            ),
            dates=ConferenceDates(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 3),
                registration_deadline=None,
            ),
            location="Moscow",
            max_participants=None,
            status=ConferenceStatus.CANCELLED,
            organizer_id=uuid4(),
        )

        with pytest.raises(InvariantViolationError, match="Cannot cancel"):
            conference.cancel()


class TestConferenceComplete:
    def test_complete_active_conference(self) -> None:
        conference = Conference(
            conference_id=uuid4(),
            title="Conference",
            description=ConferenceDescription(
                short_description="Test", full_description=None
            ),
            dates=ConferenceDates(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 3),
                registration_deadline=None,
            ),
            location="Moscow",
            max_participants=None,
            status=ConferenceStatus.ACTIVE,
            organizer_id=uuid4(),
        )

        conference.complete()

        assert conference.status == ConferenceStatus.COMPLETED

    def test_complete_draft_conference_raises_error(self) -> None:
        conference = Conference(
            conference_id=uuid4(),
            title="Conference",
            description=ConferenceDescription(
                short_description="Test", full_description=None
            ),
            dates=ConferenceDates(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 3),
                registration_deadline=None,
            ),
            location="Moscow",
            max_participants=None,
            status=ConferenceStatus.DRAFT,
            organizer_id=uuid4(),
        )

        with pytest.raises(InvariantViolationError, match="Only active"):
            conference.complete()


class TestConferenceCanAcceptParticipants:
    def test_active_conference_can_accept_participants(self) -> None:
        conference = Conference(
            conference_id=uuid4(),
            title="Conference",
            description=ConferenceDescription(
                short_description="Test", full_description=None
            ),
            dates=ConferenceDates(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 3),
                registration_deadline=None,
            ),
            location="Moscow",
            max_participants=None,
            status=ConferenceStatus.ACTIVE,
            organizer_id=uuid4(),
        )

        assert conference.can_accept_participants() is True

    def test_draft_conference_cannot_accept_participants(self) -> None:
        conference = Conference(
            conference_id=uuid4(),
            title="Conference",
            description=ConferenceDescription(
                short_description="Test", full_description=None
            ),
            dates=ConferenceDates(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 3),
                registration_deadline=None,
            ),
            location="Moscow",
            max_participants=None,
            status=ConferenceStatus.DRAFT,
            organizer_id=uuid4(),
        )

        assert conference.can_accept_participants() is False

    def test_cancelled_conference_cannot_accept_participants(self) -> None:
        conference = Conference(
            conference_id=uuid4(),
            title="Conference",
            description=ConferenceDescription(
                short_description="Test", full_description=None
            ),
            dates=ConferenceDates(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 3),
                registration_deadline=None,
            ),
            location="Moscow",
            max_participants=None,
            status=ConferenceStatus.CANCELLED,
            organizer_id=uuid4(),
        )

        assert conference.can_accept_participants() is False
