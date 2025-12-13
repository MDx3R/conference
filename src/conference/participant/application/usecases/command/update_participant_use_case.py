from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.domain.value_objects.address import Address
from common.domain.value_objects.phone_number import PhoneNumber

from conference.participant.application.dtos.commands.update_participant_command import (
    UpdateParticipantCommand,
)
from conference.participant.application.interfaces.repositories.participant_repository import (
    IParticipantRepository,
)
from conference.participant.application.interfaces.usecases.command.update_participant_use_case import (
    IUpdateParticipantUseCase,
)
from conference.participant.domain.value_objects.about import About
from conference.participant.domain.value_objects.full_name import FullName
from conference.participant.domain.value_objects.workplace import Workplace


class UpdateParticipantUseCase(IUpdateParticipantUseCase):
    def __init__(
        self,
        participant_repository: IParticipantRepository,
        unit_of_work: IUnitOfWork,
    ) -> None:
        self.participant_repository = participant_repository
        self.unit_of_work = unit_of_work

    async def execute(self, command: UpdateParticipantCommand) -> None:
        async with self.unit_of_work:
            participant = await self.participant_repository.get_by_id(command.user_id)

            if command.surname or command.name or command.patronymic is not None:
                full_name = FullName.create(
                    surname=command.surname or participant.full_name.surname,
                    name=command.name or participant.full_name.name,
                    patronymic=command.patronymic
                    if command.patronymic is not None
                    else participant.full_name.patronymic,
                )
                participant.update_full_name(full_name)

            if command.phone_number:
                participant.update_phone_number(PhoneNumber(command.phone_number))

            if command.home_number is not None:
                home_number = (
                    PhoneNumber(command.home_number) if command.home_number else None
                )
                participant.update_home_number(home_number)

            if (
                command.country
                or command.city
                or command.postal_code is not None
                or command.street_address is not None
            ):
                address = Address(
                    country=command.country or participant.address.country,
                    city=command.city or participant.address.city,
                    postal_code=command.postal_code
                    if command.postal_code is not None
                    else participant.address.postal_code,
                    street_address=command.street_address
                    if command.street_address is not None
                    else participant.address.street_address,
                )
                participant.update_address(address)

            if any(
                [
                    command.academic_degree is not None,
                    command.academic_title is not None,
                    command.research_area is not None,
                    command.organization is not None,
                    command.department is not None,
                    command.position is not None,
                ]
            ):
                workplace = None
                if command.organization or (
                    participant.about.workplace
                    and participant.about.workplace.organization
                ):
                    org = command.organization or (
                        participant.about.workplace.organization
                        if participant.about.workplace
                        else None
                    )
                    dept = (
                        command.department
                        if command.department is not None
                        else (
                            participant.about.workplace.department
                            if participant.about.workplace
                            else None
                        )
                    )
                    pos = (
                        command.position
                        if command.position is not None
                        else (
                            participant.about.workplace.position
                            if participant.about.workplace
                            else None
                        )
                    )
                    if org:
                        workplace = Workplace(
                            organization=org, department=dept, position=pos
                        )

                about = About(
                    academic_degree=command.academic_degree
                    if command.academic_degree is not None
                    else participant.about.academic_degree,
                    academic_title=command.academic_title
                    if command.academic_title is not None
                    else participant.about.academic_title,
                    research_area=command.research_area
                    if command.research_area is not None
                    else participant.about.research_area,
                    workplace=workplace,
                )
                participant.update_about(about)

            await self.participant_repository.update(participant)
            await self.unit_of_work.commit()
