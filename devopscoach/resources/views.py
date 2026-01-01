"""Views for resources blueprint."""

from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from devopscoach.extensions import db
from devopscoach.models import LearningResource
from devopscoach.resources import resources
from devopscoach.resources.forms import CreateResourceForm, EditResourceForm


@resources.route("/")
@login_required
def list_resources():
    """Display all resources for the current user."""
    # Get filter parameters
    resource_type = request.args.get("type")
    difficulty = request.args.get("difficulty")
    status = request.args.get("status")  # "completed" or "in_progress"
    tag = request.args.get("tag")
    search = request.args.get("search", "")

    # Build query
    query = LearningResource.query.filter_by(user_id=current_user.id)

    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if status == "completed":
        query = query.filter_by(is_completed=True)
    elif status == "in_progress":
        query = query.filter_by(is_completed=False)
    if search:
        query = query.filter(
            LearningResource.title.ilike(f"%{search}%")
            | LearningResource.description.ilike(f"%{search}%")
        )

    resources_list = (
        query.order_by(
            LearningResource.is_completed.asc(),
            LearningResource.created_at.desc(),
        )
        .all()
    )

    # Get all unique tags for filter sidebar
    all_tags = set()
    for resource in resources_list:
        if resource.tags:
            all_tags.update(resource.tags)

    # Calculate stats
    total_resources = len(resources_list)
    completed_resources = sum(1 for r in resources_list if r.is_completed)
    total_hours = sum(r.estimated_hours or 0 for r in resources_list)

    return render_template(
        "resources/list.html",
        resources=resources_list,
        all_tags=sorted(all_tags),
        stats={
            "total": total_resources,
            "completed": completed_resources,
            "hours": total_hours,
        },
        filters={
            "type": resource_type,
            "difficulty": difficulty,
            "status": status,
            "tag": tag,
            "search": search,
        },
    )


@resources.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new learning resource."""
    form = CreateResourceForm()

    if form.validate_on_submit():
        # Parse tags
        tags = (
            [tag.strip() for tag in form.tags.data.split(",")]
            if form.tags.data
            else []
        )

        resource = LearningResource(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            resource_type=form.resource_type.data,
            url=form.url.data,
            difficulty=form.difficulty.data,
            estimated_hours=form.estimated_hours.data,
            tags=tags if tags else None,
        )
        db.session.add(resource)
        db.session.commit()

        flash("Learning resource added!", "success")
        return redirect(url_for("resources.list_resources"))

    return render_template("resources/create.html", form=form)


@resources.route("/<int:resource_id>")
@login_required
def detail(resource_id):
    """Display a specific resource."""
    resource = LearningResource.query.filter_by(
        id=resource_id,
        user_id=current_user.id,
    ).first_or_404()

    return render_template("resources/detail.html", resource=resource)


@resources.route("/<int:resource_id>/edit", methods=["GET", "POST"])
@login_required
def edit(resource_id):
    """Edit an existing resource."""
    resource = LearningResource.query.filter_by(
        id=resource_id,
        user_id=current_user.id,
    ).first_or_404()

    form = EditResourceForm(obj=resource)

    if form.validate_on_submit():
        # Parse tags
        tags = (
            [tag.strip() for tag in form.tags.data.split(",")]
            if form.tags.data
            else []
        )

        resource.title = form.title.data
        resource.description = form.description.data
        resource.resource_type = form.resource_type.data
        resource.url = form.url.data
        resource.difficulty = form.difficulty.data
        resource.estimated_hours = form.estimated_hours.data
        resource.tags = tags if tags else None

        # Handle completion status
        is_completed = form.is_completed.data == "true"
        if is_completed and not resource.is_completed:
            resource.is_completed = True
            resource.completion_date = datetime.utcnow()
        elif not is_completed:
            resource.is_completed = False
            resource.completion_date = None

        db.session.commit()

        flash("Resource updated!", "success")
        return redirect(url_for("resources.detail", resource_id=resource.id))

    # Pre-fill form with current values
    if resource.is_completed:
        form.is_completed.data = "true"
    else:
        form.is_completed.data = "false"

    if resource.tags:
        form.tags.data = ", ".join(resource.tags)

    return render_template("resources/edit.html", form=form, resource=resource)


@resources.route("/<int:resource_id>/toggle", methods=["POST"])
@login_required
def toggle_complete(resource_id):
    """Toggle resource completion status."""
    resource = LearningResource.query.filter_by(
        id=resource_id,
        user_id=current_user.id,
    ).first_or_404()

    resource.is_completed = not resource.is_completed
    if resource.is_completed:
        resource.completion_date = datetime.utcnow()
        flash("Resource marked as complete!", "success")
    else:
        resource.completion_date = None
        flash("Resource marked as in progress.", "info")

    db.session.commit()
    return redirect(url_for("resources.list_resources"))


@resources.route("/<int:resource_id>/delete", methods=["POST"])
@login_required
def delete(resource_id):
    """Delete a resource."""
    resource = LearningResource.query.filter_by(
        id=resource_id,
        user_id=current_user.id,
    ).first_or_404()

    db.session.delete(resource)
    db.session.commit()

    flash("Resource deleted.", "success")
    return redirect(url_for("resources.list_resources"))


@resources.route("/explore")
@login_required
def explore():
    """Explore recommended resources by category."""
    # Predefined resource recommendations organized by category
    recommendations = {
        "Linux & Shell Scripting": [
            {
                "title": "Linux Journey",
                "url": "https://linuxjourney.com",
                "type": "tutorial",
                "difficulty": "beginner",
                "description": "Interactive tutorial covering Linux fundamentals",
            },
            {
                "title": "Bash Guide for Beginners",
                "url": "https://tldp.org/LDP/Bash-Beginners-Guide/html/",
                "type": "article",
                "difficulty": "beginner",
                "description": "Comprehensive guide to Bash scripting",
            },
        ],
        "Docker & Containers": [
            {
                "title": "Docker Official Documentation",
                "url": "https://docs.docker.com",
                "type": "documentation",
                "difficulty": "intermediate",
                "description": "Official docs covering all Docker concepts",
            },
            {
                "title": "Docker Mastery Udemy Course",
                "url": "https://www.udemy.com/course/docker-mastery",
                "type": "course",
                "difficulty": "intermediate",
                "description": "Hands-on Docker course with real projects",
            },
        ],
        "Kubernetes": [
            {
                "title": "Kubernetes Documentation",
                "url": "https://kubernetes.io/docs",
                "type": "documentation",
                "difficulty": "advanced",
                "description": "Official K8s documentation and tutorials",
            },
        ],
        "CI/CD": [
            {
                "title": "GitHub Actions Docs",
                "url": "https://docs.github.com/actions",
                "type": "documentation",
                "difficulty": "beginner",
                "description": "Learn to build CI/CD pipelines with GitHub Actions",
            },
        ],
        "Cloud Platforms": [
            {
                "title": "AWS Cloud Practitioner Certification",
                "url": "https://aws.amazon.com/certification/",
                "type": "certification",
                "difficulty": "beginner",
                "description": "Entry-level AWS certification",
            },
        ],
        "Infrastructure as Code": [
            {
                "title": "Terraform Documentation",
                "url": "https://www.terraform.io/docs",
                "type": "documentation",
                "difficulty": "intermediate",
                "description": "Learn to provision infrastructure as code",
            },
        ],
        "Monitoring & Logging": [
            {
                "title": "Prometheus Documentation",
                "url": "https://prometheus.io/docs",
                "type": "documentation",
                "difficulty": "advanced",
                "description": "Learn monitoring with Prometheus",
            },
        ],
    }

    return render_template(
        "resources/explore.html",
        recommendations=recommendations,
    )
