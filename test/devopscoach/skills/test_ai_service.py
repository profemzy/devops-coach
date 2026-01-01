"""Tests for AI service."""

from devopscoach.services.ai_service import AIService, get_ai_service


class TestAIService:
    """Tests for AIService class."""

    def test_ai_service_initialization(self):
        """AI service should initialize with or without API key."""
        service = AIService()
        # Client may be None if no API key is set (test environment)
        assert service.model is not None
        # Service should still be functional with fallback
        assert hasattr(service, "analyze_skills")

    def test_analyze_skills_returns_structure(self):
        """analyze_skills should return a properly structured response."""
        service = AIService()

        skills_data = {
            "current_role": "Software Developer",
            "years_of_experience": "3-5",
            "programming_experience": "intermediate",
            "programming_languages": "Python, JavaScript",
            "linux_experience": "basic",
            "cloud_experience": "none",
            "containers_experience": "none",
            "cicd_experience": "none",
            "iac_experience": "none",
            "monitoring_experience": "none",
            "career_goals": "Become a DevOps engineer",
            "target_roles": "DevOps Engineer",
            "preferred_learning_style": "hands-on",
            "weekly_learning_hours": "5-10",
        }

        result = service.analyze_skills(skills_data)

        # Check required fields exist
        assert "overall_score" in result
        assert "readiness_level" in result
        assert "strengths" in result
        assert "skill_gaps" in result
        assert "recommended_roadmap" in result
        assert "certifications" in result
        assert "projects" in result
        assert "next_steps" in result

    def test_fallback_analysis_on_error(self, monkeypatch):
        """Service should return fallback analysis if AI fails."""
        # Set a mock API key so client is initialized
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        service = AIService()

        # Mock the client to raise an exception
        class MockError(Exception):
            pass

        def mock_create(*args, **kwargs):
            raise MockError("API unavailable")

        if service.client:
            monkeypatch.setattr(
                service.client.chat.completions, "create", mock_create
            )

        skills_data = {
            "current_role": "Developer",
            "years_of_experience": "1-3",
            "programming_experience": "basic",
            "linux_experience": "none",
            "cloud_experience": "none",
            "containers_experience": "none",
            "cicd_experience": "none",
            "iac_experience": "none",
            "monitoring_experience": "none",
            "career_goals": "Transition to DevOps",
            "preferred_learning_style": "visual",
            "weekly_learning_hours": "3-5",
        }

        result = service.analyze_skills(skills_data)

        # Should still return a valid structure
        assert "overall_score" in result
        assert "readiness_level" in result
        assert "fallback_note" in result
        assert "API unavailable" in result["fallback_note"]

    def test_score_calculation_in_fallback(self, monkeypatch):
        """Fallback analysis should calculate score based on skills."""
        # Ensure no API key so we use fallback directly
        # Need to patch settings since env var is already loaded
        import config.settings
        monkeypatch.setattr(config.settings, "OPENAI_API_KEY", None)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        service = AIService()
        assert service.client is None, "Client should be None without API key"

        # User with many skills
        skills_data_high = {
            "current_role": "Senior Developer",
            "years_of_experience": "5-10",
            "programming_experience": "advanced",
            "linux_experience": "advanced",
            "cloud_experience": "multiple",
            "containers_experience": "kubernetes",
            "cicd_experience": "advanced",
            "iac_experience": "terraform",
            "monitoring_experience": "advanced",
            "career_goals": "SRE role",
            "preferred_learning_style": "hands-on",
            "weekly_learning_hours": "5-10",
        }

        result_high = service.analyze_skills(skills_data_high)
        assert result_high["overall_score"] >= 70  # Should be relatively high

        # User with few skills
        skills_data_low = {
            "current_role": "Junior Developer",
            "years_of_experience": "0-1",
            "programming_experience": "none",
            "linux_experience": "none",
            "cloud_experience": "none",
            "containers_experience": "none",
            "cicd_experience": "none",
            "iac_experience": "none",
            "monitoring_experience": "none",
            "career_goals": "Learn DevOps",
            "preferred_learning_style": "visual",
            "weekly_learning_hours": "1-3",
        }

        result_low = service.analyze_skills(skills_data_low)
        assert result_low["overall_score"] < result_high["overall_score"]


class TestGetAIService:
    """Tests for get_ai_service singleton function."""

    def test_get_ai_service_returns_singleton(self):
        """get_ai_service should return the same instance."""
        service1 = get_ai_service()
        service2 = get_ai_service()
        assert service1 is service2

    def test_get_ai_service_returns_ai_service_instance(self):
        """get_ai_service should return an AIService instance."""
        service = get_ai_service()
        assert isinstance(service, AIService)
