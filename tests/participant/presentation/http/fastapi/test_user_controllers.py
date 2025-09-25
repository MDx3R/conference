from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from idp.identity.application.interfaces.services.token_intospector import (
    ITokenIntrospector,
)
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor

from conference.participant.application.dtos.queries.get_user_be_id_query import (
    GetParticipantByIdQuery,
)
from conference.participant.application.dtos.responses.user_dto import ParticipantDTO
from conference.participant.application.interfaces.usecases.query.get_self_use_case import (
    IGetSelfUseCase,
)
from conference.participant.presentation.http.fastapi.controllers import query_router


@pytest.mark.asyncio
class TestParticipantController:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = FastAPI()
        self.app.include_router(query_router)
        self.client: TestClient = TestClient(self.app)

        self.get_self_use_case = AsyncMock(spec=IGetSelfUseCase)
        self.token_introspector = AsyncMock(spec=ITokenIntrospector)

        self.app.dependency_overrides[IGetSelfUseCase] = lambda: self.get_self_use_case
        self.app.dependency_overrides[ITokenIntrospector] = (
            lambda: self.token_introspector
        )

    async def test_me_success(self):
        # Arrange
        user_id = uuid4()
        mock_response = ParticipantDTO(
            user_id=user_id,
            username="testuser",
            surname="Иванов",
            name="Иван",
            patronymic="Иванович",
            phone_number="+79998887766",
            home_number=None,
            academic_degree=None,
            academic_title=None,
            research_area=None,
            organization=None,
            department=None,
            position=None,
            country="Россия",
            city="Москва",
            postal_code=None,
            street_address=None,
        )
        self.get_self_use_case.execute.return_value = mock_response
        self.token_introspector.extract_user.return_value = IdentityDescriptor(
            user_id, mock_response.username
        )

        # Act
        response = self.client.get(
            "/me",
            headers={"Authorization": "Bearer authenticated_token"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "user_id": str(user_id),
            "username": "testuser",
            "surname": "Иванов",
            "name": "Иван",
            "patronymic": "Иванович",
            "phone_number": "+79998887766",
            "home_number": None,
            "academic_degree": None,
            "academic_title": None,
            "research_area": None,
            "organization": None,
            "department": None,
            "position": None,
            "country": "Россия",
            "city": "Москва",
            "postal_code": None,
            "street_address": None,
        }
        self.get_self_use_case.execute.assert_awaited_once_with(
            GetParticipantByIdQuery(user_id)
        )
