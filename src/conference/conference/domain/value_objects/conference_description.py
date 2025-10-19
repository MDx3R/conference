from dataclasses import dataclass


SHORT_DESCRIPTION_MAX_LENGTH = 500


@dataclass(frozen=True)
class ConferenceDescription:
    short_description: str
    full_description: str | None = None

    def __post_init__(self) -> None:
        if not self.short_description.strip():
            raise ValueError("Short description cannot be empty")

        if len(self.short_description) > SHORT_DESCRIPTION_MAX_LENGTH:
            raise ValueError(
                f"Short description must not exceed {SHORT_DESCRIPTION_MAX_LENGTH} characters"
            )

        if self.full_description is not None:
            if not self.full_description.strip():
                raise ValueError("Full description cannot be empty if provided")
