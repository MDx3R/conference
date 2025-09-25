from enum import Enum


class AcademicDegree(str, Enum):
    NONE = "Нет"
    CANDIDATE = "Кандидат наук"
    DOCTOR = "Доктор наук"


class AcademicTitle(str, Enum):
    NONE = "Нет"
    DOCENT = "Доцент"
    PROFESSOR = "Профессор"


class ResearchArea(Enum):
    NONE = "Нет"
    MATHEMATICS = "Математика"
    PHYSICS = "Физика"
    COMPUTER_SCIENCE = "Информатика"
    BIOLOGY = "Биология"
    OTHER = "Другое"
