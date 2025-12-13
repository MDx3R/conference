from dataclasses import asdict
from datetime import date
from typing import Annotated
from uuid import UUID

from common.application.exceptions import NotFoundError
from common.presentation.http.dto.response import IDResponse
from fastapi import APIRouter, Depends, Query, status
from fastapi_utils.cbv import cbv
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from idp.identity.presentation.http.fastapi.auth import (
    get_descriptor,
    require_authenticated,
)

from conference.conference.application.dtos.commands.cancel_conference_command import (
    CancelConferenceCommand,
)
from conference.conference.application.dtos.commands.complete_conference_command import (
    CompleteConferenceCommand,
)
from conference.conference.application.dtos.commands.confirm_stay_period_command import (
    ConfirmStayPeriodCommand,
)
from conference.conference.application.dtos.commands.create_conference_command import (
    CreateConferenceCommand,
)
from conference.conference.application.dtos.commands.mark_thesis_received_command import (
    MarkThesisReceivedCommand,
)
from conference.conference.application.dtos.commands.publish_conference_command import (
    PublishConferenceCommand,
)
from conference.conference.application.dtos.commands.record_fee_payment_command import (
    RecordFeePaymentCommand,
)
from conference.conference.application.dtos.commands.register_participant_command import (
    RegisterParticipantCommand,
)
from conference.conference.application.dtos.commands.remove_participant_command import (
    RemoveParticipantCommand,
)
from conference.conference.application.dtos.commands.update_conference_command import (
    UpdateConferenceCommand,
)
from conference.conference.application.dtos.queries.get_all_conferences_query import (
    GetAllConferencesQuery,
)
from conference.conference.application.dtos.queries.get_conference_by_id_query import (
    GetConferenceByIdQuery,
)
from conference.conference.application.dtos.queries.get_participants_query import (
    GetParticipantsQuery,
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
from conference.conference.domain.value_objects.submission import Submission
from conference.conference.presentation.http.dto.request import (
    CancelConferenceRequest,
    CompleteConferenceRequest,
    ConfirmStayPeriodRequest,
    CreateConferenceRequest,
    MarkThesisReceivedRequest,
    PublishConferenceRequest,
    RecordFeePaymentRequest,
    RegisterParticipantRequest,
    UpdateConferenceRequest,
)
from conference.conference.presentation.http.dto.response import (
    ConferenceResponse,
    ParticipationWithParticipantResponse,
)


conference_router = APIRouter()


@cbv(conference_router)
class ConferenceController:
    create_conference_use_case: ICreateConferenceUseCase = Depends()
    update_conference_use_case: IUpdateConferenceUseCase = Depends()
    publish_conference_use_case: IPublishConferenceUseCase = Depends()
    cancel_conference_use_case: ICancelConferenceUseCase = Depends()
    complete_conference_use_case: ICompleteConferenceUseCase = Depends()
    get_conference_by_id_use_case: IGetConferenceByIdUseCase = Depends()
    get_all_conferences_use_case: IGetAllConferencesUseCase = Depends()

    @conference_router.post(
        "/",
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_authenticated)],
    )
    async def create_conference(
        self,
        request: CreateConferenceRequest,
        user: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> IDResponse:
        command = CreateConferenceCommand(
            title=request.title,
            short_description=request.short_description,
            full_description=request.full_description,
            start_date=request.start_date,
            end_date=request.end_date,
            registration_deadline=request.registration_deadline,
            location=request.location,
            max_participants=request.max_participants,
            organizer_id=user.identity_id,
        )
        conference_id = await self.create_conference_use_case.execute(command)
        return IDResponse(id=conference_id)

    @conference_router.get("/")
    async def get_all_conferences(
        self,
        status_filter: Annotated[ConferenceStatus | None, Query(alias="status")] = None,
        organizer_id: Annotated[UUID | None, Query()] = None,
    ) -> list[ConferenceResponse]:
        query = GetAllConferencesQuery(
            status=status_filter,
            organizer_id=str(organizer_id) if organizer_id else None,
        )
        conferences = await self.get_all_conferences_use_case.execute(query)
        return [ConferenceResponse(**asdict(c)) for c in conferences]

    @conference_router.get("/{conference_id}")
    async def get_conference(
        self,
        conference_id: UUID,
    ) -> ConferenceResponse:
        query = GetConferenceByIdQuery(conference_id=conference_id)
        conference = await self.get_conference_by_id_use_case.execute(query)

        if conference is None:
            raise NotFoundError(conference_id)

        return ConferenceResponse(**asdict(conference))

    @conference_router.patch(
        "/{conference_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_authenticated)],
    )
    async def update_conference(
        self,
        conference_id: UUID,
        request: UpdateConferenceRequest,
        user: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        command = UpdateConferenceCommand(
            conference_id=conference_id,
            organizer_id=user.identity_id,
            title=request.title,
            short_description=request.short_description,
            full_description=request.full_description,
            start_date=request.start_date,
            end_date=request.end_date,
            registration_deadline=request.registration_deadline,
            location=request.location,
            max_participants=request.max_participants,
        )
        await self.update_conference_use_case.execute(command)

    @conference_router.post(
        "/{conference_id}/publish",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_authenticated)],
    )
    async def publish_conference(
        self, conference_id: UUID, request: PublishConferenceRequest
    ) -> None:
        command = PublishConferenceCommand(conference_id=conference_id)
        await self.publish_conference_use_case.execute(command)

    @conference_router.post(
        "/{conference_id}/cancel",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_authenticated)],
    )
    async def cancel_conference(
        self, conference_id: UUID, request: CancelConferenceRequest
    ) -> None:
        command = CancelConferenceCommand(conference_id=conference_id)
        await self.cancel_conference_use_case.execute(command)

    @conference_router.post(
        "/{conference_id}/complete",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_authenticated)],
    )
    async def complete_conference(
        self, conference_id: UUID, request: CompleteConferenceRequest
    ) -> None:
        command = CompleteConferenceCommand(conference_id=conference_id)
        await self.complete_conference_use_case.execute(command)


@cbv(conference_router)
class ParticipationController:
    register_participant_use_case: IRegisterParticipantUseCase = Depends()
    remove_participant_use_case: IRemoveParticipantUseCase = Depends()
    record_fee_payment_use_case: IRecordFeePaymentUseCase = Depends()
    confirm_stay_period_use_case: IConfirmStayPeriodUseCase = Depends()
    mark_thesis_received_use_case: IMarkThesisReceivedUseCase = Depends()
    get_participants_use_case: IGetParticipantsUseCase = Depends()

    @conference_router.post(
        "/{conference_id}/participants",
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_authenticated)],
    )
    async def register_participant(
        self,
        conference_id: UUID,
        request: RegisterParticipantRequest,
        user: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        submission = None
        if request.submission:
            submission = Submission(
                topic=request.submission.topic,
                thesis_received=request.submission.thesis_received,
            )

        command = RegisterParticipantCommand(
            conference_id=conference_id,
            participant_id=user.identity_id,
            role=request.role,
            application_date=request.application_date,
            needs_hotel=request.needs_hotel,
            first_invitation_date=request.first_invitation_date,
            submission=submission,
        )
        await self.register_participant_use_case.execute(command)

    @conference_router.get("/{conference_id}/participants")
    async def get_participants(  # noqa: PLR0913
        self,
        conference_id: UUID,
        invitation_date: Annotated[date | None, Query()] = None,
        fee_paid: Annotated[bool | None, Query()] = None,
        fee_payment_date_from: Annotated[date | None, Query()] = None,
        fee_payment_date_to: Annotated[date | None, Query()] = None,
        city: Annotated[str | None, Query()] = None,
        needs_hotel: Annotated[bool | None, Query()] = None,
        has_submission: Annotated[bool | None, Query()] = None,
    ) -> list[ParticipationWithParticipantResponse]:
        query = GetParticipantsQuery(
            conference_id=conference_id,
            invitation_date=invitation_date,
            fee_paid=fee_paid,
            fee_payment_date_from=fee_payment_date_from,
            fee_payment_date_to=fee_payment_date_to,
            city=city,
            needs_hotel=needs_hotel,
            has_submission=has_submission,
        )
        participations = await self.get_participants_use_case.execute(query)
        return [
            ParticipationWithParticipantResponse(**asdict(p)) for p in participations
        ]

    @conference_router.delete(
        "/{conference_id}/participants/{participant_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_authenticated)],
    )
    async def remove_participant(
        self, conference_id: UUID, participant_id: UUID
    ) -> None:
        command = RemoveParticipantCommand(
            conference_id=conference_id, participant_id=participant_id
        )
        await self.remove_participant_use_case.execute(command)

    @conference_router.post(
        "/{conference_id}/participants/{participant_id}/fee",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_authenticated)],
    )
    async def record_fee_payment(
        self,
        conference_id: UUID,
        participant_id: UUID,
        request: RecordFeePaymentRequest,
    ) -> None:
        command = RecordFeePaymentCommand(
            conference_id=conference_id,
            participant_id=participant_id,
            amount=request.amount,
            payment_date=request.payment_date,
            currency=request.currency,
        )
        await self.record_fee_payment_use_case.execute(command)

    @conference_router.post(
        "/{conference_id}/participants/{participant_id}/stay-period",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_authenticated)],
    )
    async def confirm_stay_period(
        self,
        conference_id: UUID,
        participant_id: UUID,
        request: ConfirmStayPeriodRequest,
    ) -> None:
        command = ConfirmStayPeriodCommand(
            conference_id=conference_id,
            participant_id=participant_id,
            arrival_date=request.arrival_date,
            departure_date=request.departure_date,
        )
        await self.confirm_stay_period_use_case.execute(command)

    @conference_router.post(
        "/{conference_id}/participants/{participant_id}/thesis",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_authenticated)],
    )
    async def mark_thesis_received(
        self,
        conference_id: UUID,
        participant_id: UUID,
        request: MarkThesisReceivedRequest,
    ) -> None:
        command = MarkThesisReceivedCommand(
            conference_id=conference_id, participant_id=participant_id
        )
        await self.mark_thesis_received_use_case.execute(command)
