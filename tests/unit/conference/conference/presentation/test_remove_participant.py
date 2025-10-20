from uuid import uuid4

from fastapi import status


def test_remove_participant_success(client) -> None:
    conference_id = uuid4()
    participant_id = uuid4()
    response = client.delete(
        f"/conferences/{conference_id}/participants/{participant_id}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_remove_participant_invalid_conference_id(client) -> None:
    participant_id = uuid4()
    response = client.delete(f"/conferences/invalid-uuid/participants/{participant_id}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_remove_participant_invalid_participant_id(client) -> None:
    conference_id = uuid4()
    response = client.delete(f"/conferences/{conference_id}/participants/invalid-uuid")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
