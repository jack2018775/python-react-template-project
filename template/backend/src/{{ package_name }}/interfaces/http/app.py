from flask import Flask

from ...config import Settings
from .health import health_bp


def create_app() -> Flask:
    app = Flask(__name__)
    settings = Settings.from_env()
    app.config["SETTINGS"] = settings
    app.debug = settings.debug

    app.register_blueprint(health_bp)

    return app
