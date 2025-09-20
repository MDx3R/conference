from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from identity.domain.value_objects.descriptor import IdentityDescriptor
from identity.presentation.http.fastapi.auth import (
    get_descriptor,
    require_authenticated,
)
from user.application.dtos.queries.get_user_be_id_query import GetUserByIdQuery
from user.application.interfaces.usecases.query.get_self_use_case import IGetSelfUseCase
from user.presentation.http.dto.response import UserResponse


query_router = APIRouter()


@cbv(query_router)
class UserQueryController:
    get_self_use_case: IGetSelfUseCase = Depends()

    @query_router.get(
        "/me",
        response_model=UserResponse,
        dependencies=[Depends(require_authenticated)],
    )
    async def me(
        self, user: Annotated[IdentityDescriptor, Depends(get_descriptor)]
    ) -> UserResponse:
        result = await self.get_self_use_case.execute(
            GetUserByIdQuery(user.identity_id)
        )
        return UserResponse(**asdict(result))
