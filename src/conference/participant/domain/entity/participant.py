from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.value_objects.address import Address
from common.domain.value_objects.phone_number import PhoneNumber

from conference.participant.domain.value_objects.about import About
from conference.participant.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)
from conference.participant.domain.value_objects.full_name import FullName
from conference.participant.domain.value_objects.workplace import Workplace


@dataclass
class Participant:
    user_id: UUID  # NOTE: Email is part of identity, see identity context
    full_name: FullName
    phone_number: PhoneNumber
    home_number: PhoneNumber | None
    address: Address
    about: About

    def change_home_number(self, number: PhoneNumber) -> None:
        self.home_number = number

    def change_address(self, address: Address) -> None:
        self.address = address

    def change_workplace(self, workplace: Workplace | None) -> None:
        self.about = About(
            self.about.academic_degree,
            self.about.academic_title,
            self.about.research_area,
            workplace,
        )

    def change_about(
        self,
        academic_degree: AcademicDegree | None,
        academic_title: AcademicTitle | None,
        research_area: ResearchArea | None,
    ) -> None:
        self.about = About.create(
            academic_degree,
            academic_title,
            research_area,
            self.about.workplace,
        )

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
