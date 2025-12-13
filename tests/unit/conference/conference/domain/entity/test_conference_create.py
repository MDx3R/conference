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


def test_create_conference_with_valid_data() -> None:
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


def test_create_conference_without_max_participants() -> None:
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


def test_create_conference_with_empty_title_raises_error() -> None:
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


def test_create_conference_with_negative_max_participants_raises_error() -> None:
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


def test_create_conference_with_zero_max_participants_raises_error() -> None:
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
