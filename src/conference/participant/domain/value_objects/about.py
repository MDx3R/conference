from dataclasses import dataclass
from typing import Self

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

    @classmethod
    def create(
        cls,
        academic_degree: AcademicDegree | None,
        academic_title: AcademicTitle | None,
        research_area: ResearchArea | None,
        workplace: Workplace | None,
    ) -> Self:
        academic_degree = academic_degree or AcademicDegree.NONE
        academic_title = academic_title or AcademicTitle.NONE
        research_area = research_area or ResearchArea.NONE
        return cls(
            academic_degree=academic_degree,
            academic_title=academic_title,
            research_area=research_area,
            workplace=workplace,
        )
