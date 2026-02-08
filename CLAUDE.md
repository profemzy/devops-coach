# Project: WackOps-Coach

## Purpose
AI-powered DevOps career transition coach built with Flask and Docker.  
🌐 **Live at:** https://wackops.xyz  
Powered by [InfoTitans](https://infotitans.com/)

## Starting a New Project
Use the rename script to customize this template for your project:

```bash
./bin/rename-project <app_name> <ModuleName>
# Example: ./bin/rename-project blog Blog
```

The script will:
- Rename the `devopscoach/` directory to your app name
- Replace `devopscoach` / `DevOpsCoach` references throughout the codebase
- Prompt to reset the database (Docker volumes)
- Optionally initialize a new git repo

**Reference:** `bin/rename-project:1-105`

## Tech Stack
**Backend:** Python 3.14, Flask 3.1, SQLAlchemy 2.0, Celery 5.5
**Database:** PostgreSQL 18.1, Redis 8.2.3
**Frontend:** esbuild, TailwindCSS 4.x
**DevOps:** Docker multi-stage builds, Docker Compose v2, GitHub Actions CI
**Tooling:** uv (Python), yarn (Node.js), ruff (linting), pytest

## Project Structure
| Directory | Purpose |
|-----------|---------|
| `devopscoach/` | Flask application package (blueprints, views, templates) |
| `config/` | Application configuration (settings.py, gunicorn.py) |
| `db/` | Database migrations and seeds (Alembic) |
| `test/` | Pytest test suite |
| `assets/` | Frontend source files (JS, CSS) |
| `public/` | Built static assets (served by Flask) |
| `bin/` | Executable scripts (entrypoints, utilities) |
| `lib/` | Shared library code |

## Essential Commands

### First-time Setup
```bash
cp .env.example .env
docker compose up --build
./run flask db reset --with-testdb
```

### Development
```bash
./run test              # Run tests
./run lint              # Lint Python code
./run format            # Format Python code
./run shell             # Shell in web container
./run flask <command>   # Run Flask CLI commands
```

### Frontend Assets
```bash
./run yarn:build:js     # Build JavaScript
./run yarn:build:css    # Build CSS
```

### Database
```bash
./run psql              # Connect to PostgreSQL
./run redis-cli         # Connect to Redis
./run flask db upgrade  # Run migrations
```

## Key Files
- `devopscoach/app.py:34-55` - Application factory (`create_app()`)
- `devopscoach/app.py:11-31` - Celery factory (`create_celery_app()`)
- `config/settings.py` - Environment-based configuration
- `run` - Task runner script with all commands

## Additional Documentation
When working on specific areas, consult:
- `.claude/docs/architectural_patterns.md` - App factory, Blueprint pattern, testing patterns, Docker multi-stage builds

## CI/CD
GitHub Actions pipeline (`.github/workflows/ci.yml`) runs on PR/push to main.
