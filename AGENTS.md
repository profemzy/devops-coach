# Agent Guidelines for DevOps Coach

This document provides essential information for AI coding agents working on the DevOps Coach Flask application.

## Build, Lint, and Test Commands

### Running Tests
```bash
./run test                                          # Run all tests
./run test test/devopscoach/skills/test_views.py   # Single test file
./run test test/devopscoach/skills/test_views.py::TestSkillsAssessment  # Specific test class
./run test test/devopscoach/skills/test_views.py::TestSkillsAssessment::test_assessment_page_renders  # Single test
./run test:coverage                                 # With coverage report
./run test -m "not slow"                            # With markers
```

### Code Quality
```bash
./run lint              # Lint Python (Ruff)
./run format            # Format Python (Ruff)
./run quality           # Lint + format all (Python, Dockerfile, shell)
./run lint:dockerfile   # Lint Dockerfile (Hadolint)
./run lint:shell        # Lint shell scripts (ShellCheck)
./run format:shell      # Format shell scripts (shfmt)
```

### Development
```bash
./run shell                      # Shell in web container
./run flask db upgrade           # Run migrations
./run flask db reset --with-testdb  # Reset database
./run psql                       # PostgreSQL shell
./run redis-cli                  # Redis shell
./run yarn:build:js              # Build JavaScript
./run yarn:build:css             # Build CSS
```

## Code Style Guidelines

### Python Version & Tools
- **Python:** 3.14+
- **Linter/Formatter:** Ruff (replaces Black, flake8, isort)
- **Line Length:** 79 characters
- **Package Manager:** uv (not pip)

### Import Organization
Follow this order (Ruff's `I` rule enforces this):

```python
# 1. Standard library imports
from datetime import datetime

# 2. Third-party imports
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

# 3. Local application imports
from devopscoach.auth import auth
from devopscoach.extensions import db
from devopscoach.models import User
from devopscoach.services.ai_service import get_ai_service
```

**Rules:**
- Alphabetize imports within each group
- Use absolute imports for application code: `from devopscoach.module import Item`
- Multi-line imports use parentheses (not backslash)
- Avoid star imports (`from module import *`)

### Naming Conventions

**Files & Directories:**
- Modules: `snake_case.py` (e.g., `ai_service.py`, `web_search_service.py`)
- Blueprints: `snake_case/` (e.g., `skills/`, `dashboard/`)

**Python Code:**
- Classes: `PascalCase` (e.g., `User`, `SkillAssessment`, `AIService`)
- Functions/Methods: `snake_case` (e.g., `analyze_skills()`, `get_ai_service()`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `OPENAI_API_KEY`, `REDIS_URL`)
- Private methods: `_leading_underscore()` (e.g., `_get_fallback_analysis()`)
- Blueprint variables: `snake_case` (e.g., `auth`, `skills`, `dashboard`)

**Database:**
- Tables: `snake_case` plural (e.g., `users`, `skill_assessments`)
- Columns: `snake_case` (e.g., `user_id`, `assessment_date`)

### String Formatting
- Prefer **f-strings** for formatting: `f"User {user.id}"`
- Use double quotes `"` for strings (Ruff default)
- Multi-line strings: Use triple double-quotes `"""`

### Error Handling
```python
# Try-except with fallback
try:
    result = api_call()
    return result
except Exception as e:
    return self._get_fallback_analysis(skills_data, str(e))

# Flash messages: "success", "danger", "warning", "info"
flash("Registration successful! Please log in.", "success")

# Database operations
user = User(username="test")
db.session.add(user)
db.session.commit()

# Query patterns
user = User.query.filter_by(username=username).first()
assessment = SkillAssessment.query.filter_by(user_id=current_user.id).first_or_404()
```

## Flask Patterns

### Blueprint Structure
```python
# __init__.py
from flask import Blueprint

auth = Blueprint("auth", __name__, template_folder="templates")

from devopscoach.auth import views  # noqa: E402,F401
```

### Route Decorators
```python
@skills.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    """Skills assessment form."""
    # Implementation
```

### Form Handling
```python
form = LoginForm()
if form.validate_on_submit():
    # Process form
    flash("Success!", "success")
    return redirect(url_for("dashboard.index"))
return render_template("auth/login.html", form=form)
```

## Testing Patterns

### Test File Structure
- Location: `test/devopscoach/<blueprint>/test_<module>.py`
- Inherit from `ViewTestMixin` for view tests
- Use descriptive test names with `test_` prefix

```python
from devopscoach.models import User
from lib.test import ViewTestMixin

class TestSkillsAssessment(ViewTestMixin):
    """Tests for skills assessment view."""

    def test_assessment_requires_login(self):
        """Assessment page should redirect to login if not authenticated."""
        response = self.client.get(url_for("skills.assessment"))
        assert response.status_code == 302
```

### Fixtures
- Use `session` fixture for database operations
- Use `client` fixture for HTTP requests
- Use `monkeypatch` for environment variables
- Create unique test data using `uuid.uuid4()`
- Clean up is automatic via session rollback

## Common Patterns

### Services (Singleton Pattern)
```python
_ai_service = None

def get_ai_service() -> AIService:
    """Get or create the AI service singleton."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
```

### JSON Columns & Environment
```python
# Models use SQLAlchemy's JSON type
assessment_data = db.Column(JSON)  # User's form responses

# Access environment variables via config.settings
from config import settings
api_key = settings.OPENAI_API_KEY
```

## Security Reminders
- Never commit sensitive files (see `.security-checklist.md`)
- Use `bcrypt` for password hashing
- Enable CSRF protection (Flask-WTF handles this)
- Use `@login_required` for protected routes
- Validate all user inputs with WTForms validators

## Project-Specific Notes
- **Application Factory:** `create_app()` in `devopscoach/app.py:49-82`
- **Celery Factory:** `create_celery_app()` in `devopscoach/app.py:26-46`
- **Extensions:** Initialized in `devopscoach/extensions.py`
- **Models:** All in single file `devopscoach/models.py`
- **Migrations:** Use `./run flask db` commands, stored in `db/versions/`

## Getting Help
- **Documentation:** See `README.md`, `k8s/README.md`, `.security-checklist.md`
- **Architecture:** See `.claude/docs/architectural_patterns.md`
- **CI/CD:** See `.github/workflows/ci.yml`
