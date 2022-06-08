from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_redis import FlaskRedis

import config


# Globally accessible libraries
# db = SQLAlchemy()
# r = FlaskRedis()


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.ProdConfig')

    with app.app_context():
        # Include Routes
        from .home_blueprint import routes as home
        from .project_analysis import routes as project_analysis
        from .error_blueprint import routes as error_routes
        from .explanation_blueprint import routes as explanation_routes
        # Register Blueprints
        app.register_blueprint(home.home_bp)
        app.register_blueprint(project_analysis.project_analysis_bp)
        app.register_blueprint(error_routes.error_bp)
        app.register_blueprint(explanation_routes.explanation_bp)

        return app
