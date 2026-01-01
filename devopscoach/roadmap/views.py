"""Views for roadmap management."""

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from devopscoach.extensions import db
from devopscoach.models import CustomRoadmap, SkillAssessment
from devopscoach.roadmap import roadmap
from devopscoach.roadmap.forms import CreateRoadmapForm, UpdateMilestoneForm


@roadmap.route("/")
@login_required
def list_roadmaps():
    """Display all roadmaps for the current user."""
    roadmaps = (
        CustomRoadmap.query.filter_by(user_id=current_user.id)
        .order_by(CustomRoadmap.created_at.desc())
        .all()
    )

    return render_template("roadmap/list.html", roadmaps=roadmaps)


@roadmap.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new learning roadmap.

    Optional assessment_id query parameter can be passed to use a specific
    assessment as the basis for the roadmap.
    """
    form = CreateRoadmapForm()
    assessment_id = request.args.get("assessment_id", type=int)

    # Get the specific assessment if assessment_id provided, otherwise get latest
    if assessment_id:
        assessment = SkillAssessment.query.filter_by(
            id=assessment_id,
            user_id=current_user.id,
        ).first()
    else:
        assessment = SkillAssessment.query.filter_by(
            user_id=current_user.id
        ).first()

    if form.validate_on_submit():
        # Generate roadmap data
        roadmap_data = _generate_roadmap_data(
            target_role=form.target_role.data,
            timeline_weeks=int(form.timeline_weeks.data),
            focus_areas=form.focus_areas.data,
            assessment_data=assessment.assessment_data if assessment else None,
        )

        roadmap = CustomRoadmap(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            roadmap_data=roadmap_data,
        )
        db.session.add(roadmap)
        db.session.commit()

        flash("Your learning roadmap has been created!", "success")
        return redirect(url_for("roadmap.detail", roadmap_id=roadmap.id))

    # Pre-fill with assessment data if available
    if assessment and request.method == "GET":
        if hasattr(assessment, "recommendations") and assessment.recommendations:
            rec = assessment.recommendations
            # Pre-fill target role with first recommended role
            if "recommended_roles" in rec and rec["recommended_roles"]:
                form.target_role.data = rec["recommended_roles"][0]
            # Pre-fill focus areas from skill gaps
            if "skill_gaps" in rec and rec["skill_gaps"]:
                focus_areas = ", ".join([gap["skill"] for gap in rec["skill_gaps"][:5]])
                form.focus_areas.data = focus_areas
            # Set default title based on target role
            if "recommended_roles" in rec and rec["recommended_roles"]:
                form.title.data = f"My Path to {rec['recommended_roles'][0]}"

    return render_template(
        "roadmap/create.html",
        form=form,
        assessment=assessment,
        from_assessment=bool(assessment_id),
    )


@roadmap.route("/<int:roadmap_id>")
@login_required
def detail(roadmap_id):
    """Display a specific roadmap."""
    roadmap = CustomRoadmap.query.filter_by(
        id=roadmap_id,
        user_id=current_user.id,
    ).first_or_404()

    # Calculate progress
    progress = _calculate_roadmap_progress(roadmap.roadmap_data)

    return render_template(
        "roadmap/detail.html", roadmap=roadmap, progress=progress
    )


@roadmap.route("/<int:roadmap_id>/milestone/<int:milestone_index>", methods=["POST"])
@login_required
def update_milestone(roadmap_id, milestone_index):
    """Update milestone progress."""
    roadmap = CustomRoadmap.query.filter_by(
        id=roadmap_id,
        user_id=current_user.id,
    ).first_or_404()

    form = UpdateMilestoneForm()

    if form.validate_on_submit():
        # Update milestone status
        milestones = roadmap.roadmap_data.get("milestones", [])
        if 0 <= milestone_index < len(milestones):
            milestones[milestone_index]["status"] = form.status.data
            if form.notes.data:
                milestones[milestone_index]["notes"] = form.notes.data

            roadmap.roadmap_data["milestones"] = milestones
            db.session.commit()

            flash("Milestone updated!", "success")

    return redirect(url_for("roadmap.detail", roadmap_id=roadmap_id))


@roadmap.route("/<int:roadmap_id>/delete", methods=["POST"])
@login_required
def delete(roadmap_id):
    """Delete a roadmap."""
    roadmap = CustomRoadmap.query.filter_by(
        id=roadmap_id,
        user_id=current_user.id,
    ).first_or_404()

    db.session.delete(roadmap)
    db.session.commit()

    flash("Roadmap deleted.", "success")
    return redirect(url_for("roadmap.list_roadmaps"))


def _generate_roadmap_data(
    target_role: str,
    timeline_weeks: int,
    focus_areas: str = "",
    assessment_data: dict = None,
) -> dict:
    """Generate roadmap data based on user inputs and assessment.

    Args:
        target_role: The role the user is targeting
        timeline_weeks: Duration of the roadmap in weeks
        focus_areas: Comma-separated list of focus areas
        assessment_data: Optional assessment data for personalization

    Returns:
        Dictionary with roadmap structure
    """
    # Parse focus areas
    areas = (
        [a.strip() for a in focus_areas.split(",")]
        if focus_areas
        else ["Linux", "Docker", "CI/CD", "Cloud", "Terraform"]
    )

    # Determine number of phases based on timeline
    weeks_per_phase = max(2, timeline_weeks // 4)
    num_phases = min(6, max(3, timeline_weeks // weeks_per_phase))

    milestones = []

    # Phase 1: Foundations
    milestones.append({
        "phase": 1,
        "title": "Foundation",
        "duration_weeks": weeks_per_phase,
        "skills": ["Linux Command Line", "Bash Scripting", "Git & GitHub", "Networking Basics"],
        "resources": [
            {"title": "Linux Journey", "url": "https://linuxjourney.com", "type": "course"},
            {"title": "Bash Guide for Beginners", "url": "https://tldp.org/LDP/Bash-Beginners-Guide/html/", "type": "article"},
        ],
        "projects": ["Set up a Linux VM", "Create git repository with commits"],
        "status": "not_started",
        "notes": None,
    })

    # Phase 2: Containerization
    milestones.append({
        "phase": 2,
        "title": "Containerization",
        "duration_weeks": weeks_per_phase,
        "skills": ["Docker", "Docker Compose", "Container Orchestration Basics"],
        "resources": [
            {"title": "Docker Official Documentation", "url": "https://docs.docker.com", "type": "docs"},
            {"title": "Docker Mastery", "url": "https://www.udemy.com/course/docker-mastery", "type": "course"},
        ],
        "projects": ["Containerize a web app", "Create multi-container app with Compose"],
        "status": "not_started",
        "notes": None,
    })

    if num_phases >= 3:
        milestones.append({
            "phase": 3,
            "title": "Continuous Integration",
            "duration_weeks": weeks_per_phase,
            "skills": ["CI Concepts", "GitHub Actions", "Testing", "Artifact Management"],
            "resources": [
                {"title": "GitHub Actions Docs", "url": "https://docs.github.com/actions", "type": "docs"},
            ],
            "projects": ["Build CI pipeline for Docker app", "Add automated tests"],
            "status": "not_started",
            "notes": None,
        })

    if num_phases >= 4:
        milestones.append({
            "phase": 4,
            "title": "Cloud Platforms",
            "duration_weeks": weeks_per_phase,
            "skills": ["AWS/GCP/Azure Basics", "Compute Services", "Storage", "Networking"],
            "resources": [
                {"title": "AWS Cloud Practitioner", "url": "https://aws.amazon.com/certification/", "type": "cert"},
            ],
            "projects": ["Deploy app to cloud platform", "Set up cloud storage"],
            "status": "not_started",
            "notes": None,
        })

    if num_phases >= 5:
        milestones.append({
            "phase": 5,
            "title": "Infrastructure as Code",
            "duration_weeks": weeks_per_phase,
            "skills": ["Terraform", "Configuration Management", "Immutable Infrastructure"],
            "resources": [
                {"title": "Terraform Docs", "url": "https://www.terraform.io/docs", "type": "docs"},
            ],
            "projects": ["Provision infrastructure with Terraform", "Set up Ansible playbooks"],
            "status": "not_started",
            "notes": None,
        })

    if num_phases >= 6:
        milestones.append({
            "phase": 6,
            "title": "Advanced Operations",
            "duration_weeks": weeks_per_phase,
            "skills": ["Kubernetes", "Monitoring & Logging", "Security", "Incident Response"],
            "resources": [
                {"title": "Kubernetes Documentation", "url": "https://kubernetes.io/docs", "type": "docs"},
            ],
            "projects": ["Deploy app to Kubernetes", "Set up monitoring stack"],
            "status": "not_started",
            "notes": None,
        })

    return {
        "target_role": target_role,
        "timeline_weeks": timeline_weeks,
        "focus_areas": areas,
        "milestones": milestones,
    }


def _calculate_roadmap_progress(roadmap_data: dict) -> dict:
    """Calculate progress percentage for a roadmap.

    Args:
        roadmap_data: The roadmap data dictionary

    Returns:
        Dictionary with progress stats
    """
    milestones = roadmap_data.get("milestones", [])

    if not milestones:
        return {"percent": 0, "completed": 0, "total": 0}

    completed = sum(
        1
        for m in milestones
        if m.get("status") == "completed"
    )
    in_progress = sum(
        1
        for m in milestones
        if m.get("status") == "in_progress"
    )
    total = len(milestones)

    # Weight completed as 100%, in_progress as 50%
    percent = int(((completed * 100) + (in_progress * 50)) / total) if total > 0 else 0

    return {
        "percent": percent,
        "completed": completed,
        "in_progress": in_progress,
        "total": total,
    }