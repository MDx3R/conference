from enum import Enum


class Role(Enum):
    SPEAKER = "Докладчик"
    PARTICIPANT = "Участник"


class Currency(Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
