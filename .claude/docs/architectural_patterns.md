# Architectural Patterns

## Application Factory Pattern
The application uses the Factory pattern for creating Flask and Celery instances.

**Key Files:**
- `devopscoach/app.py:34-55` - `create_app()` function
- `devopscoach/app.py:11-31` - `create_celery_app()` function

**Usage:**
```python
from devopscoach.app import create_app
app = create_app()
```

The factory enables:
- Multiple app instances (testing, production)
- Configuration injection via `settings_override` parameter
- Separation of app creation from extension registration

**Related Functions:**
- `devopscoach/app.py:58-69` - `extensions()` - Registers Flask extensions
- `devopscoach/app.py:72-86` - `middleware()` - Registers WSGI middleware

## Blueprint Pattern
Routes are organized into feature-based Blueprints.

**Key Files:**
- `devopscoach/page/views.py` - Main application routes
- `devopscoach/up/views.py` - Health check endpoints

**Blueprint Registration:**
```python
# devopscoach/app.py:50-51
app.register_blueprint(up)
app.register_blueprint(page)
```

Each Blueprint:
- Has its own `views.py` file
- Has its own `templates/` subdirectory
- Uses modern Flask decorators (`@blueprint.get()`)

## Environment-Driven Configuration
All configuration comes from environment variables with sensible defaults.

**Key File:**
- `config/settings.py`

**Pattern:**
```python
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = bool(strtobool(os.getenv("FLASK_DEBUG", "false")))
```

Database URI is constructed from individual env vars (`POSTGRES_USER`, `POSTGRES_HOST`, etc.) with fallbacks.

## Testing Patterns
Pytest fixtures provide efficient test isolation.

**Key File:**
- `test/conftest.py`

**Fixtures:**
- `app()` (session-scoped) - Creates test app with `_test` database suffix
- `client()` (function-scoped) - Test client for each test
- `db()` (session-scoped) - Creates/drops all tables once per session
- `session()` (function-scoped) - Uses nested transactions for rollback

The nested session pattern (`test/conftest.py:66-81`) enables fast tests without cleanup between tests.

## Docker Multi-Stage Builds
Production images use three-stage builds for optimization.

**Key File:**
- `Dockerfile`

**Stages:**
1. `assets` - Builds frontend assets using Node.js
2. `app-build` - Installs Python dependencies with uv
3. `app` - Production image with copied artifacts

This minimizes final image size and separates build concerns.

## Extension Initialization Pattern
Extensions are module-level objects initialized in `extensions.py`.

**Key File:**
- `devopscoach/extensions.py`

**Pattern:**
```python
debug_toolbar = DebugToolbarExtension()
db = SQLAlchemy()
flask_static_digest = FlaskStaticDigest()
```

Registered in `devopscoach/app.py:58-69` via the `extensions(app)` function.

## Task Runner Pattern
The `./run` script provides a unified interface for development commands.

**Key File:**
- `run`

**Key Functions:**
- `_dc()` / `_dc_run()` - Docker Compose helpers
- `flask()` - Run Flask commands
- `lint()` / `format()` - Code quality
- `test()` / `test:coverage()` - Testing
- `yarn:build:js()` / `yarn:build:css()` - Asset building

All commands execute within Docker containers for consistency.

## Celery Integration Pattern
Celery tasks wrap Flask context for database access.

**Key File:**
- `devopscoach/app.py:21-24`

**Pattern:**
```python
class FlaskTask(Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)
```

This ensures tasks have access to Flask extensions (database, etc.).