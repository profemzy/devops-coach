"""Views for skills assessment."""

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from devopscoach.extensions import db
from devopscoach.models import SkillAssessment
from devopscoach.skills import skills
from devopscoach.skills.forms import SkillsAssessmentForm
from devopscoach.tasks.ai_tasks import analyze_skills_assessment


@skills.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    """Skills assessment form."""
    form = SkillsAssessmentForm()

    if form.validate_on_submit():
        # Collect form data
        skills_data = {
            "current_role": form.current_role.data,
            "years_of_experience": form.years_of_experience.data,
            "programming_experience": form.programming_experience.data,
            "programming_languages": form.programming_languages.data,
            "linux_experience": form.linux_experience.data,
            "cloud_experience": form.cloud_experience.data,
            "containers_experience": form.containers_experience.data,
            "cicd_experience": form.cicd_experience.data,
            "iac_experience": form.iac_experience.data,
            "monitoring_experience": form.monitoring_experience.data,
            "preferred_learning_style": form.preferred_learning_style.data,
            "weekly_learning_hours": form.weekly_learning_hours.data,
        }

        # Create or update assessment
        assessment = SkillAssessment.query.filter_by(
            user_id=current_user.id
        ).first()

        if assessment:
            # Update existing assessment
            assessment.assessment_data = skills_data
            # Reset results as they need to be regenerated
            assessment.recommendations = None
        else:
            # Create new assessment
            assessment = SkillAssessment(
                user_id=current_user.id,
                assessment_data=skills_data,
            )
            db.session.add(assessment)

        db.session.commit()

        flash(
            "Skills assessment submitted! Analyzing your profile...", "success"
        )
        return redirect(url_for("skills.results", assessment_id=assessment.id))

    # Check for existing assessment
    existing_assessment = SkillAssessment.query.filter_by(
        user_id=current_user.id
    ).first()
    if existing_assessment and request.method == "GET":
        # Pre-fill form with existing data
        for field, value in existing_assessment.assessment_data.items():
            if hasattr(form, field):
                getattr(form, field).data = value

    return render_template("skills/assessment.html", form=form)


@skills.route("/results/<int:assessment_id>")
@login_required
def results(assessment_id):
    """Display skills assessment results."""
    assessment = SkillAssessment.query.filter_by(
        id=assessment_id,
        user_id=current_user.id,
    ).first_or_404()

    recommendations = assessment.recommendations or {}
    is_pending = (
        isinstance(recommendations, dict)
        and recommendations.get("status") == "pending"
    )

    if assessment.recommendations is None or is_pending:
        if request.args.get("retry") == "1" or assessment.recommendations is None:
            assessment.recommendations = {"status": "pending"}
            db.session.commit()
            analyze_skills_assessment.delay(assessment.id)

        return render_template(
            "skills/results_loading.html",
            assessment=assessment,
        )

    recommendations = assessment.recommendations

    return render_template(
        "skills/results.html",
        assessment=assessment,
        recommendations=recommendations,
    )


@skills.route("/results/<int:assessment_id>/status")
@login_required
def results_status(assessment_id):
    """Return whether recommendations are ready."""
    assessment = SkillAssessment.query.filter_by(
        id=assessment_id,
        user_id=current_user.id,
    ).first_or_404()

    recommendations = assessment.recommendations or {}
    ready = not (
        isinstance(recommendations, dict)
        and recommendations.get("status") == "pending"
    )

    return jsonify({"ready": ready})


@skills.route("/history")
@login_required
def history():
    """Display user's assessment history."""
    assessments = (
        SkillAssessment.query.filter_by(user_id=current_user.id)
        .order_by(SkillAssessment.assessment_date.desc())
        .all()
    )

    return render_template("skills/history.html", assessments=assessments)
