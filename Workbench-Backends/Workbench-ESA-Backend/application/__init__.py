from flask import Flask


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.ProdConfig')

    with app.app_context():
        # Include Routes
        from .esa_blueprint import routes as esa_routes

        # Register Blueprints
        app.register_blueprint(esa_routes.esa_bp)

        return app
