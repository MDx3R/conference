from dataclasses import dataclass
from datetime import date
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from common.application.exceptions import (
    ApplicationError,
    NotFoundError,
    RepositoryError,
)
from common.domain.exceptions import DomainError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from idp.identity.presentation.http.fastapi.auth import (
    get_descriptor,
    require_authenticated,
)

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
from conference.conference.domain.value_objects.enums import ConferenceStatus
from conference.conference.presentation.http.fastapi.controllers import (
    conference_router,
)


@dataclass
class ConferenceDTO:
    conference_id: UUID
    title: str
    short_description: str
    full_description: str | None
    start_date: date
    end_date: date
    registration_deadline: date | None
    location: str
    max_participants: int | None
    organizer_id: UUID
    status: ConferenceStatus


@pytest.fixture
def sample_conference_dto() -> ConferenceDTO:
    return ConferenceDTO(
        conference_id=uuid4(),
        title="Test Conference",
        short_description="Short desc",
        full_description="Full desc",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        registration_deadline=date(2025, 5, 1),
        location="Moscow",
        max_participants=100,
        organizer_id=uuid4(),
        status=ConferenceStatus.DRAFT,
    )


@pytest.fixture
def mock_authenticated_user() -> IdentityDescriptor:
    return IdentityDescriptor(identity_id=uuid4(), username="testuser")


@pytest.fixture
def mock_create_conference_use_case() -> AsyncMock:
    mock = AsyncMock(spec=ICreateConferenceUseCase)
    mock.execute = AsyncMock(return_value=uuid4())
    return mock


@pytest.fixture
def mock_update_conference_use_case() -> AsyncMock:
    mock = AsyncMock(spec=IUpdateConferenceUseCase)
    mock.execute = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_publish_conference_use_case() -> AsyncMock:
    mock = AsyncMock(spec=IPublishConferenceUseCase)
    mock.execute = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_cancel_conference_use_case() -> AsyncMock:
    mock = AsyncMock(spec=ICancelConferenceUseCase)
    mock.execute = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_complete_conference_use_case() -> AsyncMock:
    mock = AsyncMock(spec=ICompleteConferenceUseCase)
    mock.execute = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_get_conference_by_id_use_case(
    sample_conference_dto: ConferenceDTO,
) -> AsyncMock:
    mock = AsyncMock(spec=IGetConferenceByIdUseCase)
    mock.execute = AsyncMock(return_value=sample_conference_dto)
    return mock


@pytest.fixture
def mock_get_all_conferences_use_case() -> AsyncMock:
    mock = AsyncMock(spec=IGetAllConferencesUseCase)
    mock.execute = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_register_participant_use_case() -> AsyncMock:
    mock = AsyncMock(spec=IRegisterParticipantUseCase)
    mock.execute = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_remove_participant_use_case() -> AsyncMock:
    mock = AsyncMock(spec=IRemoveParticipantUseCase)
    mock.execute = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_record_fee_payment_use_case() -> AsyncMock:
    mock = AsyncMock(spec=IRecordFeePaymentUseCase)
    mock.execute = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_confirm_stay_period_use_case() -> AsyncMock:
    mock = AsyncMock(spec=IConfirmStayPeriodUseCase)
    mock.execute = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_mark_thesis_received_use_case() -> AsyncMock:
    mock = AsyncMock(spec=IMarkThesisReceivedUseCase)
    mock.execute = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_get_participants_use_case() -> AsyncMock:
    mock = AsyncMock(spec=IGetParticipantsUseCase)
    mock.execute = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": type(exc).__name__, "detail": str(exc)},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(
        request: Request, exc: NotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": type(exc).__name__, "detail": str(exc)},
        )

    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        request: Request, exc: ApplicationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": type(exc).__name__, "detail": str(exc)},
        )

    @app.exception_handler(RepositoryError)
    async def repository_error_handler(
        request: Request, exc: RepositoryError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": type(exc).__name__, "detail": str(exc)},
        )

    return app


@pytest.fixture
def conference_app(  # noqa: PLR0913
    app: FastAPI,
    mock_create_conference_use_case: AsyncMock,
    mock_publish_conference_use_case: AsyncMock,
    mock_cancel_conference_use_case: AsyncMock,
    mock_complete_conference_use_case: AsyncMock,
    mock_update_conference_use_case: AsyncMock,
    mock_get_conference_by_id_use_case: AsyncMock,
    mock_get_all_conferences_use_case: AsyncMock,
    mock_register_participant_use_case: AsyncMock,
    mock_remove_participant_use_case: AsyncMock,
    mock_record_fee_payment_use_case: AsyncMock,
    mock_confirm_stay_period_use_case: AsyncMock,
    mock_mark_thesis_received_use_case: AsyncMock,
    mock_get_participants_use_case: AsyncMock,
    mock_authenticated_user: IdentityDescriptor,
) -> FastAPI:
    app.include_router(conference_router, prefix="/conferences")

    app.dependency_overrides[ICreateConferenceUseCase] = (
        lambda: mock_create_conference_use_case
    )
    app.dependency_overrides[IPublishConferenceUseCase] = (
        lambda: mock_publish_conference_use_case
    )
    app.dependency_overrides[ICancelConferenceUseCase] = (
        lambda: mock_cancel_conference_use_case
    )
    app.dependency_overrides[ICompleteConferenceUseCase] = (
        lambda: mock_complete_conference_use_case
    )
    app.dependency_overrides[IUpdateConferenceUseCase] = (
        lambda: mock_update_conference_use_case
    )
    app.dependency_overrides[IGetConferenceByIdUseCase] = (
        lambda: mock_get_conference_by_id_use_case
    )
    app.dependency_overrides[IGetAllConferencesUseCase] = (
        lambda: mock_get_all_conferences_use_case
    )
    app.dependency_overrides[IRegisterParticipantUseCase] = (
        lambda: mock_register_participant_use_case
    )
    app.dependency_overrides[IRemoveParticipantUseCase] = (
        lambda: mock_remove_participant_use_case
    )
    app.dependency_overrides[IRecordFeePaymentUseCase] = (
        lambda: mock_record_fee_payment_use_case
    )
    app.dependency_overrides[IConfirmStayPeriodUseCase] = (
        lambda: mock_confirm_stay_period_use_case
    )
    app.dependency_overrides[IMarkThesisReceivedUseCase] = (
        lambda: mock_mark_thesis_received_use_case
    )
    app.dependency_overrides[IGetParticipantsUseCase] = (
        lambda: mock_get_participants_use_case
    )

    async def mock_auth() -> IdentityDescriptor:
        return mock_authenticated_user

    app.dependency_overrides[get_descriptor] = mock_auth
    app.dependency_overrides[require_authenticated] = lambda: None

    return app


@pytest.fixture
def client(conference_app: FastAPI) -> TestClient:
    return TestClient(conference_app)
