"""AI service for skills analysis and recommendations."""

import json
import os
from typing import Any, Dict

from openai import OpenAI

from config import settings
from devopscoach.services.web_search_service import get_web_search_service


class AIService:
    """Service for AI-powered skills analysis using OpenAI-compatible API."""

    def __init__(self):
        """Initialize the AI service with OpenAI client."""
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        base_url = settings.OPENAI_API_BASE or os.getenv(
            "OPENAI_API_BASE", "https://api.openai.com/v1"
        )
        model = settings.OPENAI_MODEL or os.getenv("OPENAI_MODEL", "gpt-4")

        if not api_key:
            # Allow service to be created without API key for testing
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.web_search = get_web_search_service()

    def analyze_skills(self, skills_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user's skills and provide personalized recommendations.

        :param skills_data: Dictionary containing user's skills assessment data
        :return: Dictionary with analysis results and recommendations
        """
        # If no client is available, use fallback directly
        if self.client is None:
            return self._get_fallback_analysis(
                skills_data, "OpenAI API key not configured"
            )

        # Fetch current DevOps trends via web search
        current_trends = self._get_current_trends_context(skills_data)

        prompt = self._build_analysis_prompt(skills_data, current_trends)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert DevOps career coach. Analyze the user's "
                            "current skills and provide actionable, specific recommendations "
                            "for transitioning into DevOps. Use the latest DevOps trends "
                            "and best practices provided in the context. Return results as valid JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_completion_tokens=2000,
            )

            content = response.choices[0].message.content or ""
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                return self._get_fallback_analysis(
                    skills_data,
                    "AI response was not valid JSON",
                )

            # Ensure required keys exist
            defaults = self._get_fallback_analysis(
                skills_data,
                "Partial AI response",
                include_note=False,
            )
            for key, value in defaults.items():
                if key not in result:
                    result[key] = value

            return result

        except Exception as e:
            # Return a fallback analysis if AI service fails
            return self._get_fallback_analysis(skills_data, str(e))

    def _get_current_trends_context(self, skills_data: Dict[str, Any]) -> str:
        """
        Fetch current DevOps trends and include them in the analysis.

        :param skills_data: User's skills assessment data
        :return: String with current DevOps trends context
        """
        if self.web_search.client is None:
            return ""

        try:
            # Get current DevOps trends
            trends = self.web_search.get_current_devops_trends()

            if not trends:
                return ""

            context = "\n\n**CURRENT DEVOPS TRENDS & BEST PRACTICES:**\n"
            for trend in trends[:5]:
                context += f"- {trend['title']}\n"
                context += f"  {trend['snippet']}\n"

            # Add user-specific relevant topics
            cloud_provider = skills_data.get("cloud_experience")
            if cloud_provider and cloud_provider != "none":
                cloud_trends = self.web_search.search_devops_resources(
                    f"{cloud_provider} best practices", max_results=2
                )
                if cloud_trends:
                    context += f"\n**Latest {cloud_provider.upper()} Best Practices:**\n"
                    for t in cloud_trends:
                        context += f"- {t['title']}\n  {t['snippet']}\n"

            return context
        except Exception:
            # If web search fails, continue without it
            return ""

    def _build_analysis_prompt(
        self, skills_data: Dict[str, Any], current_trends: str = ""
    ) -> str:
        """Build the prompt for AI analysis."""
        return f"""
Analyze the following candidate's skills for a DevOps career transition:

**Current Role:** {skills_data.get("current_role")}
**Years of Experience:** {skills_data.get("years_of_experience")}

**Technical Skills:**
- Programming Experience: {skills_data.get("programming_experience")}
- Programming Languages: {skills_data.get("programming_languages", "None specified")}
- Linux/Unix Experience: {skills_data.get("linux_experience")}
- Cloud Platform: {skills_data.get("cloud_experience")}
- Containers: {skills_data.get("containers_experience")}
- CI/CD: {skills_data.get("cicd_experience")}
- Infrastructure as Code: {skills_data.get("iac_experience")}
- Monitoring & Logging: {skills_data.get("monitoring_experience")}

**Learning Preferences:**
- Learning Style: {skills_data.get("preferred_learning_style")}
- Weekly Learning Hours: {skills_data.get("weekly_learning_hours")}
{current_trends}

IMPORTANT: As their DevOps Career Coach, recommend the most suitable DevOps roles based on their background (e.g., DevOps Engineer, SRE, Platform Engineer). Consider their current role and technical strengths when making recommendations.

Use the current DevOps trends provided above to ensure your recommendations reflect the latest best practices and in-demand skills.

Provide a JSON response with the following structure:
{{
    "overall_score": <1-100>,
    "readiness_level": <"beginner"|"intermediate"|"advanced"|"ready">,
    "strengths": [<list of 3-5 strengths>],
    "recommended_roles": [<list of 3-5 suitable DevOps roles based on their background>],
    "skill_gaps": [<list of 5-8 skill gaps with priorities>],
    "recommended_roadmap": [
        {{
            "phase": <phase number>,
            "title": <phase title>,
            "duration": <estimated weeks>,
            "skills": [<list of skills to learn>],
            "resources": [<specific resource recommendations>]
        }}
    ],
    "certifications": [<recommended certifications in order>],
    "projects": [
        {{
            "title": "<project title>",
            "description": "<detailed description of what to build>",
            "outcome": "<what this project demonstrates>",
            "level": <"Beginner"|"Intermediate"|"Advanced">
        }}
    ],
    "next_steps": [<immediate actionable steps>]
}}
"""

    def _get_fallback_analysis(
        self,
        skills_data: Dict[str, Any],
        error: str,
        *,
        include_note: bool = True,
    ) -> Dict[str, Any]:
        """Provide fallback analysis if AI service fails."""
        # Determine readiness level based on experience
        exp_level = skills_data.get("years_of_experience", "0-1")
        readiness_map = {
            "0-1": "beginner",
            "1-3": "intermediate",
            "3-5": "intermediate",
            "5-10": "advanced",
            "10+": "ready",
        }
        readiness = readiness_map.get(exp_level, "beginner")

        # Calculate basic score
        score = 20
        if skills_data.get("programming_experience") != "none":
            score += 15
        if skills_data.get("linux_experience") != "none":
            score += 15
        if skills_data.get("cloud_experience") != "none":
            score += 15
        if skills_data.get("containers_experience") != "none":
            score += 15
        if skills_data.get("cicd_experience") != "none":
            score += 10
        if skills_data.get("iac_experience") != "none":
            score += 10

        # Recommend roles based on background
        current_role = skills_data.get("current_role", "").lower()
        programming_level = skills_data.get("programming_experience", "none")

        recommended_roles = ["DevOps Engineer"]
        if (
            "developer" in current_role or "software" in current_role
        ) and programming_level in ["intermediate", "advanced"]:
            recommended_roles = ["DevOps Engineer", "Platform Engineer"]
        if (
            "operations" in current_role
            or "system" in current_role
            or "admin" in current_role
        ):
            recommended_roles = [
                "Site Reliability Engineer (SRE)",
                "DevOps Engineer",
            ]
        if "data" in current_role or "analytics" in current_role:
            recommended_roles = ["Data Platform Engineer", "DevOps Engineer"]

        result = {
            "overall_score": min(score, 100),
            "readiness_level": readiness,
            "strengths": [
                f"Experience: {skills_data.get('years_of_experience')}",
                "Taking initiative to assess skills",
            ],
            "recommended_roles": recommended_roles,
            "skill_gaps": [
                {"skill": "Linux Fundamentals", "priority": "high"},
                {"skill": "Container Technologies", "priority": "high"},
                {"skill": "CI/CD Pipelines", "priority": "high"},
                {"skill": "Cloud Platforms", "priority": "medium"},
                {"skill": "Infrastructure as Code", "priority": "medium"},
                {"skill": "Monitoring & Logging", "priority": "medium"},
            ],
            "recommended_roadmap": [
                {
                    "phase": 1,
                    "title": "Foundations",
                    "duration": "4-6 weeks",
                    "skills": ["Linux", "Bash Scripting", "Git"],
                    "resources": [
                        "Linux Journey (free)",
                        "Bash Guide for Beginners",
                        "Git & GitHub Bootcamp",
                    ],
                },
                {
                    "phase": 2,
                    "title": "Containerization",
                    "duration": "3-4 weeks",
                    "skills": ["Docker", "Docker Compose"],
                    "resources": [
                        "Docker Official Documentation",
                        "Docker Mastery Course",
                    ],
                },
            ],
            "certifications": [
                "AWS Cloud Practitioner",
                "HashiCorp Certified: Terraform Associate",
                "CKA: Certified Kubernetes Administrator",
            ],
            "projects": [
                {
                    "title": "Personal Portfolio on Cloud (Beginner)",
                    "description": "Host a static portfolio site: create site, push to GitHub, deploy to cloud (S3 + CloudFront or Azure Static Web Apps). Use Git for versioning.",
                    "outcome": "Shows Git use, cloud console familiarity, and ability to publish a service.",
                    "level": "Beginner",
                },
                {
                    "title": "Containerize a Simple App + CI (Intermediate)",
                    "description": "Take a simple web app (template or minimal Flask/Node), write a Dockerfile, set up GitHub Actions pipeline to build and push image to Docker Hub.",
                    "outcome": "Shows Docker, CI/CD pipeline knowledge, and automation.",
                    "level": "Intermediate",
                },
                {
                    "title": "Terraform Provisioning Lab (Intermediate)",
                    "description": "Use Terraform to provision a VM, storage and security group in your chosen cloud, then deploy the containerized app to that infrastructure.",
                    "outcome": "Demonstrates IaC, cloud resource management, and deployment automation.",
                    "level": "Intermediate",
                },
            ],
            "next_steps": [
                "Start with Linux fundamentals",
                "Practice Docker daily",
                "Join DevOps communities",
            ],
        }
        if include_note:
            result["fallback_note"] = f"AI service unavailable: {error}"

        return result


# Singleton instance
_ai_service = None


def get_ai_service() -> AIService:
    """Get or create the AI service singleton."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
