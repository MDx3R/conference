from enum import Enum
from typing import ClassVar

from common.infrastructure.app.http_app import IHTTPApp
from common.infrastructure.server.fastapi.middleware.error_middleware import (
    ErrorHandlingMiddleware,
)
from common.infrastructure.server.fastapi.server import FastAPIServer
from idp.auth.application.interfaces.usecases.command.login_use_case import (
    ILoginUseCase,
)
from idp.auth.application.interfaces.usecases.command.logout_use_case import (
    ILogoutUseCase,
)
from idp.auth.application.interfaces.usecases.command.refresh_token_use_case import (
    IRefreshTokenUseCase,
)
from idp.auth.infrastructure.di.container.container import AuthContainer, TokenContainer
from idp.auth.infrastructure.server.fastapi.middleware.token_error_middleware import (
    TokenErrorHandler,
)
from idp.auth.presentation.http.fastapi.controllers import auth_router
from idp.identity.application.interfaces.services.token_intospector import (
    ITokenIntrospector,
)


class AuthApp(IHTTPApp):
    prefix = "/auth"
    tags: ClassVar[list[str | Enum]] = ["Auth"]

    def __init__(
        self,
        auth_container: AuthContainer,
        server: FastAPIServer,
    ) -> None:
        self.auth_container = auth_container
        self.server = server

    def configure_dependencies(self) -> None:
        self.server.override_dependency(
            ILoginUseCase, self.auth_container.login_use_case()
        )
        self.server.override_dependency(
            ILogoutUseCase, self.auth_container.logout_use_case()
        )
        self.server.override_dependency(
            IRefreshTokenUseCase, self.auth_container.refresh_token_use_case()
        )

    def register_routers(self) -> None:
        self.server.register_router(auth_router, self.prefix, self.tags)


class TokenApp(IHTTPApp):
    def __init__(
        self,
        container: TokenContainer,
        server: FastAPIServer,
    ) -> None:
        self.container = container
        self.server = server

    def configure(self) -> None:
        super().configure()
        self.configure_middleware()

    def configure_middleware(self) -> None:
        self.server.use_middleware(
            ErrorHandlingMiddleware,
            handlers=[TokenErrorHandler()],
        )

    def configure_dependencies(self) -> None:
        self.server.override_dependency(
            ITokenIntrospector, self.container.token_introspector()
        )

    def register_routers(self) -> None:
        pass
