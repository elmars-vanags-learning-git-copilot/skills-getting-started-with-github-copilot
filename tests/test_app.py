import copy

from fastapi.testclient import TestClient
import pytest

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to snapshot and restore the in-memory activities store between tests."""
    original = copy.deepcopy(app_module.activities)
    try:
        yield
    finally:
        app_module.activities.clear()
        app_module.activities.update(original)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # basic sanity check that a known activity exists
    assert "Chess Club" in data


def test_signup_and_duplicate():
    activity = "Chess Club"
    email = "tester@mergington.edu"

    # Ensure email is not present initially
    if email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(email)

    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Duplicate signup should return 400
    res2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert res2.status_code == 400


def test_unregister():
    activity = "Chess Club"
    email = "to_remove@mergington.edu"

    # Ensure email present before removal
    if email not in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].append(email)

    res = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert res.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # Unregistering again should return 404
    res2 = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert res2.status_code == 404
