from uuid import uuid4

from fastapi import status


def test_create_conference_success(client, mock_create_conference_use_case):
    conference_id = uuid4()
    mock_create_conference_use_case.execute.return_value = conference_id

    payload = {
        "title": "AI Conference 2025",
        "short_description": "Annual AI conference",
        "full_description": "Comprehensive AI conference",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "registration_deadline": "2025-05-01",
        "location": "Moscow",
        "max_participants": 100,
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"id": str(conference_id)}
    mock_create_conference_use_case.execute.assert_called_once()


def test_create_conference_without_optional_fields(
    client, mock_create_conference_use_case
):
    conference_id = uuid4()
    mock_create_conference_use_case.execute.return_value = conference_id

    payload = {
        "title": "Simple Conference",
        "short_description": "Basic conference",
        "start_date": "2025-06-01",
        "end_date": "2025-06-01",
        "location": "Online",
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED


def test_create_conference_missing_required_fields(client):
    payload = {
        "title": "Conference",
        "start_date": "2025-06-01",
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]
    missing_fields = {error["loc"][-1] for error in errors}
    assert "short_description" in missing_fields
    assert "end_date" in missing_fields
    assert "location" in missing_fields


def test_create_conference_invalid_date_format(client):
    payload = {
        "title": "Conference",
        "short_description": "Test",
        "start_date": "invalid-date",
        "end_date": "2025-06-03",
        "location": "Moscow",
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_conference_invalid_max_participants_type(client):
    payload = {
        "title": "Conference",
        "short_description": "Test",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "location": "Moscow",
        "max_participants": "invalid",
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_conference_null_required_field(client):
    payload = {
        "title": "Conference",
        "short_description": None,
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "location": "Moscow",
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_conference_negative_max_participants(client):
    payload = {
        "title": "Conference",
        "short_description": "Test",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "location": "Moscow",
        "max_participants": -10,
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]
    assert any("max_participants" in str(error["loc"]) for error in errors)


def test_create_conference_zero_max_participants(client):
    payload = {
        "title": "Conference",
        "short_description": "Test",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "location": "Moscow",
        "max_participants": 0,
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]
    assert any("max_participants" in str(error["loc"]) for error in errors)


def test_create_conference_empty_title(client):
    payload = {
        "title": "",
        "short_description": "Test",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "location": "Moscow",
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]
    assert any("title" in str(error["loc"]) for error in errors)


def test_create_conference_whitespace_only_title(client):
    payload = {
        "title": "   ",
        "short_description": "Test",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "location": "Moscow",
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_conference_empty_location(client):
    payload = {
        "title": "Conference",
        "short_description": "Test",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "location": "",
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_conference_with_max_participants_large_value(
    client, mock_create_conference_use_case
):
    conference_id = uuid4()
    mock_create_conference_use_case.execute.return_value = conference_id

    payload = {
        "title": "Conference",
        "short_description": "Test",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "location": "Moscow",
        "max_participants": 1000000,
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED


def test_create_conference_date_as_string_with_wrong_format(client):
    payload = {
        "title": "Conference",
        "short_description": "Test",
        "start_date": "01-06-2025",
        "end_date": "2025-06-03",
        "location": "Moscow",
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_conference_date_as_integer(client):
    payload = {
        "title": "Conference",
        "short_description": "Test",
        "start_date": 20250601,
        "end_date": "2025-06-03",
        "location": "Moscow",
    }

    response = client.post("/conferences/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
