from dataclasses import dataclass

from common.domain.exceptions import InvariantViolationError


@dataclass(frozen=True)
class PhoneNumber:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise InvariantViolationError("Phone number cannot be empty")
