from common.application.exceptions import NotFoundError
from common.domain.interfaces.clock import IClock
from identity.application.dtos.models.auth_tokens import AuthTokens
from identity.application.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
)
from identity.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from identity.application.interfaces.services.token_service import ITokenRefresher
from identity.infrastructure.services.jwt.token_issuer import JWTTokenIssuer
from identity.infrastructure.services.jwt.token_revoker import JWTTokenRevoker


class JWTTokenRefresher(ITokenRefresher):
    def __init__(
        self,
        clock: IClock,
        token_issuer: JWTTokenIssuer,
        token_revoker: JWTTokenRevoker,
        refresh_token_repository: IRefreshTokenRepository,
    ) -> None:
        self.clock = clock
        self.token_issuer = token_issuer
        self.token_revoker = token_revoker
        self.refresh_token_repository = refresh_token_repository

    async def refresh_tokens(self, refresh_token: str) -> AuthTokens:
        try:
            token = await self.refresh_token_repository.get(refresh_token)
        except NotFoundError as e:
            raise InvalidTokenError from e
        if token.is_expired(self.clock.now().value):
            raise TokenExpiredError()
        if token.is_revoked():
            raise TokenRevokedError()

        await self.token_revoker.revoke_refresh_token(refresh_token)
        return await self.token_issuer.issue_tokens(token.identity_id)
