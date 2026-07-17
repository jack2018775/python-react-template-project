import importlib
import pkgutil

from flask import Blueprint, Flask

from ...config import Settings


def _discover_blueprints() -> list[Blueprint]:
    assert __package__ is not None
    package = importlib.import_module(__package__)
    blueprints: list[Blueprint] = []

    for module_info in pkgutil.iter_modules(package.__path__):
        if module_info.name == "app":
            continue
        module = importlib.import_module(f"{__package__}.{module_info.name}")
        blueprints.extend(value for value in vars(module).values() if isinstance(value, Blueprint))

    return blueprints


def create_app() -> Flask:
    app = Flask(__name__)
    settings = Settings.from_env()
    app.config["SETTINGS"] = settings
    app.debug = settings.debug

    for blueprint in _discover_blueprints():
        app.register_blueprint(blueprint)

    return app
