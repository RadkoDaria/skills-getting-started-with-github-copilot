"""
Tests for the Mergington High School extracurricular activities API
"""

import pytest


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""
    
    def test_get_activities_returns_dict(self, client):
        """Test that get_activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that all expected activities are in the response"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Volleyball Club",
            "Track and Field",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Science Club",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing field {field}"
    
    def test_participants_list_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_data in data.values():
            assert isinstance(activity_data["participants"], list)
    
    def test_max_participants_is_positive(self, client):
        """Test that max_participants is a positive integer"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_data in data.values():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_new_student(self, clean_activities):
        """Test successful signup of a new student"""
        response = clean_activities.post(
            "/activities/Volleyball Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up test@mergington.edu for Volleyball Club" in data["message"]
    
    def test_signup_adds_student_to_activity(self, clean_activities):
        """Test that signup actually adds student to activity participants"""
        email = "alex@mergington.edu"
        clean_activities.post(
            f"/activities/Drama Club/signup?email={email}"
        )
        
        # Verify student was added
        response = clean_activities.get("/activities")
        data = response.json()
        assert email in data["Drama Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, clean_activities):
        """Test that signup fails for nonexistent activity"""
        response = clean_activities.post(
            "/activities/Fake Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_student(self, clean_activities):
        """Test that signup fails if student is already signed up"""
        email = "michael@mergington.edu"
        # Michael is already in Chess Club
        response = clean_activities.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "Student already signed up" in data["detail"]
    
    def test_signup_multiple_students_same_activity(self, clean_activities):
        """Test that multiple students can sign up for the same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = clean_activities.post(
                f"/activities/Science Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all students were added
        response = clean_activities.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data["Science Club"]["participants"]
    
    def test_signup_same_student_different_activities(self, clean_activities):
        """Test that a student can sign up for multiple activities"""
        email = "versatile@mergington.edu"
        activities_list = ["Volleyball Club", "Track and Field", "Art Studio"]
        
        for activity in activities_list:
            response = clean_activities.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify student is in all activities
        response = clean_activities.get("/activities")
        data = response.json()
        for activity in activities_list:
            assert email in data[activity]["participants"]
    
    def test_signup_response_format(self, clean_activities):
        """Test that signup response has correct format"""
        response = clean_activities.post(
            "/activities/Art Studio/signup?email=artist@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)


class TestActivityData:
    """Tests for the activity data integrity"""
    
    def test_chess_club_initial_participants(self, client):
        """Test that Chess Club has initial participants"""
        response = client.get("/activities")
        data = response.json()
        chess_participants = data["Chess Club"]["participants"]
        
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants
    
    def test_programming_class_initial_participants(self, client):
        """Test that Programming Class has initial participants"""
        response = client.get("/activities")
        data = response.json()
        prog_participants = data["Programming Class"]["participants"]
        
        assert "emma@mergington.edu" in prog_participants
        assert "sophia@mergington.edu" in prog_participants
    
    def test_activities_have_descriptions(self, client):
        """Test that all activities have meaningful descriptions"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            desc = activity_data["description"]
            assert len(desc) > 0
            assert isinstance(desc, str)
    
    def test_activities_have_schedules(self, client):
        """Test that all activities have schedule information"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_data in data.values():
            schedule = activity_data["schedule"]
            assert len(schedule) > 0
            assert isinstance(schedule, str)
