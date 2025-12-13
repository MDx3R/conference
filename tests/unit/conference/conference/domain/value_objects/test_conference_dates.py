from datetime import date

import pytest

from conference.conference.domain.value_objects.conference_dates import ConferenceDates


class TestConferenceDatesCreate:
    def test_create_with_valid_dates(self) -> None:
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=date(2025, 5, 1),
        )

        assert dates.start_date == date(2025, 6, 1)
        assert dates.end_date == date(2025, 6, 3)
        assert dates.registration_deadline == date(2025, 5, 1)

    def test_create_without_registration_deadline(self) -> None:
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=None,
        )

        assert dates.registration_deadline is None

    def test_create_with_end_date_before_start_date_raises_error(self) -> None:
        with pytest.raises(ValueError, match="End date cannot be earlier"):
            ConferenceDates(
                start_date=date(2025, 6, 3),
                end_date=date(2025, 6, 1),
                registration_deadline=None,
            )

    def test_create_with_registration_deadline_after_start_raises_error(self) -> None:
        with pytest.raises(
            ValueError, match="Registration deadline cannot be after conference start"
        ):
            ConferenceDates(
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 3),
                registration_deadline=date(2025, 6, 2),
            )

    def test_duration_days_single_day_conference(self) -> None:
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 1),
            registration_deadline=None,
        )

        assert dates.duration_days == 1

    def test_duration_days_multi_day_conference(self) -> None:
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 5),
            registration_deadline=None,
        )

        expected_duration_days = 5
        assert dates.duration_days == expected_duration_days
