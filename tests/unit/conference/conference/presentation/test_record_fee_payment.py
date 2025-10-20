from uuid import uuid4

from fastapi import status


def test_record_fee_payment_success(client, mock_record_fee_payment_use_case):
    conference_id = uuid4()
    participant_id = uuid4()

    payload = {
        "amount": 5000.0,
        "payment_date": "2025-05-20",
        "currency": "RUB",
    }

    response = client.post(
        f"/conferences/{conference_id}/participants/{participant_id}/fee", json=payload
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_record_fee_payment_use_case.execute.assert_called_once()


def test_record_fee_payment_with_usd(client, mock_record_fee_payment_use_case):
    conference_id = uuid4()
    participant_id = uuid4()

    payload = {
        "amount": 100.0,
        "payment_date": "2025-05-20",
        "currency": "USD",
    }

    response = client.post(
        f"/conferences/{conference_id}/participants/{participant_id}/fee", json=payload
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_record_fee_payment_missing_required_fields(client):
    conference_id = uuid4()
    participant_id = uuid4()

    payload = {
        "amount": 5000.0,
    }

    response = client.post(
        f"/conferences/{conference_id}/participants/{participant_id}/fee", json=payload
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_record_fee_payment_negative_amount(client):
    conference_id = uuid4()
    participant_id = uuid4()

    payload = {
        "amount": -5000.0,
        "payment_date": "2025-05-20",
        "currency": "RUB",
    }

    response = client.post(
        f"/conferences/{conference_id}/participants/{participant_id}/fee", json=payload
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_record_fee_payment_zero_amount(client):
    conference_id = uuid4()
    participant_id = uuid4()

    payload = {
        "amount": 0.0,
        "payment_date": "2025-05-20",
        "currency": "RUB",
    }

    response = client.post(
        f"/conferences/{conference_id}/participants/{participant_id}/fee", json=payload
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_record_fee_payment_invalid_currency(client):
    conference_id = uuid4()
    participant_id = uuid4()

    payload = {
        "amount": 5000.0,
        "payment_date": "2025-05-20",
        "currency": "INVALID",
    }

    response = client.post(
        f"/conferences/{conference_id}/participants/{participant_id}/fee", json=payload
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_record_fee_payment_invalid_conference_id(client):
    participant_id = uuid4()

    payload = {
        "amount": 5000.0,
        "payment_date": "2025-05-20",
        "currency": "RUB",
    }

    response = client.post(
        f"/conferences/invalid-uuid/participants/{participant_id}/fee", json=payload
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_record_fee_payment_invalid_participant_id(client):
    conference_id = uuid4()

    payload = {
        "amount": 5000.0,
        "payment_date": "2025-05-20",
        "currency": "RUB",
    }

    response = client.post(
        f"/conferences/{conference_id}/participants/invalid-uuid/fee", json=payload
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_record_fee_payment_amount_as_string(client):
    conference_id = uuid4()
    participant_id = uuid4()

    payload = {
        "amount": "5000",
        "payment_date": "2025-05-20",
        "currency": "RUB",
    }

    response = client.post(
        f"/conferences/{conference_id}/participants/{participant_id}/fee", json=payload
    )

    assert response.status_code in [
        status.HTTP_204_NO_CONTENT,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ]
