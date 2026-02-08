# WackOps-Coach

An AI-powered Flask application designed to help professionals transition into DevOps careers.  
🌐 **Live at:** https://wackops.xyz  
Powered by [InfoTitans](https://infotitans.com/)

## Features

- **Skills Assessment** - Analyze your current skills against DevOps requirements
- **Custom Roadmaps** - Get personalized learning paths based on your background
- **Learning Resources** - Discover curated tutorials, courses, and certifications
- **Portfolio Projects** - Build hands-on projects to showcase your skills
- **Interview Prep** - Practice DevOps-specific interview questions and scenarios
- **Job Search** - Track and analyze DevOps job opportunities

## Tech Stack

### Backend
- **Python 3.14** + **Flask 3.1** - Web framework
- **PostgreSQL 18** - Primary database
- **Redis 8** - Cache and message broker
- **Celery 5.5** - Background task processing
- **SQLAlchemy 2.0** - ORM
- **Flask-Login** - User authentication
- **OpenAI API** - AI-powered features (compatible endpoints)
- **Tavily API** - Web search for up-to-date DevOps trends

### Frontend
- **esbuild** - JavaScript bundler
- **TailwindCSS 4.x** - CSS framework
- **Jinja2** - Template engine with glassmorphism UI

### DevOps
- **Docker** - Containerization with multi-stage builds
- **Docker Compose v2** - Container orchestration
- **GitHub Actions** - CI/CD pipeline

## Quick Start

### Prerequisites
- Docker installed
- Docker Compose v2 (2.20.2+)

### Installation

```bash
# Clone the repository
git clone <your-repo-url> devopscoach
cd devopscoach

# Copy environment file
cp .env.example .env

# Build and start services
docker compose up --build

# In a second terminal, setup the database
./run flask db reset --with-testdb
```

### Access the Application

Visit **http://localhost:8000** in your browser.

### Default Credentials

Register a new account through the web interface.

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Application
SECRET_KEY=your_secret_key_here
FLASK_DEBUG=true

# Database
POSTGRES_USER=devopscoach
POSTGRES_PASSWORD=password
DATABASE_URL=postgresql+psycopg://devopscoach:password@postgres:5432/devopscoach

# Redis
REDIS_URL=redis://redis:6379/0

# OpenAI Compatible API (required for AI features)
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://profemzy-5149-resource.openai.azure.com/openai/v1/
OPENAI_MODEL=gpt-5.2

# Tavily Web Search API (for up-to-date DevOps trends)
TAVILY_API_KEY=your_tavily_api_key_here

# Email (optional, for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

## Development

### Running Commands

Use the `./run` script for common development tasks:

```bash
./run test              # Run tests
./run lint              # Lint Python code
./run format            # Format Python code
./run shell             # Shell in web container
./run flask <command>   # Run Flask commands
```

### Database Management

```bash
./run flask db reset --with-testdb  # Reset database
./run psql                          # Connect to PostgreSQL
./run flask db upgrade              # Run migrations
```

### Code Quality

```bash
./run quality            # Run linting and formatting
./run test:coverage      # Run tests with coverage
```

## Project Structure

```
devopscoach/
├── app.py              # Application factory
├── extensions.py       # Flask extensions
├── models.py           # Database models
├── auth/               # Authentication blueprint
├── dashboard/          # Main dashboard
├── skills/             # Skills assessment ✅
│   ├── views.py        # Assessment & results pages
│   ├── forms.py        # Assessment form
│   └── templates/      # Assessment UI
├── services/           # Business logic services
│   ├── ai_service.py   # AI analysis with web search
│   └── web_search_service.py  # Tavily integration
├── roadmap/            # Learning roadmaps (coming soon)
├── resources/          # Learning resources (coming soon)
├── projects/           # Portfolio projects (coming soon)
├── interview/          # Interview prep (coming soon)
├── job_search/         # Job search (coming soon)
└── templates/          # Jinja2 templates
```

## Current Status

**Completed (Phase 1):**
- ✅ User authentication (login, register, logout)
- ✅ Dashboard with assessment count tracking
- ✅ Database models for all features
- ✅ Responsive glassmorphism UI design

**Completed (Phase 2):**
- ✅ Skills Assessment form with 12 input fields
- ✅ AI-powered skill analysis using OpenAI-compatible API
- ✅ Web search integration (Tavily) for up-to-date DevOps trends
- ✅ Personalized recommendations (roles, skills, roadmap, certifications, projects)
- ✅ Assessment history tracking
- ✅ 24 passing tests

**Planned:**
- ⏳ Custom Roadmaps (Phase 3)
- ⏳ Learning Resources (Phase 4)
- ⏳ Portfolio Projects (Phase 5)
- ⏳ Interview Prep (Phase 6)
- ⏳ Job Search (Phase 7)

## Roadmap

1. **Phase 1: Foundation** ✅ - Authentication, dashboard, core infrastructure
2. **Phase 2: Skills Assessment** ✅ - AI-powered skill gap analysis with web search
3. **Phase 3: Learning Roadmaps** - Personalized learning paths with progress tracking
4. **Phase 4: Resources** - Curated tutorials, courses, and certifications
5. **Phase 5: Projects** - Hands-on portfolio projects with templates
6. **Phase 6: Interview Prep** - Practice questions and mock scenarios
7. **Phase 7: Job Search** - Job tracking and market analysis
8. **Phase 8: Polish** - Performance, optimizations, and final touches

## License

MIT License - See LICENSE file for details
