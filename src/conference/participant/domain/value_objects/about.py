from dataclasses import dataclass

from conference.participant.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)
from conference.participant.domain.value_objects.workplace import Workplace


@dataclass(frozen=True)
class About:
    academic_degree: AcademicDegree
    academic_title: AcademicTitle
    research_area: ResearchArea
    workplace: Workplace | None
