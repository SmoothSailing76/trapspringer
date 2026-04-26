from pathlib import Path
from flask import Flask


def create_app() -> Flask:
    template_folder = str(Path(__file__).parent / "templates")
    app = Flask(__name__, template_folder=template_folder)
    app.secret_key = "trapspringer-local-dev-key"

    from trapspringer.adapters.api.routes import register_routes
    register_routes(app)

    return app
