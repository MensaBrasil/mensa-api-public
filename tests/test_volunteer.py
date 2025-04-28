"""Tests for the volunteer API endpoints."""

import base64
import os

import pytest

MY_BUCKET_NAME = "mybucket"

###############################
# Authentication / Authorization Tests
###############################


@pytest.mark.parametrize(
    "method, endpoint, payload",
    [
        (
            "POST",
            "/volunteer/admin/categories/",
            {"name": "New Category", "points": 10, "description": "Test"},
        ),
        (
            "PATCH",
            "/volunteer/admin/categories/by-name/NEW.CATEGORY",
            {"description": "Updated description", "points": 5},
        ),
        ("GET", "/volunteer/categories/", None),
        ("DELETE", "/volunteer/admin/categories/NEW.CATEGORY", None),
        (
            "POST",
            "/volunteer/admin/evaluations/",
            {"activity_id": 6, "evaluator": "Test Evaluator", "status": "pending"},
        ),
        ("GET", "/volunteer/leaderboard/", None),
        ("GET", "/volunteer/activity-with-category/?activity_id=10", None),
        ("GET", "/volunteer/activities/full/unevaluated/?registration_id=6", None),
        (
            "POST",
            "/volunteer/activity/logs/",
            {
                "registration_id": 6,
                "title": "Test Log",
                "description": "Test description",
                "category_id": 10,
            },
        ),
        ("GET", "/volunteer/activity/evaluations/member/", None),
        ("GET", "/volunteer/activities/", None),
        ("GET", "/volunteer/admin/categories/1", None),
        ("GET", "/volunteer/names", None),
        ("GET", "/volunteer/admin/evaluate-with-category/", None),
        ("GET", "/volunteer/points/?registration_id=6", None),
        ("GET", "/volunteer/activities/full/approved/?registration_id=6", None),
        ("GET", "/volunteer/activities/full/rejected/?registration_id=6", None),
    ],
)
def test_protected_endpoints_no_token(test_client, method, endpoint, payload):
    """
    Requests to protected endpoints without an auth token should return 401/403.
    For endpoints that require query parameters, missing required parameters should also fail.
    """
    response = test_client.request(method, endpoint, json=payload)
    assert response.status_code in [401, 403, 422], (
        f"Expected unauthorized or validation error for {endpoint}"
    )


###############################
# Volunteer Activity Categories Endpoint Tests
###############################


def test_create_category(test_client, mock_valid_token_auth):
    """Test creating a new activity category."""
    payload = {
        "name": "NEW.CATEGORY",
        "description": "Test category description",
        "points": 10,
    }
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    response = test_client.post("/volunteer/admin/categories/", json=payload, headers=headers)
    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}. Response: {response.text}"
    )
    created_category = response.json()
    assert created_category["name"] == payload["name"]


def test_update_category_by_name(test_client, mock_valid_token_auth):
    """
    Test updating a category by name.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    create_payload = {
        "name": "TO.BE.UPDATED",
        "description": "A category to be updated",
        "points": 10,
    }
    create_resp = test_client.post(
        "/volunteer/admin/categories/", json=create_payload, headers=headers
    )
    assert create_resp.status_code == 201, create_resp.text

    update_payload = {"description": "Updated description", "points": 5}
    update_resp = test_client.patch(
        f"/volunteer/admin/categories/by-name/{create_payload['name']}",
        json=update_payload,
        headers=headers,
    )
    assert update_resp.status_code == 200, update_resp.text

    updated_category = update_resp.json()
    assert updated_category["name"] == create_payload["name"]
    assert updated_category["description"] == update_payload["description"]
    assert updated_category["points"] == update_payload["points"]


def test_update_category_by_name_not_found(test_client, mock_valid_token_auth):
    """
    Test updating a non-existent category should return a 404 error.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    update_payload = {"description": "Non-existent category update", "points": 5}
    response = test_client.patch(
        "/volunteer/admin/categories/by-name/NO.SUCH.CATEGORY",
        json=update_payload,
        headers=headers,
    )
    assert response.status_code == 404, (
        f"Expected 404, got {response.status_code}. Response: {response.text}"
    )


def test_delete_category_by_name_not_found(test_client, mock_valid_token_auth):
    """
    Test deleting a non-existent category should return a 404 error.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    response = test_client.delete("/volunteer/admin/categories/NO.SUCH.CATEGORY", headers=headers)
    assert response.status_code == 404, (
        f"Expected 404, got {response.status_code}. Response: {response.text}"
    )


def test_delete_category_by_name(test_client, mock_valid_token_auth):
    """Test deleting a category by name."""
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    payload = {
        "name": "DELETE.CATEGORY",
        "description": "To be deleted",
        "points": 20,
    }
    create_resp = test_client.post("/volunteer/admin/categories/", json=payload, headers=headers)
    assert create_resp.status_code == 201, create_resp.text

    delete_resp = test_client.delete(
        f"/volunteer/admin/categories/{payload['name']}", headers=headers
    )
    assert delete_resp.status_code == 200, delete_resp.text

    data = delete_resp.json()
    assert data["ok"] is True

    update_resp = test_client.patch(
        f"/volunteer/admin/categories/by-name/{payload['name']}",
        json={"description": "dummy"},
        headers=headers,
    )
    assert update_resp.status_code == 404


def test_create_category_no_permissions(test_client, mock_valid_token):
    """
    Attempt to create a category without permissions.
    Expect a 401 or 403 response.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    payload = {
        "name": "NoPermCat",
        "description": "Should fail due to lack of permission",
        "points": 5,
    }
    response = test_client.post("/volunteer/admin/categories/", json=payload, headers=headers)
    assert response.status_code in [401, 403], f"Response: {response.text}"


def test_update_category_no_permissions(test_client, mock_valid_token):
    """
    Attempt to update a category without permissions.
    Expect a 401 or 403 response.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    payload = {"description": "Updated description"}
    response = test_client.patch(
        "/volunteer/admin/categories/by-name/TEST.CATEGORY",
        json=payload,
        headers=headers,
    )
    assert response.status_code in [401, 403], f"Response: {response.text}"


def test_delete_category_no_permissions(test_client, mock_valid_token):
    """
    Attempt to delete a category without permissions.
    Expect a 401 or 403 response.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.delete("/volunteer/admin/categories/TEST.CATEGORY", headers=headers)
    assert response.status_code in [401, 403], f"Response: {response.text}"


###############################
# Volunteer Activity Logs Endpoint Tests
###############################


def test_create_activity_log(test_client, mock_valid_token_auth):
    """Test creating a new activity log."""
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    log_payload = {
        "registration_id": 6,
        "title": "Test Activity Log",
        "description": "Log description",
        "category_id": 10,
    }
    log_resp = test_client.post("/volunteer/activity/logs/", json=log_payload, headers=headers)
    assert log_resp.status_code == 201, log_resp.text
    log = log_resp.json()
    assert log["title"] == log_payload["title"]


def test_create_activity_log_missing_title(test_client, mock_valid_token_auth):
    """
    Test creating an activity log without the required 'title' field should fail with a 422 error.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    log_payload = {
        "registration_id": 6,
        "description": "Log without title",
        "category_id": 10,
    }
    response = test_client.post("/volunteer/activity/logs/", json=log_payload, headers=headers)
    assert response.status_code == 422, (
        f"Expected 422, got {response.status_code}. Response: {response.text}"
    )


def test_activity_log_autoincrement(test_client, mock_valid_token_auth, run_db_query):
    """
    Test that activity log IDs auto-increment correctly.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}

    run_db_query("DELETE FROM activity_evaluation")
    run_db_query("DELETE FROM volunteer_point_transactions")
    run_db_query("DELETE FROM volunteer_activity_log")
    run_db_query("SELECT setval('volunteer_activity_log_id_seq', 1, false)")

    activity_log_payload1 = {
        "registration_id": 6,
        "category_id": 10,
        "title": "First Activity",
        "description": "First activity log for auto-increment test",
        "activity_date": "2024-11-11",
    }
    resp1 = test_client.post(
        "/volunteer/activity/logs/", json=activity_log_payload1, headers=headers
    )
    assert resp1.status_code == 201, (
        f"Expected 201 when creating first activity log, got {resp1.status_code}. Response: {resp1.text}"
    )
    log1 = resp1.json()

    activity_log_payload2 = {
        "registration_id": 6,
        "category_id": 10,
        "title": "Second Activity",
        "description": "Second activity log for auto-increment test",
        "activity_date": "2024-11-12",
    }
    resp2 = test_client.post(
        "/volunteer/activity/logs/", json=activity_log_payload2, headers=headers
    )
    assert resp2.status_code == 201, (
        f"Expected 201 when creating second activity log, got {resp2.status_code}. Response: {resp2.text}"
    )
    log2 = resp2.json()

    activity_log_payload3 = {
        "registration_id": 6,
        "category_id": 10,
        "title": "Third Activity",
        "description": "Third activity log for auto-increment test",
        "activity_date": "2024-11-13",
    }
    resp3 = test_client.post(
        "/volunteer/activity/logs/", json=activity_log_payload3, headers=headers
    )
    assert resp3.status_code == 201, (
        f"Expected 201 when creating third activity log, got {resp3.status_code}. Response: {resp3.text}"
    )
    log3 = resp3.json()

    assert log1["id"] == 1, f"Expected first activity log id to be 1, got {log1['id']}"
    assert log2["id"] == 2, f"Expected second activity log id to be 2, got {log2['id']}"
    assert log3["id"] == 3, f"Expected third activity log id to be 3, got {log3['id']}"


###############################
# Volunteer Activity Evaluations Endpoint Tests
###############################


def test_create_activity_evaluation(test_client, mock_valid_token_auth):
    """Test creating a new activity evaluation."""
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    payload = {
        "activity_id": 10,
        "evaluator_id": 5,
        "status": "pending",
    }
    response = test_client.post("/volunteer/admin/evaluations/", json=payload, headers=headers)
    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}. Response: {response.text}"
    )
    evaluation = response.json()
    assert evaluation["activity_id"] == payload["activity_id"]
    assert evaluation["evaluator_id"] == payload["evaluator_id"]
    assert evaluation["status"] == payload["status"]


def test_create_activity_evaluation_missing_evaluator(test_client, mock_valid_token_auth):
    """
    Test creating an activity evaluation without the required status field should fail with a 422 error.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    payload = {
        "activity_id": 10,
    }
    response = test_client.post("/volunteer/admin/evaluations/", json=payload, headers=headers)
    assert response.status_code == 422, (
        f"Expected 422, got {response.status_code}. Response: {response.text}"
    )


def test_create_activity_evaluation_approved(test_client, mock_valid_token_auth):
    """
    Test creating an evaluation with status 'approved' to trigger point transaction creation.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    payload = {
        "activity_id": 10,
        "evaluator_id": "1805",
        "status": "approved",
    }
    response = test_client.post("/volunteer/admin/evaluations/", json=payload, headers=headers)
    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}. Response: {response.text}"
    )
    evaluation = response.json()
    assert evaluation["status"].lower() == "approved"


def test_create_activity_evaluation_for_nonexistent_log(test_client, mock_valid_token_auth):
    """Test creating an evaluation for a non-existent activity log."""
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    payload = {"activity_id": 99999, "evaluator_id": "1805", "status": "approved"}
    response = test_client.post("/volunteer/admin/evaluations/", json=payload, headers=headers)
    assert response.status_code == 404, (
        f"Expected 404 for non-existent activity log, got {response.status_code}."
    )


def test_get_member_activity_evaluations(test_client, mock_valid_token_auth):
    """
    Test fetching evaluations for the authenticated member.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    response = test_client.get("/volunteer/activity/evaluations/member/", headers=headers)
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    evaluations = response.json()
    assert isinstance(evaluations, list), "Response should be a list"


###############################
# Volunteer Leaderboard Endpoint Tests
###############################


def test_get_leaderboard_all_periods(test_client, mock_valid_token_auth):
    """
    Test retrieving the leaderboard.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    start_date = "2023-01-01T00:00:00Z"
    end_date = "2023-12-31T23:59:59Z"
    url = f"/volunteer/leaderboard/?start_date={start_date}&end_date={end_date}"
    response = test_client.get(url, headers=headers)
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    leaderboard = response.json()
    assert isinstance(leaderboard, list), "Leaderboard should be a list"


def test_get_leaderboard_invalid_date_format(test_client, mock_valid_token_auth):
    """
    Test retrieving the leaderboard with invalid date formats should return a 422 error.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    start_date = "invalid-date"
    end_date = "another-invalid-date"
    url = f"/volunteer/leaderboard/?start_date={start_date}&end_date={end_date}"
    response = test_client.get(url, headers=headers)
    assert response.status_code == 422, (
        f"Expected 422, got {response.status_code}. Response: {response.text}"
    )


def test_leaderboard_threshold_filtering(test_client, mock_valid_token_auth):
    """
    Test that leaderboard filtering by date range works correctly.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    response = test_client.get(
        "/volunteer/leaderboard/?start_date=2023-01-01T00:00:00Z&end_date=2023-12-31T23:59:59Z",
        headers=headers,
    )
    leaderboard = response.json()
    assert isinstance(leaderboard, list), "Leaderboard should be a list"


###############################
# Additional Endpoints Tests
###############################


def test_get_public_activity_feed(test_client, mock_valid_token_auth):
    """
    Test retrieving all volunteer activity logs for the public feed.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    response = test_client.get("/volunteer/activities/", headers=headers)
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    logs = response.json()
    assert isinstance(logs, list), "Expected a list of activity logs"


def test_get_activity_category_by_id(test_client, mock_valid_token_auth):
    """
    Test retrieving a single activity category by its ID.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    payload = {
        "name": "GET.CATEGORY",
        "description": "Category for get-by-id test",
        "points": 15,
    }
    create_resp = test_client.post("/volunteer/admin/categories/", json=payload, headers=headers)
    assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
    category = create_resp.json()
    category_id = category["id"]

    get_resp = test_client.get(f"/volunteer/admin/categories/{category_id}", headers=headers)
    assert get_resp.status_code == 200, (
        f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
    )
    fetched_category = get_resp.json()
    assert fetched_category["id"] == category_id
    assert fetched_category["name"] == payload["name"]


def test_get_combined_names(test_client, mock_valid_token_auth, run_db_query):
    """
    Test retrieving combined names (registration and legal representatives).
    For testing purposes, ensure the registration record and legal representatives are seeded.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    registration_id = 5

    run_db_query(
        f"UPDATE registration SET name='TestFirst TestLast' WHERE registration_id={registration_id}"
    )

    run_db_query(f"""
        INSERT INTO legal_representatives (registration_id, cpf, full_name, email, phone, alternative_phone, observations)
        VALUES ({registration_id}, '12345678901', 'Ana Silva', 'ana@example.com', '5551111111', '5552222222', 'Test LR One')
    """)
    run_db_query(f"""
        INSERT INTO legal_representatives (registration_id, cpf, full_name, email, phone, alternative_phone, observations)
        VALUES ({registration_id}, '12345678902', 'Carlos Pereira', 'carlos@example.com', '5553333333', '5554444444', 'Test LR Two')
    """)

    response = test_client.get("/volunteer/names", headers=headers)
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    data = response.json()
    assert "names" in data, "Response should contain a 'names' key"

    names = data["names"]
    assert isinstance(names, list), "The 'names' value should be a list"
    assert len(names) == 3, f"Expected exactly 3 names, got {len(names)}"
    assert names[0] == "TestFirst TestLast", (
        f"Expected registration name to be 'TestFirst TestLast', got {names[0]}"
    )
    assert names[1] == "Ana Silva", f"Expected first legal rep to be 'Ana Silva', got {names[1]}"
    assert names[2] == "Carlos Pereira", (
        f"Expected second legal rep to be 'Carlos Pereira', got {names[2]}"
    )


def test_create_activity_log_with_media(test_client, aws_resource, mock_valid_token_auth):
    """
    Test creating an activity log with media upload via JSON.
    The test sends a JSON payload including a base64-encoded 'media_file'.
    """
    os.environ["MY_BUCKET_NAME"] = "mybucket"

    file_content = b"Test image content"
    media_file_encoded = base64.b64encode(file_content).decode("utf-8")

    payload = {
        "registration_id": 5,
        "title": "Test Activity Log",
        "description": "Activity with media upload",
        "category_id": 10,
        "activity_date": "2024-11-11",
        "media_file": media_file_encoded,
    }
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}

    response = test_client.post("/volunteer/activity/logs/", json=payload, headers=headers)
    assert response.status_code == 201, f"Response: {response.text}"

    result = response.json()
    media_path = result.get("media_path")
    assert media_path is not None, "media_path should be set"
    assert media_path.startswith("s3://"), "media_path should be an S3 URL"

    bucket = "mybucket"
    key = media_path.split(f"s3://{bucket}/")[-1]
    obj = aws_resource.Object(bucket, key)
    uploaded_content = obj.get()["Body"].read()
    assert uploaded_content == file_content


def test_get_all_activity_categories(test_client, mock_valid_token_auth):
    """
    Test retrieving all activity categories.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    payload = {
        "name": "ALL.CATEGORIES",
        "description": "Test category for get all",
        "points": 10,
    }
    create_resp = test_client.post("/volunteer/admin/categories/", json=payload, headers=headers)
    assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
    get_resp = test_client.get("/volunteer/categories/", headers=headers)
    assert get_resp.status_code == 200, (
        f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
    )
    categories = get_resp.json()
    assert isinstance(categories, list), "Expected list of categories"
    assert any(cat["name"] == payload["name"] for cat in categories), (
        "New category not found in list"
    )


def test_get_activity_with_category_success(test_client, mock_valid_token_auth):
    """
    Test retrieving an activity along with its category using the /activity-with-category/ endpoint.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    category_payload = {
        "name": "AWC.CATEGORY",
        "description": "Category for get activity with category test",
        "points": 15,
    }
    cat_resp = test_client.post(
        "/volunteer/admin/categories/", json=category_payload, headers=headers
    )
    assert cat_resp.status_code == 201, f"Category creation failed: {cat_resp.text}"
    category = cat_resp.json()
    category_id = category["id"]

    activity_payload = {
        "registration_id": 5,
        "category_id": category_id,
        "title": "Activity with Category",
        "description": "Test activity with category",
        "activity_date": "2025-03-21",
    }
    act_resp = test_client.post("/volunteer/activity/logs/", json=activity_payload, headers=headers)
    assert act_resp.status_code == 201, f"Activity creation failed: {act_resp.text}"
    activity = act_resp.json()
    activity_id = activity["id"]

    get_resp = test_client.get(
        f"/volunteer/activity-with-category/?activity_id={activity_id}", headers=headers
    )
    assert get_resp.status_code == 200, (
        f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
    )
    data = get_resp.json()
    assert "activity" in data, "Response missing 'activity'"
    assert "category_name" in data, "Response missing 'category_name'"
    assert data["activity"]["id"] == activity_id, "Activity id mismatch"
    assert data["category_name"] == category_payload["name"], "Category name mismatch"


def test_get_activity_with_category_not_found(test_client, mock_valid_token_auth):
    """
    Test retrieving an activity with category using an invalid activity_id should return 404.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    get_resp = test_client.get(
        "/volunteer/activity-with-category/?activity_id=99999", headers=headers
    )
    assert get_resp.status_code == 404, (
        f"Expected 404 for non-existent activity, got {get_resp.status_code}. Response: {get_resp.text}"
    )


def test_get_user_full_activities_unevaluated_empty(test_client, mock_valid_token_auth):
    """
    Test retrieving full unevaluated activities for a registration when there are none.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    registration_id = 5
    get_resp = test_client.get(
        f"/volunteer/activities/full/unevaluated/?registration_id={registration_id}",
        headers=headers,
    )
    assert get_resp.status_code == 200, (
        f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
    )
    activities = get_resp.json()
    assert isinstance(activities, list), "Expected a list of unevaluated activities"


def test_get_user_full_activities_unevaluated_with_logs(test_client, mock_valid_token_auth):
    """
    Test retrieving full unevaluated activities for a registration when at least one exists.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    registration_id = 5

    category_payload = {
        "name": "FULL.UNEVALUATED.CATEGORY",
        "description": "Category for unevaluated activities test",
        "points": 20,
    }
    cat_resp = test_client.post(
        "/volunteer/admin/categories/", json=category_payload, headers=headers
    )
    assert cat_resp.status_code == 201, f"Category creation failed: {cat_resp.text}"
    category = cat_resp.json()
    category_id = category["id"]

    activity_payload = {
        "registration_id": registration_id,
        "category_id": category_id,
        "title": "Unevaluated Activity",
        "description": "Activity for unevaluated test",
        "activity_date": "2025-03-21",
    }
    act_resp = test_client.post("/volunteer/activity/logs/", json=activity_payload, headers=headers)
    assert act_resp.status_code == 201, f"Activity creation failed: {act_resp.text}"
    activity = act_resp.json()
    activity_id = activity["id"]

    get_resp = test_client.get(
        f"/volunteer/activities/full/unevaluated/?registration_id={registration_id}",
        headers=headers,
    )
    assert get_resp.status_code == 200, (
        f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
    )
    activities = get_resp.json()
    assert isinstance(activities, list), "Expected a list of unevaluated activities"
    assert any(act["activity"]["id"] == activity_id for act in activities), (
        "Unevaluated activity not found"
    )


# def test_get_user_full_activities_approved(test_client, mock_valid_token_auth):
#     """
#     Test retrieving full approved activities for a registration.
#     This involves creating an activity log, then an evaluation with status "approved".
#     """
#     headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}

#     activity_payload = {
#         "category_id": 10,
#         "title": "Approved Activity",
#         "description": "Test approved activity",
#         "activity_date": "2025-03-22",
#         "volunteer_name": "Test User"
#     }
#     act_resp = test_client.post("/volunteer/activity/logs/", json=activity_payload, headers=headers)
#     assert act_resp.status_code == 201, f"Activity log creation failed: {act_resp.text}"
#     activity = act_resp.json()
#     activity_id = activity["id"]

#     evaluation_payload = {
#         "activity_id": activity_id,
#         "evaluator": "Approver",
#         "status": "approved",
#     }
#     eval_resp = test_client.post("/volunteer/admin/evaluations/", json=evaluation_payload, headers=headers)
#     assert eval_resp.status_code == 201, f"Evaluation creation failed: {eval_resp.text}"

#     get_resp = test_client.get("/volunteer/activities/full/approved/", headers=headers)
#     assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
#     activities = get_resp.json()
#     assert isinstance(activities, list), "Response should be a list"

#     matching = [act for act in activities if act.get("activity", {}).get("id") == activity_id]
#     assert matching, "Approved activity not found in response"
#     evaluation_data = matching[0].get("evaluation")
#     assert evaluation_data and evaluation_data.get("status").lower() == "approved", "Evaluation status is not 'approved'"

# def test_get_user_full_activities_rejected(test_client, mock_valid_token_auth):
#     """
#     Test retrieving full rejected activities for a registration.
#     This involves creating an activity log, then an evaluation with status "rejected".
#     """
#     headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}

#     activity_payload = {
#         "category_id": 10,
#         "title": "Rejected Activity",
#         "description": "Test rejected activity",
#         "activity_date": "2025-03-22",
#         "volunteer_name": "Test User"
#     }
#     act_resp = test_client.post("/volunteer/activity/logs/", json=activity_payload, headers=headers)
#     assert act_resp.status_code == 201, f"Activity log creation failed: {act_resp.text}"
#     activity = act_resp.json()
#     activity_id = activity["id"]

#     evaluation_payload = {
#         "activity_id": activity_id,
#         "evaluator": "Rejector",
#         "status": "rejected",
#     }
#     eval_resp = test_client.post("/volunteer/admin/evaluations/", json=evaluation_payload, headers=headers)
#     assert eval_resp.status_code == 201, f"Evaluation creation failed: {eval_resp.text}"

#     get_resp = test_client.get("/volunteer/activities/full/rejected/", headers=headers)
#     assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
#     activities = get_resp.json()
#     assert isinstance(activities, list), "Response should be a list"

#     matching = [act for act in activities if act.get("activity", {}).get("id") == activity_id]
#     assert matching, "Rejected activity not found in response"
#     evaluation_data = matching[0].get("evaluation")
#     assert evaluation_data and evaluation_data.get("status").lower() == "rejected", "Evaluation status is not 'rejected'"


def test_get_unevaluated_activities_for_evaluation(test_client, mock_valid_token_auth):
    """
    Test retrieving unevaluated activities via the evaluate-with-category endpoint.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    get_resp = test_client.get("/volunteer/admin/evaluate-with-category/", headers=headers)
    assert get_resp.status_code == 200, (
        f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
    )
    results = get_resp.json()
    assert isinstance(results, list), "Response should be a list"
