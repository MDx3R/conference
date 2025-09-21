from typing import Annotated
from uuid import uuid4

from common.presentation.http.dto.response import IDResponse
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from idp.identity.presentation.http.fastapi.auth import (
    get_token,
    require_authenticated,
)


identity_router = APIRouter()


@cbv(identity_router)
class IdentityController:
    @identity_router.post(
        "/register",
        response_model=IDResponse,
        dependencies=[Depends(require_authenticated)],
    )
    async def register(self, token: Annotated[str, Depends(get_token)]) -> IDResponse:
        return IDResponse(id=uuid4())  # stub
