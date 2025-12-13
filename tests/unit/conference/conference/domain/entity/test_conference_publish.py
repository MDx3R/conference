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


def test_publish_draft_conference() -> None:
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


def test_publish_active_conference_raises_error() -> None:
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
