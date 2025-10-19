from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from conference.participant.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)


class ParticipantBase(Base):
    __tablename__ = "participants"

    user_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    surname: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    patronymic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    home_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    academic_degree: Mapped[AcademicDegree | None] = mapped_column(
        Enum(AcademicDegree, native_enum=False), nullable=True
    )
    academic_title: Mapped[AcademicTitle | None] = mapped_column(
        Enum(AcademicTitle, native_enum=False), nullable=True
    )
    research_area: Mapped[ResearchArea | None] = mapped_column(
        Enum(ResearchArea, native_enum=False), nullable=True
    )
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    position: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    street_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
