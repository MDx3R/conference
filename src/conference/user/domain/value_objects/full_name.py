from dataclasses import dataclass
from typing import Self

from common.domain.exceptions import InvariantViolationError


@dataclass(frozen=True)
class FullName:
    surname: str
    name: str
    patronymic: str | None

    def __post_init__(self) -> None:
        if self.patronymic is not None and not self.patronymic.strip():
            raise InvariantViolationError("Patronymic must be None or non-empty string")
        if not self.surname.strip() or not self.name.strip():
            raise InvariantViolationError("Surname and name must not be empty")

    def short(self) -> str:
        return f"{self.surname} {self.name[0]}."

    def full(self) -> str:
        return f"{self.surname} {self.name} {self.patronymic or ''}".strip()

    @classmethod
    def create(cls, surname: str, name: str, patronymic: str | None) -> Self:
        return cls(surname=surname, name=name, patronymic=patronymic)
