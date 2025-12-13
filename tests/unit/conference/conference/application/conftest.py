from unittest.mock import AsyncMock, Mock

import pytest
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork


@pytest.fixture
def mock_uow() -> Mock:
    uow = Mock(spec=IUnitOfWork)
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.commit = AsyncMock()
    return uow
