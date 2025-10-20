from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

from common.application.exceptions import NotFoundError
from fastapi import status

from conference.conference.domain.value_objects.enums import ConferenceStatus


@dataclass
class ConferenceDTO:
    conference_id: UUID
    title: str
    short_description: str
    full_description: str | None
    start_date: date
    end_date: date
    registration_deadline: date | None
    location: str
    max_participants: int | None
    organizer_id: UUID
    status: ConferenceStatus


def test_get_all_conferences_empty_list(client, mock_get_all_conferences_use_case):
    mock_get_all_conferences_use_case.execute.return_value = []

    response = client.get("/conferences/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_all_conferences_with_results(client, mock_get_all_conferences_use_case):
    conference_id = uuid4()
    organizer_id = uuid4()

    conference_dto = ConferenceDTO(
        conference_id=conference_id,
        title="AI Conference",
        short_description="AI Conference description",
        full_description="Full description",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        registration_deadline=date(2025, 5, 1),
        location="Moscow",
        max_participants=100,
        organizer_id=organizer_id,
        status=ConferenceStatus.DRAFT,
    )

    mock_get_all_conferences_use_case.execute.return_value = [conference_dto]

    response = client.get("/conferences/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["conference_id"] == str(conference_id)
    assert data[0]["title"] == "AI Conference"


def test_get_conference_by_id_success(client, mock_get_conference_by_id_use_case):
    conference_id = uuid4()
    organizer_id = uuid4()

    conference_dto = ConferenceDTO(
        conference_id=conference_id,
        title="AI Conference",
        short_description="AI Conference description",
        full_description="Full description",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        registration_deadline=date(2025, 5, 1),
        location="Moscow",
        max_participants=100,
        organizer_id=organizer_id,
        status=ConferenceStatus.DRAFT,
    )

    mock_get_conference_by_id_use_case.execute.return_value = conference_dto

    response = client.get(f"/conferences/{conference_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["conference_id"] == str(conference_id)
    assert data["title"] == "AI Conference"


def test_get_conference_by_id_invalid_uuid(client):
    response = client.get("/conferences/invalid-uuid")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_conference_by_id_not_found(client, mock_get_conference_by_id_use_case):
    conference_id = uuid4()
    mock_get_conference_by_id_use_case.execute.side_effect = NotFoundError(
        conference_id
    )

    response = client.get(f"/conferences/{conference_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_conference_by_id_returns_none(client, mock_get_conference_by_id_use_case):
    conference_id = uuid4()
    mock_get_conference_by_id_use_case.execute.return_value = None

    response = client.get(f"/conferences/{conference_id}")

    assert response.status_code in [
        status.HTTP_404_NOT_FOUND,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    ]
