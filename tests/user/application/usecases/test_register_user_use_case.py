from unittest.mock import Mock
from uuid import uuid4

import pytest
from common.domain.value_objects.address import Address
from common.domain.value_objects.phone_number import PhoneNumber
from idp.identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from idp.identity.application.exceptions import UsernameAlreadyTakenError
from idp.identity.application.interfaces.services.identity_service import (
    IIdentityService,
)

from conference.user.application.dtos.commands.register_user_command import (
    RegisterUserCommand,
)
from conference.user.application.interfaces.repositories.user_repository import (
    IUserRepository,
)
from conference.user.application.usecases.command.register_user_use_case import (
    RegisterUserUseCase,
)
from conference.user.domain.entity.user import User
from conference.user.domain.interfaces.user_factory import IUserFactory, UserFactoryDTO
from conference.user.domain.value_objects.about import About
from conference.user.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)
from conference.user.domain.value_objects.full_name import FullName
from conference.user.domain.value_objects.workplace import Workplace


@pytest.mark.asyncio
class TestRegisterUserUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()
        self.full_name = FullName.create(
            surname="Иванов", name="Иван", patronymic="Иванович"
        )
        self.phone_number = PhoneNumber("+79998887766")
        self.address = Address(
            country="Россия",
            city="Москва",
            postal_code="123456",
            street_address="ул. Пушкина, д. 1",
        )
        self.workplace = Workplace(
            organization="МГУ", department="Мехмат", position="Доцент"
        )
        self.about = About(
            academic_degree=AcademicDegree.CANDIDATE,
            academic_title=AcademicTitle.DOCENT,
            research_area=ResearchArea.MATHEMATICS,
            workplace=self.workplace,
        )
        self.user = User(
            user_id=self.user_id,
            full_name=self.full_name,
            phone_number=self.phone_number,
            home_number=None,
            address=self.address,
            about=self.about,
        )

        self.identity_service = Mock(spec=IIdentityService)
        self.identity_service.create_identity.return_value = self.user_id

        self.user_factory = Mock(spec=IUserFactory)
        self.user_factory.create.return_value = self.user

        self.user_repository = Mock(spec=IUserRepository)

        self.command = RegisterUserCommand(
            username="testuser",
            password="password",
            surname="Иванов",
            name="Иван",
            patronymic="Иванович",
            phone_number="+79998887766",
            country="Россия",
            city="Москва",
        )
        self.use_case = RegisterUserUseCase(
            user_factory=self.user_factory,
            user_repository=self.user_repository,
            identity_service=self.identity_service,
        )

    async def test_register_success(self):
        result = await self.use_case.execute(self.command)

        assert result == self.user_id

        self.identity_service.create_identity.assert_awaited_once_with(
            CreateIdentityCommand(self.command.username, self.command.password)
        )
        self.user_factory.create.assert_called_once_with(
            self.user_id,
            UserFactoryDTO(
                surname=self.command.surname,
                name=self.command.name,
                patronymic=self.command.patronymic,
                phone_number=self.command.phone_number,
                country=self.command.country,
                city=self.command.city,
            ),
        )
        self.user_repository.add.assert_awaited_once_with(self.user)

    async def test_register_username_already_taken(self):
        self.identity_service.create_identity.side_effect = UsernameAlreadyTakenError(
            self.command.username
        )

        with pytest.raises(UsernameAlreadyTakenError):
            await self.use_case.execute(self.command)

        self.identity_service.create_identity.assert_awaited_once_with(
            CreateIdentityCommand(self.command.username, self.command.password)
        )
        self.user_repository.add.assert_not_awaited()
