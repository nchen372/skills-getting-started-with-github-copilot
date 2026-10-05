import src.app as app_module
from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def activity_store(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activity_store):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_details(client, activity_store):
    # Arrange
    expected_activities = activity_store.copy()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activity_store):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activity_store["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client, activity_store):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 409
    assert response.json() == {"detail": "Already signed up"}
    assert activity_store["Chess Club"]["participants"] == [email]


def test_signup_rejects_unknown_activity(client, activity_store):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(f"/activities/Unknown Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_store["Chess Club"]["participants"] == ["existing@mergington.edu"]


def test_unregister_removes_participant(client, activity_store):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert activity_store["Chess Club"]["participants"] == []


def test_unregister_rejects_unknown_activity(client, activity_store):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete(f"/activities/Unknown Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activity_store["Chess Club"]["participants"] == [email]


def test_unregister_rejects_nonparticipant(client, activity_store):
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}
    assert activity_store["Chess Club"]["participants"] == ["existing@mergington.edu"]