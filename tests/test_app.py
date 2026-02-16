"""
Comprehensive tests for the Mergington High School Activities API
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Drama Club" in data
        assert "Art Studio" in data
        assert "Debate Team" in data
        assert "Math Club" in data
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_includes_required_fields(self, client):
        """Test that activities include all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        # Check first activity has all required fields
        activity = data["Basketball Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "netstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "netstudent@mergington.edu" in data["message"]
        assert "Basketball Team" in data["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "newstudent@mergington.edu"
        
        # Sign up
        response = client.post(
            "/activities/Soccer Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Soccer Club"]["participants"]
    
    def test_signup_duplicate_student(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"].lower() or "Student already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test that signup fails for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_multiple_different_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "student@mergington.edu"
        
        # Sign up for Basketball Team
        response1 = client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Soccer Club
        response2 = client.post(
            "/activities/Soccer Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Basketball Team"]["participants"]
        assert email in data["Soccer Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "alex@mergington.edu" in data["message"]
        assert "Basketball Team" in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant from the activity"""
        email = "alex@mergington.edu"
        
        # Verify participant exists
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Basketball Team"]["participants"]
        
        # Unregister
        response = client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email not in data["Basketball Team"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test that unregister fails for a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_unregister_student_not_registered(self, client):
        """Test that unregister fails if student is not registered"""
        response = client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_after_signup(self, client):
        """Test full signup then unregister cycle"""
        email = "tempstudent@mergington.edu"
        activity = "Drama Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email not in data[activity]["participants"]


class TestEdgeCases:
    """Tests for edge cases and special scenarios"""
    
    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with email containing special characters"""
        email = "student+special@mergington.edu"
        response = client.post(
            "/activities/Math Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Math Club"]["participants"]
    
    def test_activity_name_case_sensitivity(self, client):
        """Test that activity names are case-sensitive"""
        response = client.post(
            "/activities/basketball team/signup",  # lowercase
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_signup_multiple_students_to_same_activity(self, client):
        """Test that multiple students can sign up for the same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                "/activities/Art Studio/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all students were added
        activities_response = client.get("/activities")
        data = activities_response.json()
        for email in emails:
            assert email in data["Art Studio"]["participants"]
    
    def test_activity_participant_count_after_signup(self, client):
        """Test that participant count is correct after signup"""
        activity = "Chess Club"
        email = "newchesser@mergington.edu"
        
        # Get initial count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()[activity]["participants"])
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Get new count
        activities_response = client.get("/activities")
        new_count = len(activities_response.json()[activity]["participants"])
        
        assert new_count == initial_count + 1
    
    def test_activity_participant_count_after_unregister(self, client):
        """Test that participant count is correct after unregister"""
        activity = "Programming Class"
        email = "emma@mergington.edu"
        
        # Get initial count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()[activity]["participants"])
        
        # Unregister
        client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        
        # Get new count
        activities_response = client.get("/activities")
        new_count = len(activities_response.json()[activity]["participants"])
        
        assert new_count == initial_count - 1
