from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        activities.clear()
        activities.update(original_activities)


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    email = "new-student@mergington.edu"

    response = client.post(
        "/activities/Soccer Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Soccer Club"}
    assert email in client.get("/activities").json()["Soccer Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = "michael@mergington.edu"
    participant_count = len(activities["Chess Club"]["participants"])

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert len(activities["Chess Club"]["participants"]) == participant_count


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_removes_participant(client):
    email = "michael@mergington.edu"

    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_rejects_unregistered_participant(client):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "not-signed-up@mergington.edu"},
    )

    assert response.status_code == 404