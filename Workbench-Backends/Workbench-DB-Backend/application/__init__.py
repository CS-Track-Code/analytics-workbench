from flask import Flask


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.ProdConfig')

    with app.app_context():
        # Include Routes
        from .save_blueprint import routes as save_routes
        from .evaluation_blueprint import routes as eval_routes

        # Register Blueprints
        app.register_blueprint(save_routes.save_bp)
        app.register_blueprint(eval_routes.evaluation_bp)

        return app
