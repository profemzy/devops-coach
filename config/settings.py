import os

from distutils.util import strtobool

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = bool(strtobool(os.getenv("FLASK_DEBUG", "false")))

SERVER_NAME = os.getenv(
    "SERVER_NAME", "localhost:{0}".format(os.getenv("PORT", "8000"))
)
# SQLAlchemy.
pg_user = os.getenv("POSTGRES_USER", "devopscoach")
pg_pass = os.getenv("POSTGRES_PASSWORD", "password")
pg_host = os.getenv("POSTGRES_HOST", "postgres")
pg_port = os.getenv("POSTGRES_PORT", "5432")
pg_db = os.getenv("POSTGRES_DB", pg_user)
db = f"postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", db)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Redis.
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Celery.
CELERY_CONFIG = {
    "broker_url": REDIS_URL,
    "result_backend": REDIS_URL,
    "include": ["devopscoach.tasks.ai_tasks"],
    "task_routes": {
        "devopscoach.tasks.ai_tasks.*": {"queue": "celery"},
        "devopscoach.tasks.job_scraping.*": {"queue": "job_scraping"},
        "devopscoach.tasks.email_tasks.*": {"queue": "email_tasks"},
    },
}

# OpenAI Compatible API.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv(
    "OPENAI_API_BASE",
    "https://profemzy-5149-resource.openai.azure.com/openai/v1/",
)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")

# Email.
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USE_TLS = strtobool(os.getenv("MAIL_USE_TLS", "true"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

# Tavily Web Search API.
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
