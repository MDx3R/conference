from enum import Enum
from typing import ClassVar

from common.infrastructure.app.http_app import IHTTPApp
from common.infrastructure.server.fastapi.server import FastAPIServer

from conference.participant.application.interfaces.usecases.command.register_user_use_case import (
    IRegisterUserUseCase,
)
from conference.participant.application.interfaces.usecases.command.update_participant_use_case import (
    IUpdateParticipantUseCase,
)
from conference.participant.application.interfaces.usecases.query.get_self_use_case import (
    IGetSelfUseCase,
)
from conference.participant.infrastructure.di.container.container import (
    ParticipantContainer,
)
from conference.participant.presentation.http.fastapi.controllers import (
    participant_router,
)


class ParticipantApp(IHTTPApp):
    prefix = "/participants"
    tags: ClassVar[list[str | Enum]] = ["Participants"]

    def __init__(
        self,
        participant_container: ParticipantContainer,
        server: FastAPIServer,
    ) -> None:
        self.participant_container = participant_container
        self.server = server

    def configure_dependencies(self) -> None:
        self.server.override_dependency(
            IRegisterUserUseCase, self.participant_container.register_user_use_case()
        )
        self.server.override_dependency(
            IUpdateParticipantUseCase,
            self.participant_container.update_participant_use_case(),
        )
        self.server.override_dependency(
            IGetSelfUseCase, self.participant_container.get_self_use_case()
        )

    def register_routers(self) -> None:
        self.server.register_router(participant_router, self.prefix, self.tags)
