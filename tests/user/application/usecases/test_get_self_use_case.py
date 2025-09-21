from unittest.mock import Mock
from uuid import uuid4

import pytest

from conference.user.application.dtos.queries.get_user_be_id_query import (
    GetUserByIdQuery,
)
from conference.user.application.dtos.responses.user_dto import UserDTO
from conference.user.application.interfaces.repositories.user_read_repository import (
    IUserReadRepository,
)
from conference.user.application.read_models.user_read_model import UserReadModel
from conference.user.application.usecases.query.get_self_use_case import (
    GetSelfUseCase,
)


@pytest.mark.asyncio
class TestGetSelfUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.user = UserReadModel(self.user_id, "test user")

        self.user_repository = Mock(spec=IUserReadRepository)
        self.user_repository.get_by_id.return_value = self.user

        self.command = GetUserByIdQuery(self.user_id)
        self.use_case = GetSelfUseCase(self.user_repository)

    async def test_execute_success(self) -> None:
        result = await self.use_case.execute(self.command)

        assert isinstance(result, UserDTO)
        assert result.user_id == self.user_id
        assert result.username == self.user.username

        self.user_repository.get_by_id.assert_awaited_once_with(self.user.user_id)
