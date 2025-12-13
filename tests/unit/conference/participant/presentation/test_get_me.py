from common.application.exceptions import NotFoundError
from fastapi import status


def test_get_me_success(client, sample_participant_dto) -> None:
    response = client.get("/participants/me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] == str(sample_participant_dto.user_id)
    assert data["username"] == "testuser"
    assert data["surname"] == "Ivanov"
    assert data["name"] == "Ivan"
    assert data["phone_number"] == "+79991234567"


def test_get_me_not_found(
    client, mock_get_self_use_case, mock_authenticated_user
) -> None:
    mock_get_self_use_case.execute.side_effect = NotFoundError(
        mock_authenticated_user.identity_id
    )
    response = client.get("/participants/me")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_me_minimal_data(
    client, mock_get_self_use_case, sample_participant_dto
) -> None:
    sample_participant_dto.patronymic = None
    sample_participant_dto.home_number = None
    sample_participant_dto.academic_degree = None
    sample_participant_dto.organization = None
    mock_get_self_use_case.execute.return_value = sample_participant_dto

    response = client.get("/participants/me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["patronymic"] is None
    assert data["home_number"] is None
