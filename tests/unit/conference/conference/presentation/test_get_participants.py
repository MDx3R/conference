from uuid import uuid4

from fastapi import status


def test_get_participants_empty(client, mock_get_participants_use_case) -> None:
    conference_id = uuid4()
    mock_get_participants_use_case.execute.return_value = []
    response = client.get(f"/conferences/{conference_id}/participants")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_participants_with_filters(client) -> None:
    conference_id = uuid4()
    url = (
        f"/conferences/{conference_id}/participants"
        "?invitation_date=2025-05-01"
        "&fee_paid=true"
        "&fee_payment_date_from=2025-05-10"
        "&fee_payment_date_to=2025-05-20"
        "&city=Moscow"
        "&needs_hotel=false"
        "&has_submission=true"
    )
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_get_participants_invalid_date(client) -> None:
    conference_id = uuid4()
    response = client.get(
        f"/conferences/{conference_id}/participants?invitation_date=01-05-2025"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_participants_invalid_uuid(client) -> None:
    response = client.get("/conferences/invalid-uuid/participants")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
