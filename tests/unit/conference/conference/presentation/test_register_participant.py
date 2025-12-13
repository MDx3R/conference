from uuid import uuid4

from fastapi import status

from conference.conference.application.exceptions import (
    ConferenceFullError,
    ParticipantAlreadyRegisteredError,
)


DATE_APPL = "2025-05-15"
DATE_INV1 = "2025-05-01"


def test_register_participant_success(client) -> None:
    conference_id = uuid4()
    payload = {
        "role": "Докладчик",
        "application_date": DATE_APPL,
        "needs_hotel": True,
        "first_invitation_date": DATE_INV1,
        "submission": {"topic": "AI in Healthcare", "thesis_received": False},
    }
    response = client.post(f"/conferences/{conference_id}/participants", json=payload)
    assert response.status_code == status.HTTP_201_CREATED


def test_register_participant_without_optional_fields(client) -> None:
    conference_id = uuid4()
    payload = {"role": "Участник", "application_date": DATE_APPL, "needs_hotel": False}
    response = client.post(f"/conferences/{conference_id}/participants", json=payload)
    assert response.status_code == status.HTTP_201_CREATED


def test_register_participant_missing_required_fields(client) -> None:
    conference_id = uuid4()
    payload = {"role": "Докладчик"}
    response = client.post(f"/conferences/{conference_id}/participants", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_participant_invalid_role(client) -> None:
    conference_id = uuid4()
    payload = {"role": "SPEAKER", "application_date": DATE_APPL, "needs_hotel": False}
    response = client.post(f"/conferences/{conference_id}/participants", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_participant_invalid_conference_id(client) -> None:
    payload = {"role": "Докладчик", "application_date": DATE_APPL, "needs_hotel": False}
    response = client.post("/conferences/invalid-uuid/participants", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_participant_invalid_date_format(client) -> None:
    conference_id = uuid4()
    payload = {
        "role": "Докладчик",
        "application_date": "15-05-2025",
        "needs_hotel": False,
    }
    response = client.post(f"/conferences/{conference_id}/participants", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_participant_needs_hotel_wrong_type(client) -> None:
    conference_id = uuid4()
    payload = {"role": "Докладчик", "application_date": DATE_APPL, "needs_hotel": 123}
    response = client.post(f"/conferences/{conference_id}/participants", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_participant_null_required_field(client) -> None:
    conference_id = uuid4()
    payload = {"role": "Докладчик", "application_date": None, "needs_hotel": False}
    response = client.post(f"/conferences/{conference_id}/participants", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_participant_submission_invalid_structure(client) -> None:
    conference_id = uuid4()
    payload = {
        "role": "Докладчик",
        "application_date": DATE_APPL,
        "needs_hotel": False,
        "submission": {"topic": "AI"},
    }
    response = client.post(f"/conferences/{conference_id}/participants", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_participant_submission_empty_topic(client) -> None:
    conference_id = uuid4()
    payload = {
        "role": "Докладчик",
        "application_date": DATE_APPL,
        "needs_hotel": False,
        "submission": {"topic": "", "thesis_received": False},
    }
    response = client.post(f"/conferences/{conference_id}/participants", json=payload)
    assert response.status_code in [
        status.HTTP_201_CREATED,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ]


def test_register_participant_conference_full(
    client, mock_register_participant_use_case
) -> None:
    conference_id = uuid4()
    mock_register_participant_use_case.execute.side_effect = ConferenceFullError(
        conference_id
    )
    payload = {"role": "Докладчик", "application_date": DATE_APPL, "needs_hotel": False}
    response = client.post(f"/conferences/{conference_id}/participants", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_register_participant_already_registered(
    client, mock_register_participant_use_case
) -> None:
    conference_id = uuid4()
    participant_id = uuid4()
    mock_register_participant_use_case.execute.side_effect = (
        ParticipantAlreadyRegisteredError(conference_id, participant_id)
    )
    payload = {"role": "Докладчик", "application_date": DATE_APPL, "needs_hotel": False}
    response = client.post(f"/conferences/{conference_id}/participants", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
