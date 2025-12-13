from uuid import uuid4

from common.application.exceptions import NotFoundError
from fastapi import status


def test_publish_conference_success(client) -> None:
    conference_id = uuid4()
    response = client.post(f"/conferences/{conference_id}/publish", json={})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_publish_conference_invalid_uuid(client) -> None:
    response = client.post("/conferences/invalid-uuid/publish", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_publish_conference_not_found(client, mock_publish_conference_use_case) -> None:
    conference_id = uuid4()
    mock_publish_conference_use_case.execute.side_effect = NotFoundError(conference_id)
    response = client.post(f"/conferences/{conference_id}/publish", json={})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cancel_conference_success(client) -> None:
    conference_id = uuid4()
    response = client.post(f"/conferences/{conference_id}/cancel", json={})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_cancel_conference_invalid_uuid(client) -> None:
    response = client.post("/conferences/invalid-uuid/cancel", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_complete_conference_success(client) -> None:
    conference_id = uuid4()
    response = client.post(f"/conferences/{conference_id}/complete", json={})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_complete_conference_invalid_uuid(client) -> None:
    response = client.post("/conferences/invalid-uuid/complete", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_conference_action_no_body(client) -> None:
    conference_id = uuid4()

    response = client.post(f"/conferences/{conference_id}/publish")
    assert response.status_code in (
        status.HTTP_204_NO_CONTENT,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
