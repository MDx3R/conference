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


def test_update_title_success() -> None:
    conference = Conference(
        conference_id=uuid4(),
        title="Old Title",
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

    new_title = "New Title"
    conference.update(title=new_title)

    assert conference.title == new_title


def test_update_description_success() -> None:
    conference = Conference(
        conference_id=uuid4(),
        title="Conference",
        description=ConferenceDescription(
            short_description="Old", full_description=None
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

    new_description = ConferenceDescription(
        short_description="New short", full_description="New full"
    )
    conference.update(description=new_description)

    assert conference.description.short_description == "New short"
    assert conference.description.full_description == "New full"


def test_update_dates_success() -> None:
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

    new_dates = ConferenceDates(
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 5),
        registration_deadline=date(2025, 6, 15),
    )
    conference.update(dates=new_dates)

    assert conference.dates.start_date == date(2025, 7, 1)
    assert conference.dates.end_date == date(2025, 7, 5)
    assert conference.dates.registration_deadline == date(2025, 6, 15)


def test_update_location_success() -> None:
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

    new_location = "St. Petersburg"
    conference.update(location=new_location)

    assert conference.location == new_location


def test_update_max_participants_success() -> None:
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
        max_participants=100,
        status=ConferenceStatus.DRAFT,
        organizer_id=uuid4(),
    )

    new_max_participants = 200
    conference.update(max_participants=new_max_participants)

    assert conference.max_participants == new_max_participants


def test_update_multiple_fields_success() -> None:
    conference = Conference(
        conference_id=uuid4(),
        title="Old Title",
        description=ConferenceDescription(
            short_description="Old", full_description=None
        ),
        dates=ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=None,
        ),
        location="Moscow",
        max_participants=100,
        status=ConferenceStatus.DRAFT,
        organizer_id=uuid4(),
    )

    conference.update(
        title="New Title",
        location="Online",
        max_participants=150,
    )

    expected_max_participants = 150
    assert conference.title == "New Title"
    assert conference.location == "Online"
    assert conference.max_participants == expected_max_participants


def test_update_completed_conference_fails() -> None:
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

    with pytest.raises(
        InvariantViolationError, match="Cannot update completed conference"
    ):
        conference.update(title="New Title")


def test_update_cancelled_conference_fails() -> None:
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

    with pytest.raises(
        InvariantViolationError, match="Cannot update cancelled conference"
    ):
        conference.update(title="New Title")


def test_update_with_empty_title_fails() -> None:
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

    with pytest.raises(
        InvariantViolationError, match="Conference title cannot be empty"
    ):
        conference.update(title="   ")


def test_update_with_negative_max_participants_fails() -> None:
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
        max_participants=100,
        status=ConferenceStatus.DRAFT,
        organizer_id=uuid4(),
    )

    with pytest.raises(
        InvariantViolationError, match="Max participants must be positive"
    ):
        conference.update(max_participants=-10)


def test_update_with_zero_max_participants_fails() -> None:
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
        max_participants=100,
        status=ConferenceStatus.DRAFT,
        organizer_id=uuid4(),
    )

    with pytest.raises(
        InvariantViolationError, match="Max participants must be positive"
    ):
        conference.update(max_participants=0)


def test_update_with_none_values_does_not_change_fields() -> None:
    original_title = "Conference"
    original_location = "Moscow"
    original_max = 100

    conference = Conference(
        conference_id=uuid4(),
        title=original_title,
        description=ConferenceDescription(
            short_description="Test", full_description=None
        ),
        dates=ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=None,
        ),
        location=original_location,
        max_participants=original_max,
        status=ConferenceStatus.DRAFT,
        organizer_id=uuid4(),
    )

    conference.update()

    assert conference.title == original_title
    assert conference.location == original_location
    assert conference.max_participants == original_max
