import importlib
import pkgutil

from flask import Blueprint, Flask
from flask_cors import CORS

from ...config import Settings

_EXCLUDED_TOP_LEVEL_PACKAGES = {"shared"}


def _blueprints_in(http_package_name: str) -> list[Blueprint]:
    try:
        http_package = importlib.import_module(http_package_name)
    except ModuleNotFoundError:
        return []

    blueprints: list[Blueprint] = []
    for module_info in pkgutil.iter_modules(http_package.__path__):
        if module_info.name == "app":
            continue
        module = importlib.import_module(f"{http_package_name}.{module_info.name}")
        blueprints.extend(value for value in vars(module).values() if isinstance(value, Blueprint))

    return blueprints


def _discover_blueprints() -> list[Blueprint]:
    assert __package__ is not None
    root_package_name = __package__.removesuffix(".interfaces.http")
    root_package = importlib.import_module(root_package_name)

    blueprints = _blueprints_in(f"{root_package_name}.interfaces.http")

    for module_info in pkgutil.iter_modules(root_package.__path__):
        if not module_info.ispkg or module_info.name in _EXCLUDED_TOP_LEVEL_PACKAGES:
            continue
        blueprints.extend(_blueprints_in(f"{root_package_name}.{module_info.name}.interfaces.http"))

    return blueprints


def create_app() -> Flask:
    app = Flask(__name__)
    settings = Settings.from_env()
    app.config["SETTINGS"] = settings
    app.debug = settings.debug

    CORS(app, origins=settings.cors_origins)

    for blueprint in _discover_blueprints():
        app.register_blueprint(blueprint)

    return app
