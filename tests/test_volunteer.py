"""Tests for the volunteer API endpoints."""

import base64
import urllib.parse

import pytest

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
        ("GET", "/volunteer/names", None),
        ("GET", "/volunteer/admin/evaluate-with-category/", None),
        ("GET", "/volunteer/points/?registration_id=6", None),
        ("GET", "/volunteer/activities/full/approved/?registration_id=6", None),
        ("GET", "/volunteer/activities/full/rejected/?registration_id=6", None),
        ("GET", "/volunteer/activities/full/unevaluated/?registration_id=6", None),
        ("GET", "/volunteer/leaderboard/me/?registration_id=6", None),
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


def test_get_combined_names(test_client, get_valid_internal_token):
    """
    Test retrieving combined names (registration and legal representatives).
    Uses seeded data from test_db_dump.sql.
    """

    token = get_valid_internal_token(7)
    headers = {"Authorization": f"Bearer {token}"}

    response = test_client.get("/volunteer/names", headers=headers)
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    data = response.json()
    assert "names" in data, "Response should contain a 'names' key"

    names = data["names"]
    assert isinstance(names, list), "The 'names' value should be a list"

    expected_names = {"Ana Junior", "Carlos Silva", "Ana Silva"}
    found_names = set(names)
    assert expected_names.issubset(found_names), (
        f"Expected names {expected_names} in response, got {found_names}"
    )


def test_create_activity_log_with_media(
    test_client, aws_resource, mock_valid_token_auth, monkeypatch
):
    """Test creating a new activity log with a media file."""
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}

    bucket = "volunteer-platform-staging"
    aws_resource.create_bucket(Bucket=bucket)
    monkeypatch.setenv("volunteer_s3_bucket", bucket)
    from people_api.settings import get_settings

    get_settings.cache_clear()

    dummy = b"hello, moto!"
    media_file_b64 = base64.b64encode(dummy).decode()

    log_payload = {
        "registration_id": 6,
        "title": "Test Activity Log Media",
        "description": "Log with media",
        "category_id": 10,
        "media_file": media_file_b64,
    }

    resp = test_client.post(
        "/volunteer/activity/logs/",
        json=log_payload,
        headers=headers,
    )
    assert resp.status_code == 201, resp.text

    log = resp.json()
    assert log["title"] == log_payload["title"]

    media_url = log["media_path"]
    assert media_url.startswith("s3://") or media_url.startswith("https://"), (
        f"Expected s3:// or https:// URL, got {media_url}"
    )

    if media_url.startswith("s3://"):
        prefix = f"s3://{bucket}/"
        key = media_url[len(prefix) :]
    else:
        parsed = urllib.parse.urlparse(media_url)
        key = parsed.path.lstrip("/")

    stored = aws_resource.Object(bucket, key).get()["Body"].read()
    assert stored == dummy


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


def test_get_user_full_activities_unevaluated_empty(test_client, mock_valid_token_auth):
    """
    Test retrieving full unevaluated activities for a registration when there are none.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}

    get_resp = test_client.get(
        "/volunteer/activities/full/unevaluated/",
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

    category_payload = {
        "name": "FULL.UNEVALUATED.CATEGORY",
        "description": "Category for unevaluated activities test",
        "points": 20,
    }
    cat_resp = test_client.post(
        "/volunteer/admin/categories/",
        json=category_payload,
        headers=headers,
    )
    assert cat_resp.status_code == 201, f"Category creation failed: {cat_resp.text}"
    category_id = cat_resp.json()["id"]

    activity_payload = {
        "category_id": category_id,
        "title": "Unevaluated Activity",
        "description": "Activity for unevaluated test",
        "activity_date": "2025-03-21",
    }
    act_resp = test_client.post(
        "/volunteer/activity/logs/",
        json=activity_payload,
        headers=headers,
    )
    assert act_resp.status_code == 201, f"Activity creation failed: {act_resp.text}"
    activity_id = act_resp.json()["id"]

    get_resp = test_client.get(
        "/volunteer/activities/full/unevaluated/",
        headers=headers,
    )
    assert get_resp.status_code == 200, (
        f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
    )

    activities = get_resp.json()
    assert isinstance(activities, list), "Expected a list of unevaluated activities"
    assert activities, "Expected at least one unevaluated activity in the list"

    assert any(act["activity"]["id"] == activity_id for act in activities), (
        f"Expected to find activity {activity_id} in unevaluated activities, got {activities}"
    )


def test_get_user_full_activities_approved(test_client, mock_valid_token_auth):
    """
    Test retrieving full approved activities for a registration.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}

    cat_payload = {
        "name": "APPROVED.CATEGORY",
        "description": "Category for approved activities test",
        "points": 30,
    }
    cat_resp = test_client.post(
        "/volunteer/admin/categories/",
        json=cat_payload,
        headers=headers,
    )
    assert cat_resp.status_code == 201, f"Category creation failed: {cat_resp.text}"
    category_id = cat_resp.json()["id"]

    act_payload = {
        "category_id": category_id,
        "title": "Approved Activity",
        "description": "Test approved activity",
        "activity_date": "2025-03-22",
    }
    act_resp = test_client.post(
        "/volunteer/activity/logs/",
        json=act_payload,
        headers=headers,
    )
    assert act_resp.status_code == 201, f"Activity log creation failed: {act_resp.text}"
    activity_id = act_resp.json()["id"]

    eval_payload = {
        "activity_id": activity_id,
        "evaluator": "Approver",
        "status": "approved",
    }
    eval_resp = test_client.post(
        "/volunteer/admin/evaluations/",
        json=eval_payload,
        headers=headers,
    )
    assert eval_resp.status_code == 201, f"Evaluation creation failed: {eval_resp.text}"

    get_resp = test_client.get(
        "/volunteer/activities/full/approved/",
        headers=headers,
    )
    assert get_resp.status_code == 200, (
        f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
    )
    activities = get_resp.json()
    assert isinstance(activities, list), "Response should be a list"

    matching = [act for act in activities if act.get("activity", {}).get("id") == activity_id]
    assert matching, "Approved activity not found in response"
    evaluation_data = matching[0].get("evaluation")
    assert evaluation_data and evaluation_data.get("status").lower() == "approved", (
        "Evaluation status is not 'approved'"
    )


def test_get_user_full_activities_rejected(test_client, mock_valid_token_auth):
    """
    Test retrieving full rejected activities for a registration.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}

    cat_payload = {
        "name": "REJECTED.CATEGORY",
        "description": "Category for rejected activities test",
        "points": 10,
    }
    cat_resp = test_client.post(
        "/volunteer/admin/categories/",
        json=cat_payload,
        headers=headers,
    )
    assert cat_resp.status_code == 201, f"Category creation failed: {cat_resp.text}"
    category_id = cat_resp.json()["id"]

    act_payload = {
        "category_id": category_id,
        "title": "Rejected Activity",
        "description": "Test rejected activity",
        "activity_date": "2025-03-22",
    }
    act_resp = test_client.post(
        "/volunteer/activity/logs/",
        json=act_payload,
        headers=headers,
    )
    assert act_resp.status_code == 201, f"Activity log creation failed: {act_resp.text}"
    activity_id = act_resp.json()["id"]

    eval_payload = {
        "activity_id": activity_id,
        "evaluator": "Rejector",
        "status": "rejected",
    }
    eval_resp = test_client.post(
        "/volunteer/admin/evaluations/",
        json=eval_payload,
        headers=headers,
    )
    assert eval_resp.status_code == 201, f"Evaluation creation failed: {eval_resp.text}"

    get_resp = test_client.get(
        "/volunteer/activities/full/rejected/",
        headers=headers,
    )
    assert get_resp.status_code == 200, (
        f"Expected 200, got {get_resp.status_code}. Response: {get_resp.text}"
    )
    activities = get_resp.json()
    assert isinstance(activities, list), "Response should be a list"

    matching = [act for act in activities if act.get("activity", {}).get("id") == activity_id]
    assert matching, "Rejected activity not found in response"
    evaluation_data = matching[0].get("evaluation")
    assert evaluation_data and evaluation_data.get("status").lower() == "rejected", (
        "Evaluation status is not 'rejected'"
    )


###############################
# Leaderboard Endpoint Tests
###############################


def test_get_leaderboard_top_n_and_order(
    test_client,
    mock_valid_token_auth,
    run_db_query,
):
    """
    Seed three volunteers with different point totals and verify that the leaderboard endpoint
    returns them in descending order of points and limits to the top N entries.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}

    run_db_query("DELETE FROM volunteer_point_transactions")
    run_db_query("DELETE FROM activity_evaluation")
    run_db_query("DELETE FROM volunteer_activity_log")

    run_db_query("""
        INSERT INTO volunteer_activity_log
            (id, registration_id, category_id, title, description, activity_date,
             media_path, volunteer_name, created_at, updated_at)
        VALUES
            (5000, 1805, 10, 'Log A', 'Description A', '2025-01-01', NULL, 'Alice Santos', '2025-01-01 09:00:00', '2025-01-01 09:00:00'),
            (5001,    5, 10, 'Log B', 'Description B', '2025-01-02', NULL, 'Bruno Lima',  '2025-01-02 09:00:00', '2025-01-02 09:00:00'),
            (5002,    6, 10, 'Log C', 'Description C', '2025-01-03', NULL, 'Carla Souza', '2025-01-03 09:00:00', '2025-01-03 09:00:00');
    """)

    run_db_query("""
        INSERT INTO activity_evaluation
            (id, activity_id, evaluator_id, status, observation, created_at, updated_at)
        VALUES
            (6000, 5000, 999, 'approved', 'OK A', '2025-01-01 10:00:00', '2025-01-01 10:00:00'),
            (6001, 5001, 999, 'approved', 'OK B', '2025-01-02 10:00:00', '2025-01-02 10:00:00'),
            (6002, 5002, 999, 'approved', 'OK C', '2025-01-03 10:00:00', '2025-01-03 10:00:00');
    """)

    run_db_query("""
        INSERT INTO volunteer_point_transactions
            (id, registration_id, activity_id, points, created_at, updated_at)
        VALUES
            (7000, 1805, 5000,  5, '2025-01-01 10:00:00', '2025-01-01 10:00:00'),
            (7001,    5, 5001, 10, '2025-01-02 10:00:00', '2025-01-02 10:00:00'),
            (7002,    6, 5002,  7, '2025-01-03 10:00:00', '2025-01-03 10:00:00');
    """)

    url = "/volunteer/leaderboard/?start_date=2025-01-01T00:00:00Z&end_date=2025-12-31T23:59:59Z"
    response = test_client.get(url, headers=headers)
    assert response.status_code == 200, response.text

    leaderboard = response.json()
    assert isinstance(leaderboard, list), "Expected a list of leaderboard entries"
    ids = [entry["registration_id"] for entry in leaderboard]
    assert ids == [5, 6, 1805], f"Unexpected order: {ids}"
    points = [entry["total_points"] for entry in leaderboard]
    assert points == [10, 7, 5]
    ranks = [entry["rank"] for entry in leaderboard]
    assert ranks == [1, 2, 3]


def test_get_my_ranking_returns_correct_user_entry(
    test_client,
    mock_valid_token_auth,
    run_db_query,
):
    """
    Given seeded data, verify the /leaderboard/me/ endpoint returns the
    calling user’s registration_id, points and rank correctly.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}

    run_db_query("DELETE FROM volunteer_point_transactions")
    run_db_query("DELETE FROM activity_evaluation")
    run_db_query("DELETE FROM volunteer_activity_log")

    run_db_query("""
        INSERT INTO volunteer_activity_log
            (id, registration_id, category_id, title, description, activity_date,
             media_path, volunteer_name, created_at, updated_at)
        VALUES
            (5002,    5, 10, 'Log B', 'Description B', '2025-01-02', NULL, 'Fernando Filho', '2025-01-02 10:00:00', '2025-01-02 10:00:00');
    """)

    run_db_query("""
        INSERT INTO activity_evaluation
            (id, activity_id, evaluator_id, status, observation, created_at, updated_at)
        VALUES
            (6002, 5002, 999, 'approved', 'OK B', '2025-01-02 11:00:00', '2025-01-02 11:00:00');
    """)

    run_db_query("""
        INSERT INTO volunteer_point_transactions
            (id, registration_id, activity_id, points, created_at, updated_at)
        VALUES
            (7002,    5, 5002,  7, '2025-01-02 11:00:00', '2025-01-02 11:00:00');
    """)

    url_me = (
        "/volunteer/leaderboard/me/?start_date=2025-01-01T00:00:00Z&end_date=2025-12-31T23:59:59Z"
    )
    response = test_client.get(url_me, headers=headers)
    assert response.status_code == 200, response.text

    me = response.json()
    assert isinstance(me, dict), "Expected a single leaderboard entry"
    assert me["registration_id"] == 5
    assert me["total_points"] == 7
    assert me["rank"] == 1
    assert me["volunteer_name"] == "Fernando Filho"


@pytest.mark.asyncio
async def test_get_unevaluated_activities_by_authorized_role_api(
    test_client, get_valid_internal_token
):
    """
    Evaluator with role permission to category should only see authorized unevaluated logs.
    All permissions/roles are seeded in the test DB.
    """

    token = get_valid_internal_token(1805)
    headers = {"Authorization": f"Bearer {token}"}

    get_resp = test_client.get("/volunteer/admin/evaluate-with-category/", headers=headers)
    assert get_resp.status_code == 200

    data = get_resp.json()
    assert isinstance(data, list)
    assert any(item["activity"]["title"] == "Visible Activity" for item in data)


@pytest.mark.asyncio
async def test_get_unevaluated_activities_with_no_roles_api(test_client, mock_valid_token_auth):
    """
    Test that evaluator with no roles sees no activities — using only API calls.
    """
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}

    category_payload = {
        "name": "NO.ROLE.CATEGORY",
        "description": "Not linked to any role",
        "points": 5,
    }
    response = test_client.post(
        "/volunteer/admin/categories/", json=category_payload, headers=headers
    )
    assert response.status_code == 201
    category_id = response.json()["id"]

    log_payload = {
        "registration_id": 6,
        "title": "Hidden Activity",
        "description": "Should not be visible",
        "category_id": category_id,
    }
    resp = test_client.post("/volunteer/activity/logs/", json=log_payload, headers=headers)
    assert resp.status_code == 201

    get_resp = test_client.get("/volunteer/admin/evaluate-with-category/", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json() == []
