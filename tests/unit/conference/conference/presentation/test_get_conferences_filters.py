from uuid import uuid4

from fastapi import status


def test_get_all_conferences_ok_without_filters(client) -> None:
    response = client.get("/conferences/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_get_all_conferences_with_status_valid_enum(client) -> None:
    response = client.get("/conferences/?status=Черновик")
    assert response.status_code == status.HTTP_200_OK


def test_get_all_conferences_with_status_invalid_enum(client) -> None:
    response = client.get("/conferences/?status=DRAFT")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_all_conferences_with_organizer_id_valid_uuid(client) -> None:
    organizer_id = uuid4()
    response = client.get(f"/conferences/?organizer_id={organizer_id}")
    assert response.status_code == status.HTTP_200_OK


def test_get_all_conferences_with_organizer_id_invalid_uuid(client) -> None:
    response = client.get("/conferences/?organizer_id=not-a-uuid")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_all_conferences_combined_filters(client) -> None:
    organizer_id = uuid4()
    response = client.get(f"/conferences/?status=Активна&organizer_id={organizer_id}")
    assert response.status_code == status.HTTP_200_OK
