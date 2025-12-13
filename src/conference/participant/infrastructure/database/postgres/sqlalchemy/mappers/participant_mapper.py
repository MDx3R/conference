from common.domain.value_objects.address import Address
from common.domain.value_objects.phone_number import PhoneNumber

from conference.participant.domain.entity.participant import Participant
from conference.participant.domain.value_objects.about import About
from conference.participant.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)
from conference.participant.domain.value_objects.full_name import FullName
from conference.participant.domain.value_objects.workplace import Workplace
from conference.participant.infrastructure.database.postgres.sqlalchemy.models.participant_base import (
    ParticipantBase,
)


class ParticipantMapper:
    @staticmethod
    def to_domain(model: ParticipantBase) -> Participant:
        fullname = FullName.create(
            surname=model.surname,
            name=model.name,
            patronymic=model.patronymic,
        )
        phone_number = PhoneNumber(model.phone_number)
        home_number = PhoneNumber(model.home_number) if model.home_number else None

        address = Address(
            country=model.country,
            city=model.city,
            postal_code=model.postal_code,
            street_address=model.street_address,
        )

        workplace = None
        if model.organization:
            workplace = Workplace(
                organization=model.organization,
                department=model.department,
                position=model.position,
            )

        about = About(
            academic_degree=model.academic_degree or AcademicDegree.NONE,
            academic_title=model.academic_title or AcademicTitle.NONE,
            research_area=model.research_area or ResearchArea.NONE,
            workplace=workplace,
        )

        return Participant.create(
            user_id=model.user_id,
            full_name=fullname,
            phone_number=phone_number,
            home_number=home_number,
            address=address,
            about=about,
        )

    @staticmethod
    def to_persistence(participant: Participant) -> ParticipantBase:
        return ParticipantBase(
            user_id=participant.user_id,
            username="",
            surname=participant.full_name.surname,
            name=participant.full_name.name,
            patronymic=participant.full_name.patronymic,
            phone_number=participant.phone_number.value,
            home_number=participant.home_number.value
            if participant.home_number
            else None,
            academic_degree=participant.about.academic_degree,
            academic_title=participant.about.academic_title,
            research_area=participant.about.research_area,
            organization=(
                participant.about.workplace.organization
                if participant.about.workplace
                else None
            ),
            department=(
                participant.about.workplace.department
                if participant.about.workplace
                else None
            ),
            position=(
                participant.about.workplace.position
                if participant.about.workplace
                else None
            ),
            country=participant.address.country,
            city=participant.address.city,
            postal_code=participant.address.postal_code,
            street_address=participant.address.street_address,
        )
