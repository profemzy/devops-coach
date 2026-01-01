from datetime import datetime

from celery import Celery, Task
from flask import Flask
from werkzeug.debug import DebuggedApplication
from werkzeug.middleware.proxy_fix import ProxyFix

from devopscoach.auth import auth
from devopscoach.dashboard.views import dashboard
from devopscoach.extensions import (
    bcrypt,
    db,
    debug_toolbar,
    flask_static_digest,
    login_manager,
    mail,
    migrate,
)
from devopscoach.page.views import page
from devopscoach.roadmap import roadmap
from devopscoach.skills import skills
from devopscoach.up.views import up


def create_celery_app(app=None):
    """
    Create a new Celery app and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(app.import_name, task_cls=FlaskTask)
    celery.conf.update(app.config.get("CELERY_CONFIG", {}))
    celery.set_default()
    app.extensions["celery"] = celery

    return celery


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, static_folder="../public", static_url_path="")

    app.config.from_object("config.settings")

    if settings_override:
        app.config.update(settings_override)

    middleware(app)

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(dashboard)
    app.register_blueprint(up)
    app.register_blueprint(page)
    app.register_blueprint(skills, url_prefix="/skills")
    app.register_blueprint(roadmap)

    extensions(app)

    # Template context processors
    @app.context_processor
    def utility_context():
        return {
            "current_year": datetime.now().year,
        }

    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    bcrypt.init_app(app)
    debug_toolbar.init_app(app)
    db.init_app(app)
    flask_static_digest.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Flask-Login user loader
    from devopscoach.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    return None


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Enable the Flask interactive debugger in the brower for development.
    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    # Set the real IP address into request.remote_addr when behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


celery_app = create_celery_app()
