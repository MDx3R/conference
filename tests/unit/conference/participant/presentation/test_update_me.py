from typing import Any

from common.domain.exceptions import InvariantViolationError
from fastapi import status


def test_update_me_all_fields(client) -> None:
    payload = {
        "surname": "Petrov",
        "name": "Petr",
        "patronymic": "Petrovich",
        "phone_number": "+79991234567",
        "home_number": "+74951234567",
        "academic_degree": "Кандидат наук",
        "academic_title": "Доцент",
        "research_area": "Информатика",
        "organization": "MSU",
        "department": "CS Department",
        "position": "Senior Researcher",
        "country": "Russia",
        "city": "Moscow",
        "postal_code": "123456",
        "street_address": "Leninsky Avenue 1",
    }
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_partial_update_surname_only(client) -> None:
    payload = {"surname": "Sidorov"}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_partial_update_phone_and_city(client) -> None:
    payload = {"phone_number": "+79999999999", "city": "Saint Petersburg"}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_set_optional_fields_to_null(client) -> None:
    payload = {
        "patronymic": None,
        "home_number": None,
        "academic_degree": None,
        "organization": None,
    }
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_empty_payload(client) -> None:
    payload: dict[str, Any] = {}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_empty_string_surname(client) -> None:
    payload = {"surname": ""}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code in (
        status.HTTP_204_NO_CONTENT,
        status.HTTP_400_BAD_REQUEST,
    )


def test_update_me_whitespace_only_name(client) -> None:
    payload = {"name": "   "}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code in (
        status.HTTP_204_NO_CONTENT,
        status.HTTP_400_BAD_REQUEST,
    )


def test_update_me_invalid_academic_degree(client) -> None:
    payload = {"academic_degree": "INVALID_DEGREE"}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_me_invalid_academic_title(client) -> None:
    payload = {"academic_title": "PROFESSOR_EMERITUS"}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_me_invalid_research_area(client) -> None:
    payload = {"research_area": "QUANTUM_PHYSICS"}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_me_valid_enum_values(client) -> None:
    payload = {
        "academic_degree": "Доктор наук",
        "academic_title": "Профессор",
        "research_area": "Математика",
    }
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_phone_number_format(client) -> None:
    payload = {"phone_number": "+1234567890"}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_domain_error(client, mock_update_participant_use_case) -> None:
    mock_update_participant_use_case.execute.side_effect = InvariantViolationError(
        "Invalid data"
    )
    payload = {"surname": "Petrov"}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_me_extra_fields_ignored(client) -> None:
    payload = {"surname": "Petrov", "extra_field": "should be ignored"}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_null_for_all_optional_fields(client) -> None:
    payload = {
        "surname": None,
        "name": None,
        "patronymic": None,
        "phone_number": None,
        "home_number": None,
        "academic_degree": None,
        "academic_title": None,
        "research_area": None,
        "organization": None,
        "department": None,
        "position": None,
        "country": None,
        "city": None,
        "postal_code": None,
        "street_address": None,
    }
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_me_wrong_type_for_phone(client) -> None:
    payload = {"phone_number": 123456789}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_me_boolean_instead_of_string(client) -> None:
    payload = {"surname": True}
    response = client.patch("/participants/me", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
