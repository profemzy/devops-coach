from flask import Blueprint, render_template
from flask_login import current_user, login_required

from devopscoach.models import SkillAssessment

dashboard = Blueprint("dashboard", __name__, template_folder="templates")


@dashboard.route("/")
@login_required
def index():
    """Main dashboard page."""
    # Count user's skills assessments
    assessment_count = SkillAssessment.query.filter_by(
        user_id=current_user.id
    ).count()

    return render_template(
        "dashboard/index.html", assessment_count=assessment_count
    )
