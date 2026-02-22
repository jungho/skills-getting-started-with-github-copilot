"""
Tests for the Mergington High School API signup and unregister endpoints.
Uses the AAA (Arrange-Act-Assert) testing pattern.
"""

from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


# ── Signup (POST) Tests ──────────────────────────────────────────────


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup"""

    def test_signup_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in activities[activity_name]["participants"]

        # Cleanup – reverse the mutation so other tests see original state
        activities[activity_name]["participants"].remove(email)

    def test_signup_duplicate(self):
        # Arrange – use a pre-seeded participant
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_nonexistent_activity(self):
        # Arrange
        fake_activity = "Underwater Basket Weaving"
        email = "someone@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


# ── Unregister (DELETE) Tests ─────────────────────────────────────────


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/signup"""

    def test_unregister_success(self):
        # Arrange – sign up a temporary participant first
        activity_name = "Chess Club"
        email = "tempstudent@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_signed_up(self):
        # Arrange
        activity_name = "Chess Club"
        email = "ghost@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_nonexistent_activity(self):
        # Arrange
        fake_activity = "Underwater Basket Weaving"
        email = "someone@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{fake_activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
