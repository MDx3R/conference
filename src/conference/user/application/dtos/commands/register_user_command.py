from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserCommand:
    username: str
    password: str
    surname: str
    name: str
    patronymic: str | None
    phone_number: str
    country: str
    city: str
