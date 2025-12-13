from dataclasses import dataclass

from conference.conference.domain.value_objects.enums import Currency


@dataclass(frozen=True)
class Fee:
    amount: float
    currency: Currency = Currency.RUB
