import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

class TestActivitiesAPI:
    """Test cases for the activities API endpoints"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()

        # Check that we have activities
        assert isinstance(activities, dict)
        assert len(activities) > 0

        # Check structure of first activity
        first_activity = next(iter(activities.values()))
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)

    def test_get_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]

    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        # First, get the activities to find one to sign up for
        response = client.get("/activities")
        activities = response.json()
        activity_name = list(activities.keys())[0]  # Get first activity

        # Sign up a new participant
        email = "test@example.com"
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert signup_response.status_code == 200
        result = signup_response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

        # Verify the participant was added
        updated_response = client.get("/activities")
        updated_activities = updated_response.json()
        assert email in updated_activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistentActivity/signup",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_signup_already_registered(self, client):
        """Test signup when already registered"""
        # First, get an activity and its existing participants
        response = client.get("/activities")
        activities = response.json()
        activity_name = list(activities.keys())[0]
        existing_participants = activities[activity_name]["participants"]

        # If no participants, add one first
        if not existing_participants:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": "temp@example.com"}
            )
            existing_participants = ["temp@example.com"]

        # Try to sign up the same participant again
        email = existing_participants[0]
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert signup_response.status_code == 400
        result = signup_response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"]

    def test_delete_participant(self, client):
        """Test deleting a participant (placeholder test)"""
        # Note: The current delete endpoint uses participant_id but participants are emails
        # This test is for the placeholder endpoint
        response = client.delete("/participants/1")
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "unregistered" in result["message"]