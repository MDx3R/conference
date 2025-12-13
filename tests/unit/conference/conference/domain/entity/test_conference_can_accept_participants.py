from datetime import date
from uuid import uuid4

from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.domain.value_objects.enums import ConferenceStatus


def test_active_conference_can_accept_participants() -> None:
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


def test_draft_conference_cannot_accept_participants() -> None:
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


def test_cancelled_conference_cannot_accept_participants() -> None:
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
