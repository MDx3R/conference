import pytest

from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)


class TestConferenceDescriptionCreate:
    def test_create_with_short_description_only(self) -> None:
        description = ConferenceDescription(
            short_description="AI Conference 2025", full_description=None
        )

        assert description.short_description == "AI Conference 2025"
        assert description.full_description is None

    def test_create_with_both_descriptions(self) -> None:
        description = ConferenceDescription(
            short_description="AI Conference 2025",
            full_description="A comprehensive conference about artificial intelligence",
        )

        assert description.short_description == "AI Conference 2025"
        assert (
            description.full_description
            == "A comprehensive conference about artificial intelligence"
        )

    def test_create_with_empty_short_description_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Short description cannot be empty"):
            ConferenceDescription(short_description="   ", full_description=None)

    def test_create_with_too_long_short_description_raises_error(self) -> None:
        long_text = "A" * 501

        with pytest.raises(ValueError, match="must not exceed 500 characters"):
            ConferenceDescription(short_description=long_text, full_description=None)

    def test_create_with_empty_full_description_raises_error(self) -> None:
        with pytest.raises(
            ValueError, match="Full description cannot be empty if provided"
        ):
            ConferenceDescription(
                short_description="Valid short", full_description="   "
            )

    def test_create_with_maximum_length_short_description(self) -> None:
        max_length = 500
        max_length_text = "A" * max_length

        description = ConferenceDescription(
            short_description=max_length_text, full_description=None
        )

        assert len(description.short_description) == max_length
