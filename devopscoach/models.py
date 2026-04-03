from flask_login import UserMixin
from sqlalchemy import JSON, Boolean, DateTime, Integer, String

from devopscoach.extensions import bcrypt, db
from devopscoach.utils.datetime import utc_now


class User(UserMixin, db.Model):
    """User model for authentication and profile data."""

    __tablename__ = "users"

    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(80), unique=True, nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(255), nullable=False)
    first_name = db.Column(String(80))
    last_name = db.Column(String(80))
    created_at = db.Column(DateTime, default=utc_now)
    updated_at = db.Column(DateTime, default=utc_now, onupdate=utc_now)
    is_active = db.Column(Boolean, default=True)

    # Relationships
    skills = db.relationship(
        "SkillAssessment",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    roadmaps = db.relationship(
        "CustomRoadmap",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    resources = db.relationship(
        "LearningResource",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    projects = db.relationship(
        "PortfolioProject",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    interviews = db.relationship(
        "InterviewPrep",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    job_searches = db.relationship(
        "JobSearch", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode(
            "utf-8"
        )

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class SkillAssessment(db.Model):
    """Model for storing user skill assessments."""

    __tablename__ = "skill_assessments"

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)

    # Assessment type for categorization
    skill_name = db.Column(
        String(100), default="DevOps Transition"
    )  # For backward compatibility
    skill_level = db.Column(
        String(20), default="Pending"
    )  # For backward compatibility

    # Dates
    assessment_date = db.Column(DateTime, default=utc_now, nullable=False)
    notes = db.Column(String(500))

    # JSON fields for storing structured data
    assessment_data = db.Column(JSON)  # User's form responses
    recommendations = db.Column(JSON)  # AI-generated recommendations

    def __repr__(self):
        return f"<SkillAssessment {self.id} - User {self.user_id}>"


class CustomRoadmap(db.Model):
    """Model for storing personalized learning roadmaps."""

    __tablename__ = "custom_roadmaps"

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(String(200), nullable=False)
    description = db.Column(String(1000))
    created_at = db.Column(DateTime, default=utc_now)
    updated_at = db.Column(DateTime, default=utc_now, onupdate=utc_now)

    # JSON field for storing roadmap structure
    roadmap_data = db.Column(JSON)

    def __repr__(self):
        return f"<CustomRoadmap {self.title}>"


class LearningResource(db.Model):
    """Model for storing learning resources."""

    __tablename__ = "learning_resources"

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(String(200), nullable=False)
    description = db.Column(String(1000))
    resource_type = db.Column(
        String(50), nullable=False
    )  # Course, Book, Video, Article
    url = db.Column(String(500))
    difficulty = db.Column(String(20))  # Beginner, Intermediate, Advanced
    estimated_hours = db.Column(Integer)
    is_completed = db.Column(Boolean, default=False)
    completion_date = db.Column(DateTime)
    created_at = db.Column(DateTime, default=utc_now)

    # Tags/categories stored as JSON
    tags = db.Column(JSON)

    def __repr__(self):
        return f"<LearningResource {self.title}>"


class PortfolioProject(db.Model):
    """Model for storing portfolio projects."""

    __tablename__ = "portfolio_projects"

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(String(200), nullable=False)
    description = db.Column(String(2000))
    technologies = db.Column(JSON)  # List of technologies used
    github_url = db.Column(String(500))
    live_url = db.Column(String(500))
    start_date = db.Column(DateTime)
    end_date = db.Column(DateTime)
    status = db.Column(String(20), default="In Progress")
    created_at = db.Column(DateTime, default=utc_now)

    # Project data stored as JSON
    images = db.Column(JSON)
    features = db.Column(JSON)

    def __repr__(self):
        return f"<PortfolioProject {self.title}>"


class InterviewPrep(db.Model):
    """Model for storing interview preparation data."""

    __tablename__ = "interview_prep"

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    company_name = db.Column(String(200), nullable=False)
    position = db.Column(String(100), nullable=False)
    interview_date = db.Column(DateTime)
    interview_type = db.Column(String(50))  # Phone, Technical, Behavioral
    status = db.Column(String(20), default="Scheduled")
    created_at = db.Column(DateTime, default=utc_now)

    # JSON fields for storing structured data
    questions_practiced = db.Column(JSON)
    notes = db.Column(JSON)
    feedback = db.Column(JSON)
    prep_resources = db.Column(JSON)

    def __repr__(self):
        return f"<InterviewPrep {self.company_name} - {self.position}>"


class JobSearch(db.Model):
    """Model for storing job search tracking."""

    __tablename__ = "job_search"

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    company_name = db.Column(String(200), nullable=False)
    position = db.Column(String(100), nullable=False)
    location = db.Column(String(100))
    url = db.Column(String(500))
    application_date = db.Column(DateTime)
    status = db.Column(String(50), default="Applied")
    notes = db.Column(String(2000))
    created_at = db.Column(DateTime, default=utc_now)
    updated_at = db.Column(DateTime, default=utc_now, onupdate=utc_now)

    # Application tracking
    contact_person = db.Column(String(200))
    salary_range = db.Column(String(100))
    follow_up_date = db.Column(DateTime)

    def __repr__(self):
        return f"<JobSearch {self.company_name} - {self.position}>"
