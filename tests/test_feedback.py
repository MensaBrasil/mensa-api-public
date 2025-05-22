"""Feedback tests for the People API."""

from unittest.mock import patch

import pytest
from fastapi import HTTPException

from people_api.database.models.feedback import (
    FeedbackTargets,
    FeedbackTypes,
)


@pytest.fixture
def feedback_fixture():
    """Fixture for feedback data."""

    class FeedbackData:
        registration_id = 5
        feedback_text = "Very useful chatbot!"
        feedback_target = FeedbackTargets.CHATBOT
        feedback_type = FeedbackTypes.POSITIVE

    return FeedbackData()


@pytest.mark.asyncio
async def test_feedback_endpoint_success(
    feedback_fixture, test_client, get_valid_internal_token, run_db_query
):
    """Test the feedback endpoint with valid data and check DB insertion."""
    token = get_valid_internal_token(5)
    response = test_client.post(
        "/feedback/",
        json={
            "registration_id": feedback_fixture.registration_id,
            "feedback_text": feedback_fixture.feedback_text,
            "feedback_target": feedback_fixture.feedback_target.value,
            "feedback_type": feedback_fixture.feedback_type.value,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Feedback submitted successfully"}

    rows = run_db_query(
        f"""
        SELECT * from feedbacks where registration_id = 5 and feedback_text = '{feedback_fixture.feedback_text}'
        """
    )
    assert rows, "No feedback row found in the database."
    assert rows[0][3] == feedback_fixture.registration_id
    assert rows[0][4] == feedback_fixture.feedback_text
    assert rows[0][5] == feedback_fixture.feedback_target.value
    assert rows[0][6] == feedback_fixture.feedback_type.value


@pytest.mark.asyncio
async def test_feedback_endpoint_invalid_token(feedback_fixture, test_client):
    """Test the feedback endpoint with an invalid token."""

    response = test_client.post(
        "/feedback/",
        json={
            "registration_id": feedback_fixture.registration_id,
            "feedback_text": feedback_fixture.feedback_text,
            "feedback_target": feedback_fixture.feedback_target,
            "feedback_type": feedback_fixture.feedback_type,
        },
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Token"


@pytest.mark.asyncio
async def test_feedback_endpoint_internal_error(
    feedback_fixture, test_client, get_valid_internal_token
):
    """Test the feedback endpoint when an internal error occurs."""

    async def raise_internal(*args, **kwargs):
        raise HTTPException(status_code=500, detail="An error occurred while processing feedback.")

    token = get_valid_internal_token(5)
    with patch(
        "people_api.services.feedback_service.FeedbackService.process_feedback",
        new=raise_internal,
    ):
        response = test_client.post(
            "/feedback/",
            json={
                "registration_id": feedback_fixture.registration_id,
                "feedback_text": feedback_fixture.feedback_text,
                "feedback_target": feedback_fixture.feedback_target,
                "feedback_type": feedback_fixture.feedback_type,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 500
        assert "An error occurred while processing feedback" in response.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "feedback_text,expected_status,expected_detail",
    [
        ("", 422, "Feedback text must not be empty."),
        ("short", 422, "Feedback text must be between 10 and 1200 characters."),
        (" " * 11, 422, "Feedback text must not be empty."),
        ("a" * 1201, 422, "Feedback text must be between 10 and 1200 characters."),
    ],
)
async def test_feedback_create_validation(
    feedback_text, expected_status, expected_detail, test_client, get_valid_internal_token
):
    """Test the feedback endpoint with invalid feedback text."""
    token = get_valid_internal_token(5)
    valid_data = {
        "registration_id": 1,
        "feedback_text": feedback_text,
        "feedback_target": FeedbackTargets.CHATBOT,
        "feedback_type": FeedbackTypes.POSITIVE,
    }
    response = test_client.post(
        "/feedback/",
        json=valid_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == expected_status
    detail = response.json().get("detail")
    if isinstance(detail, list) and detail:
        assert expected_detail in detail[0].get("msg", "")
    elif isinstance(detail, str):
        assert expected_detail in detail
    else:
        assert False, f"Unexpected error detail: {detail}"
