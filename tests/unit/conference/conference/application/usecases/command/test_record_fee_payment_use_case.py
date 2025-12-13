from datetime import date
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from conference.conference.application.dtos.commands.record_fee_payment_command import (
    RecordFeePaymentCommand,
)
from conference.conference.application.interfaces.repositories.participation_repository import (
    IParticipationRepository,
)
from conference.conference.application.usecases.command.record_fee_payment_use_case import (
    RecordFeePaymentUseCase,
)
from conference.conference.domain.entity.participation import Participation
from conference.conference.domain.value_objects.enums import Currency


@pytest.mark.asyncio
class TestRecordFeePaymentUseCase:
    @pytest.fixture(autouse=True)
    def setup(self, mock_uow) -> None:
        self.conference_id = uuid4()
        self.participant_id = uuid4()
        self.amount = 5000.0
        self.payment_date = date(2025, 5, 15)
        self.currency = Currency.RUB

        self.participation = Mock(spec=Participation)
        self.participation.record_fee_payment = Mock()

        self.participation_repository = Mock(spec=IParticipationRepository)
        self.participation_repository.get_by_id = AsyncMock(
            return_value=self.participation
        )
        self.participation_repository.update = AsyncMock()

        self.uow = mock_uow

        self.command = RecordFeePaymentCommand(
            conference_id=self.conference_id,
            participant_id=self.participant_id,
            amount=self.amount,
            payment_date=self.payment_date,
            currency=self.currency,
        )

        self.use_case = RecordFeePaymentUseCase(
            participation_repository=self.participation_repository,
            uow=self.uow,
        )

    async def test_record_fee_payment_success(self) -> None:
        await self.use_case.execute(self.command)

        self.participation_repository.get_by_id.assert_awaited_once_with(
            self.conference_id, self.participant_id
        )
        self.participation.record_fee_payment.assert_called_once_with(
            amount=self.amount, payment_date=self.payment_date, currency=self.currency
        )
        self.participation_repository.update.assert_awaited_once_with(
            self.participation
        )
        self.uow.commit.assert_awaited_once()
