from dataclasses import dataclass

from common.domain.exceptions import InvariantViolationError


@dataclass(frozen=True)
class Workplace:
    organization: str
    department: str | None
    position: str | None

    def __post_init__(self) -> None:
        if not self.organization.strip():
            raise InvariantViolationError("Organization name cannot be empty")
        if self.department is not None and not self.department.strip():
            raise InvariantViolationError("Department must not be blank")
        if self.position is not None and not self.position.strip():
            raise InvariantViolationError("Position must not be blank")
