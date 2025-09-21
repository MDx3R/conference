from common.presentation.http.dto.response import IDResponse
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv
from idp.identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from idp.identity.application.exceptions import UsernameAlreadyTakenError
from idp.identity.application.interfaces.usecases.command.create_identity_use_case import (
    ICreateIdentityUseCase,
)
from idp.identity.presentation.http.dto.request import RegisterUserRequest
from idp.identity.presentation.http.fastapi.auth import require_unauthenticated


identity_router = APIRouter()


@cbv(identity_router)
class IdentityController:
    create_identity_use_case: ICreateIdentityUseCase = Depends()

    @identity_router.post(
        "/register",
        dependencies=[Depends(require_unauthenticated)],
        response_model=IDResponse,
    )
    async def register(self, request: RegisterUserRequest) -> IDResponse:
        try:
            identity_id = await self.create_identity_use_case.execute(
                CreateIdentityCommand(request.username, request.password)
            )
            return IDResponse(id=identity_id)
        except UsernameAlreadyTakenError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "UsernameAlreadyTakenError",
                    "username": exc.username,
                    "message": str(exc),
                },
            ) from exc
