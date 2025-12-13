from enum import Enum
from typing import ClassVar

from common.infrastructure.app.http_app import IHTTPApp
from common.infrastructure.server.fastapi.server import FastAPIServer

from conference.conference.application.interfaces.usecases.command.cancel_conference_use_case import (
    ICancelConferenceUseCase,
)
from conference.conference.application.interfaces.usecases.command.complete_conference_use_case import (
    ICompleteConferenceUseCase,
)
from conference.conference.application.interfaces.usecases.command.confirm_stay_period_use_case import (
    IConfirmStayPeriodUseCase,
)
from conference.conference.application.interfaces.usecases.command.create_conference_use_case import (
    ICreateConferenceUseCase,
)
from conference.conference.application.interfaces.usecases.command.mark_thesis_received_use_case import (
    IMarkThesisReceivedUseCase,
)
from conference.conference.application.interfaces.usecases.command.publish_conference_use_case import (
    IPublishConferenceUseCase,
)
from conference.conference.application.interfaces.usecases.command.record_fee_payment_use_case import (
    IRecordFeePaymentUseCase,
)
from conference.conference.application.interfaces.usecases.command.register_participant_use_case import (
    IRegisterParticipantUseCase,
)
from conference.conference.application.interfaces.usecases.command.remove_participant_use_case import (
    IRemoveParticipantUseCase,
)
from conference.conference.application.interfaces.usecases.command.update_conference_use_case import (
    IUpdateConferenceUseCase,
)
from conference.conference.application.interfaces.usecases.query.get_all_conferences_use_case import (
    IGetAllConferencesUseCase,
)
from conference.conference.application.interfaces.usecases.query.get_conference_by_id_use_case import (
    IGetConferenceByIdUseCase,
)
from conference.conference.application.interfaces.usecases.query.get_participants_use_case import (
    IGetParticipantsUseCase,
)
from conference.conference.infrastructure.di.container.container import (
    ConferenceContainer,
)
from conference.conference.presentation.http.fastapi.controllers import (
    conference_router,
)


class ConferenceApp(IHTTPApp):
    prefix = "/conferences"
    tags: ClassVar[list[str | Enum]] = ["Conferences"]

    def __init__(
        self,
        conference_container: ConferenceContainer,
        server: FastAPIServer,
    ) -> None:
        self.conference_container = conference_container
        self.server = server

    def configure_dependencies(self) -> None:
        self.server.override_dependency(
            ICreateConferenceUseCase,
            self.conference_container.create_conference_use_case(),
        )
        self.server.override_dependency(
            IUpdateConferenceUseCase,
            self.conference_container.update_conference_use_case(),
        )
        self.server.override_dependency(
            IPublishConferenceUseCase,
            self.conference_container.publish_conference_use_case(),
        )
        self.server.override_dependency(
            ICancelConferenceUseCase,
            self.conference_container.cancel_conference_use_case(),
        )
        self.server.override_dependency(
            ICompleteConferenceUseCase,
            self.conference_container.complete_conference_use_case(),
        )
        self.server.override_dependency(
            IRegisterParticipantUseCase,
            self.conference_container.register_participant_use_case(),
        )
        self.server.override_dependency(
            IRemoveParticipantUseCase,
            self.conference_container.remove_participant_use_case(),
        )
        self.server.override_dependency(
            IRecordFeePaymentUseCase,
            self.conference_container.record_fee_payment_use_case(),
        )
        self.server.override_dependency(
            IConfirmStayPeriodUseCase,
            self.conference_container.confirm_stay_period_use_case(),
        )
        self.server.override_dependency(
            IMarkThesisReceivedUseCase,
            self.conference_container.mark_thesis_received_use_case(),
        )
        self.server.override_dependency(
            IGetConferenceByIdUseCase,
            self.conference_container.get_conference_by_id_use_case(),
        )
        self.server.override_dependency(
            IGetAllConferencesUseCase,
            self.conference_container.get_all_conferences_use_case(),
        )
        self.server.override_dependency(
            IGetParticipantsUseCase,
            self.conference_container.get_participants_use_case(),
        )

    def register_routers(self) -> None:
        self.server.register_router(conference_router, self.prefix, self.tags)
