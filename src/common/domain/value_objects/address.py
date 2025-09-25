from dataclasses import dataclass

from common.domain.exceptions import InvariantViolationError


@dataclass(frozen=True)
class Address:
    country: str
    city: str
    postal_code: str | None
    street_address: str | None

    def __post_init__(self) -> None:
        if not self.country.strip() or not self.city.strip():
            raise InvariantViolationError("Country and city are required")
        if self.postal_code is not None and not self.postal_code.strip():
            raise InvariantViolationError(
                "Postal code must be None or non-empty string"
            )
        if self.street_address is not None and not self.street_address.strip():
            raise InvariantViolationError(
                "Street address must be None or non-empty string"
            )
