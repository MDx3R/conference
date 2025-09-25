from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from idp.identity.presentation.http.fastapi.auth import (
    get_descriptor,
    require_authenticated,
)

from conference.participant.application.dtos.queries.get_user_be_id_query import (
    GetParticipantByIdQuery,
)
from conference.participant.application.interfaces.usecases.query.get_self_use_case import (
    IGetSelfUseCase,
)
from conference.participant.presentation.http.dto.response import ParticipantResponse


query_router = APIRouter()


@cbv(query_router)
class ParticipantQueryController:
    get_self_use_case: IGetSelfUseCase = Depends()

    @query_router.get(
        "/me",
        dependencies=[Depends(require_authenticated)],
    )
    async def me(
        self, participant: Annotated[IdentityDescriptor, Depends(get_descriptor)]
    ) -> ParticipantResponse:
        result = await self.get_self_use_case.execute(
            GetParticipantByIdQuery(participant.identity_id)
        )
        return ParticipantResponse(**asdict(result))
