from uuid import uuid4

from common.application.exceptions import NotFoundError
from fastapi import status


def test_publish_conference_success(client, mock_publish_conference_use_case):
    conference_id = uuid4()
    mock_publish_conference_use_case.execute.return_value = None

    response = client.post(f"/conferences/{conference_id}/publish", json={})

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_publish_conference_use_case.execute.assert_called_once()


def test_publish_conference_invalid_uuid(client):
    response = client.post("/conferences/invalid-uuid/publish", json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_publish_conference_not_found(client, mock_publish_conference_use_case):
    conference_id = uuid4()
    mock_publish_conference_use_case.execute.side_effect = NotFoundError(conference_id)

    response = client.post(f"/conferences/{conference_id}/publish", json={})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cancel_conference_success(client, mock_cancel_conference_use_case):
    conference_id = uuid4()
    mock_cancel_conference_use_case.execute.return_value = None

    response = client.post(f"/conferences/{conference_id}/cancel", json={})

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_cancel_conference_use_case.execute.assert_called_once()


def test_cancel_conference_invalid_uuid(client):
    response = client.post("/conferences/invalid-uuid/cancel", json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_complete_conference_success(client, mock_complete_conference_use_case):
    conference_id = uuid4()
    mock_complete_conference_use_case.execute.return_value = None

    response = client.post(f"/conferences/{conference_id}/complete", json={})

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_complete_conference_use_case.execute.assert_called_once()


def test_complete_conference_invalid_uuid(client):
    response = client.post("/conferences/invalid-uuid/complete", json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_conference_action_without_request_body(
    client, mock_publish_conference_use_case
):
    conference_id = uuid4()
    mock_publish_conference_use_case.execute.return_value = None

    response = client.post(f"/conferences/{conference_id}/publish")

    assert response.status_code in [
        status.HTTP_204_NO_CONTENT,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ]
