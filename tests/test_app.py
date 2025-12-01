import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_and_unregister():
    # Use a unique email for testing
    test_email = "pytestuser@mergington.edu"
    activity = "Chess Club"

    # Ensure not already signed up
    client.delete(f"/activities/{activity}/unregister", params={"email": test_email})

    # Sign up
    response = client.post(f"/activities/{activity}/signup", params={"email": test_email})
    assert response.status_code == 200
    assert f"Signed up {test_email}" in response.json()["message"]

    # Check participant is in list
    activities = client.get("/activities").json()
    assert test_email in activities[activity]["participants"]

    # Unregister
    response = client.delete(f"/activities/{activity}/unregister", params={"email": test_email})
    assert response.status_code == 200
    assert f"Unregistered {test_email}" in response.json()["message"]

    # Check participant is removed
    activities = client.get("/activities").json()
    assert test_email not in activities[activity]["participants"]

def test_signup_duplicate():
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already present
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_not_found():
    activity = "Chess Club"
    email = "notfound@mergington.edu"
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]

def test_activity_not_found():
    response = client.post("/activities/Nonexistent/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    response = client.delete("/activities/Nonexistent/unregister", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
