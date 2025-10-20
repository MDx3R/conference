from abc import abstractmethod

from common.infrastructure.app.iapp import IApp
from common.infrastructure.server.fastapi.middleware.error_middleware import (
    IHTTPErrorHandler,
)


class IHTTPApp(IApp):
    def configure(self) -> None:
        self.configure_dependencies()
        self.register_routers()

    def error_handlers(self) -> list[IHTTPErrorHandler]:
        return []

    @abstractmethod
    def configure_dependencies(self) -> None: ...

    @abstractmethod
    def register_routers(self) -> None: ...
