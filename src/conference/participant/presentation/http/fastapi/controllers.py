from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from idp.identity.presentation.http.fastapi.auth import (
    get_descriptor,
    require_authenticated,
)

from conference.participant.application.dtos.commands.update_participant_command import (
    UpdateParticipantCommand,
)
from conference.participant.application.dtos.queries.get_user_be_id_query import (
    GetParticipantByIdQuery,
)
from conference.participant.application.interfaces.usecases.command.update_participant_use_case import (
    IUpdateParticipantUseCase,
)
from conference.participant.application.interfaces.usecases.query.get_self_use_case import (
    IGetSelfUseCase,
)
from conference.participant.presentation.http.dto.request import (
    UpdateParticipantRequest,
)
from conference.participant.presentation.http.dto.response import ParticipantResponse


participant_router = APIRouter()


@cbv(participant_router)
class ParticipantController:
    get_self_use_case: IGetSelfUseCase = Depends()
    update_participant_use_case: IUpdateParticipantUseCase = Depends()

    @participant_router.get(
        "/me",
        dependencies=[Depends(require_authenticated)],
    )
    async def get_me(
        self, user: Annotated[IdentityDescriptor, Depends(get_descriptor)]
    ) -> ParticipantResponse:
        result = await self.get_self_use_case.execute(
            GetParticipantByIdQuery(user.identity_id)
        )
        return ParticipantResponse(**asdict(result))

    @participant_router.patch(
        "/me",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_authenticated)],
    )
    async def update_me(
        self,
        request: UpdateParticipantRequest,
        user: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        command = UpdateParticipantCommand(
            user_id=user.identity_id,
            surname=request.surname,
            name=request.name,
            patronymic=request.patronymic,
            phone_number=request.phone_number,
            home_number=request.home_number,
            academic_degree=request.academic_degree,
            academic_title=request.academic_title,
            research_area=request.research_area,
            organization=request.organization,
            department=request.department,
            position=request.position,
            country=request.country,
            city=request.city,
            postal_code=request.postal_code,
            street_address=request.street_address,
        )
        await self.update_participant_use_case.execute(command)
