from uuid import uuid4

from common.application.exceptions import NotFoundError
from fastapi import status


def test_get_conference_by_id_success(client, sample_conference_dto) -> None:
    conference_id = sample_conference_dto.conference_id
    response = client.get(f"/conferences/{conference_id}")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["conference_id"] == str(conference_id)


def test_get_conference_by_id_invalid_uuid(client) -> None:
    response = client.get("/conferences/invalid-uuid")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_conference_by_id_not_found(
    client, mock_get_conference_by_id_use_case
) -> None:
    conference_id = uuid4()
    mock_get_conference_by_id_use_case.execute.side_effect = NotFoundError(
        conference_id
    )
    response = client.get(f"/conferences/{conference_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
