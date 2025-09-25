from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from conference.participant.domain.entity.participant import Participant
from conference.participant.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)


@dataclass(frozen=True, kw_only=True)
class ParticipantFactoryDTO:
    surname: str
    name: str
    patronymic: str | None = None
    phone_number: str
    home_number: str | None = None
    academic_degree: AcademicDegree | None = None
    academic_title: AcademicTitle | None = None
    research_area: ResearchArea | None = None
    organization: str | None = None
    department: str | None = None
    position: str | None = None
    country: str
    city: str
    postal_code: str | None = None
    street_address: str | None = None


class IParticipantFactory(ABC):
    @abstractmethod
    def create(self, user_id: UUID, data: ParticipantFactoryDTO) -> Participant: ...
