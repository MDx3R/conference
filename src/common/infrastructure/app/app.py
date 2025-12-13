import logging

from common.infrastructure.app.http_app import IHTTPApp
from common.infrastructure.app.iapp import IApp
from common.infrastructure.config.config import RunEnvironment
from common.infrastructure.config.server_config import ServerConfig
from common.infrastructure.server.fastapi.middleware.error_middleware import (
    ApplicationErrorHandler,
    DomainErrorHandler,
    ErrorHandlingMiddleware,
    IHTTPErrorHandler,
    RepositoryErrorHandler,
)
from common.infrastructure.server.fastapi.middleware.logging_middleware import (
    LoggingMiddleware,
)
from common.infrastructure.server.fastapi.server import FastAPIServer


class App(IApp):
    def __init__(
        self,
        env: RunEnvironment,
        logger: logging.Logger,
        server: FastAPIServer,
        config: ServerConfig,
    ) -> None:
        self.env = env
        self.logger = logger
        self.server = server
        self.config = config
        self.sub_apps: list[IHTTPApp] = []

    def configure(self) -> None:
        all_handlers: list[IHTTPErrorHandler] = []

        for sub_app in self.sub_apps:
            all_handlers.extend(sub_app.error_handlers())

        all_handlers.extend(
            [
                RepositoryErrorHandler(),
                ApplicationErrorHandler(),
                DomainErrorHandler(),
            ]
        )

        self.server.include_cors_middleware()
        self.server.use_middleware(LoggingMiddleware, logger=self.logger)
        self.server.use_middleware(
            ErrorHandlingMiddleware,
            handlers=all_handlers,
        )

    def add_app(self, *apps: IApp) -> None:
        for app in apps:
            app.configure()
            self.logger.info(
                f"Sub-application '{app.__class__.__name__}' registered successfully"
            )

    def run(self) -> None:
        import uvicorn  # noqa: PLC0415

        self.logger.info(
            "Service starting",
            extra={"env": self.env, "host": self.config.host, "port": self.config.port},
        )
        uvicorn.run(self.server.get_app(), host=self.config.host, port=self.config.port)
        self.logger.info(
            "Service stopped",
            extra={"host": self.config.host, "port": self.config.port},
        )

    def get_server(self) -> FastAPIServer:
        return self.server

    def get_logger(self) -> logging.Logger:
        return self.logger
