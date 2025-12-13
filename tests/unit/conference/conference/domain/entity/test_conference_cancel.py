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


def test_cancel_active_conference() -> None:
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


def test_cancel_draft_conference() -> None:
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


def test_cancel_completed_conference_raises_error() -> None:
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


def test_cancel_already_cancelled_conference_raises_error() -> None:
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
