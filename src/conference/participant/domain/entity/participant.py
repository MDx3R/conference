from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.value_objects.address import Address
from common.domain.value_objects.phone_number import PhoneNumber

from conference.participant.domain.value_objects.about import About
from conference.participant.domain.value_objects.full_name import FullName


@dataclass
class Participant:
    user_id: UUID  # NOTE: Email is part of identity, see identity context
    full_name: FullName
    phone_number: PhoneNumber
    home_number: PhoneNumber | None
    address: Address
    about: About

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        user_id: UUID,
        full_name: FullName,
        phone_number: PhoneNumber,
        home_number: PhoneNumber | None,
        address: Address,
        about: About,
    ) -> Self:
        return cls(
            user_id=user_id,
            full_name=full_name,
            phone_number=phone_number,
            home_number=home_number,
            about=about,
            address=address,
        )
