import pytest
from fastapi.testclient import TestClient
from app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset participant lists to a known state before each test."""
    original = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, participants in original.items():
        activities[name]["participants"] = participants


# --- GET /activities ---

def test_get_activities_returns_all():
    # Arrange - no setup needed, activities are pre-loaded

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert len(response.json()) > 0


def test_get_activities_has_expected_fields():
    # Arrange - no setup needed

    # Act
    response = client.get("/activities")

    # Assert
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# --- POST /activities/{name}/signup ---

def test_signup_success():
    # Arrange
    email = "new@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant():
    # Arrange
    email = "new@mergington.edu"
    activity_name = "Chess Club"

    # Act
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    response = client.get("/activities")
    assert email in response.json()[activity_name]["participants"]


def test_signup_unknown_activity():
    # Arrange
    email = "new@mergington.edu"
    activity_name = "Unknown Activity"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404


def test_signup_duplicate_rejected():
    # Arrange
    email = "dup@mergington.edu"
    activity_name = "Chess Club"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400


# --- DELETE /activities/{name}/signup ---

def test_unregister_success():
    # Arrange
    email = "temp@mergington.edu"
    activity_name = "Chess Club"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200


def test_unregister_removes_participant():
    # Arrange
    email = "temp@mergington.edu"
    activity_name = "Chess Club"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    response = client.get("/activities")
    assert email not in response.json()[activity_name]["participants"]


def test_unregister_unknown_activity():
    # Arrange
    email = "x@mergington.edu"
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404


def test_unregister_not_signed_up():
    # Arrange
    email = "nobody@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
