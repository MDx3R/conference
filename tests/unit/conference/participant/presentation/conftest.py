from dataclasses import dataclass
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

from conference.participant.application.interfaces.usecases.command.update_participant_use_case import (
    IUpdateParticipantUseCase,
)
from conference.participant.application.interfaces.usecases.query.get_self_use_case import (
    IGetSelfUseCase,
)
from conference.participant.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)
from conference.participant.presentation.http.fastapi.controllers import (
    participant_router,
)


@dataclass
class ParticipantDTO:
    user_id: UUID
    username: str
    surname: str
    name: str
    patronymic: str | None
    phone_number: str
    home_number: str | None
    academic_degree: AcademicDegree | None
    academic_title: AcademicTitle | None
    research_area: ResearchArea | None
    organization: str | None
    department: str | None
    position: str | None
    country: str
    city: str
    postal_code: str | None
    street_address: str | None


@pytest.fixture
def sample_participant_dto() -> ParticipantDTO:
    return ParticipantDTO(
        user_id=uuid4(),
        username="testuser",
        surname="Ivanov",
        name="Ivan",
        patronymic="Ivanovich",
        phone_number="+79991234567",
        home_number="+74951234567",
        academic_degree=AcademicDegree.CANDIDATE,
        academic_title=AcademicTitle.DOCENT,
        research_area=ResearchArea.COMPUTER_SCIENCE,
        organization="MSU",
        department="CS Department",
        position="Senior Researcher",
        country="Russia",
        city="Moscow",
        postal_code="123456",
        street_address="Leninsky Avenue 1",
    )


@pytest.fixture
def mock_authenticated_user() -> IdentityDescriptor:
    return IdentityDescriptor(identity_id=uuid4(), username="testuser")


@pytest.fixture
def mock_get_self_use_case(sample_participant_dto: ParticipantDTO) -> AsyncMock:
    mock = AsyncMock(spec=IGetSelfUseCase)
    mock.execute = AsyncMock(return_value=sample_participant_dto)
    return mock


@pytest.fixture
def mock_update_participant_use_case() -> AsyncMock:
    mock = AsyncMock(spec=IUpdateParticipantUseCase)
    mock.execute = AsyncMock(return_value=None)
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
def participant_app(
    app: FastAPI,
    mock_get_self_use_case: AsyncMock,
    mock_update_participant_use_case: AsyncMock,
    mock_authenticated_user: IdentityDescriptor,
) -> FastAPI:
    app.include_router(participant_router, prefix="/participants")

    app.dependency_overrides[IGetSelfUseCase] = lambda: mock_get_self_use_case
    app.dependency_overrides[IUpdateParticipantUseCase] = (
        lambda: mock_update_participant_use_case
    )

    async def mock_auth() -> IdentityDescriptor:
        return mock_authenticated_user

    app.dependency_overrides[get_descriptor] = mock_auth
    app.dependency_overrides[require_authenticated] = lambda: None

    return app


@pytest.fixture
def client(participant_app: FastAPI) -> TestClient:
    return TestClient(participant_app)
