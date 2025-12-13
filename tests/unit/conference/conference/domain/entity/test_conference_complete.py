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


def test_complete_active_conference() -> None:
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


def test_complete_draft_conference_raises_error() -> None:
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
