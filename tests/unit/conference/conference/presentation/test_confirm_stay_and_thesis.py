from uuid import uuid4

from common.domain.exceptions import InvariantViolationError
from fastapi import status


def test_confirm_stay_period_success(client) -> None:
    conference_id = uuid4()
    participant_id = uuid4()
    payload = {"arrival_date": "2025-05-20", "departure_date": "2025-05-25"}
    response = client.post(
        f"/conferences/{conference_id}/participants/{participant_id}/stay-period",
        json=payload,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_confirm_stay_period_invalid_order(client) -> None:
    conference_id = uuid4()
    participant_id = uuid4()
    payload = {"arrival_date": "2025-05-26", "departure_date": "2025-05-25"}
    response = client.post(
        f"/conferences/{conference_id}/participants/{participant_id}/stay-period",
        json=payload,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_confirm_stay_invalid_uuid_path(client) -> None:
    payload = {"arrival_date": "2025-05-20", "departure_date": "2025-05-25"}
    response = client.post(
        "/conferences/invalid-uuid/participants/invalid-uuid/stay-period", json=payload
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_mark_thesis_received_success(client) -> None:
    conference_id = uuid4()
    participant_id = uuid4()
    response = client.post(
        f"/conferences/{conference_id}/participants/{participant_id}/thesis", json={}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_mark_thesis_received_domain_error(
    client, mock_mark_thesis_received_use_case
) -> None:
    conference_id = uuid4()
    participant_id = uuid4()
    mock_mark_thesis_received_use_case.execute.side_effect = InvariantViolationError(
        "no submission"
    )
    response = client.post(
        f"/conferences/{conference_id}/participants/{participant_id}/thesis", json={}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_mark_thesis_invalid_uuids(client) -> None:
    response = client.post(
        "/conferences/invalid-uuid/participants/invalid-uuid/thesis", json={}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
