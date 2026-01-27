"""Celery tasks for AI workflows."""

from celery import shared_task

from devopscoach.extensions import db
from devopscoach.models import SkillAssessment
from devopscoach.services.ai_service import get_ai_service


@shared_task(name="devopscoach.tasks.ai_tasks.analyze_skills_assessment")
def analyze_skills_assessment(assessment_id: int) -> bool:
    """Generate AI recommendations for a skills assessment."""
    assessment = SkillAssessment.query.get(assessment_id)
    if assessment is None or assessment.assessment_data is None:
        return False

    try:
        ai_service = get_ai_service()
        recommendations = ai_service.analyze_skills(
            assessment.assessment_data
        )
        assessment.recommendations = recommendations
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        raise
