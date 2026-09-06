from src.app import activities


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location

    def test_static_index_is_available(self, client):
        # Arrange
        endpoint = "/static/index.html"

        # Act
        response = client.get(endpoint)

        # Assert
        assert response.status_code == 200
        assert "Mergington High School" in response.text


class TestActivities:
    def test_get_activities_returns_activity_details(self, client):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activity = response.json()[expected_activity]
        assert activity["description"]
        assert activity["schedule"]
        assert activity["max_participants"] == 12
        assert "michael@mergington.edu" in activity["participants"]


class TestSignup:
    def test_signup_adds_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in activities[activity_name]["participants"]

    def test_signup_rejects_duplicate_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Student is already signed up for this activity"
        )
        assert activities[activity_name]["participants"].count(email) == 1

    def test_signup_rejects_unknown_activity(self, client):
        # Arrange
        activity_name = "Robotics Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_requires_email(self, client):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422


class TestUnregister:
    def test_unregister_removes_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in activities[activity_name]["participants"]

    def test_unregister_rejects_unknown_activity(self, client):
        # Arrange
        activity_name = "Robotics Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_rejects_nonparticipant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "not.registered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Student is not signed up for this activity"
        )

    def test_activity_names_with_spaces_are_supported(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "space.test@mergington.edu"

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert signup_response.status_code == 200
        assert unregister_response.status_code == 200
