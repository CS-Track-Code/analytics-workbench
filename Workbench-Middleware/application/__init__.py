from flask import Flask


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.ProdConfig')

    with app.app_context():
        # Include Routes
        from .mercury_blueprint import routes as mercury_routes
        from .esa_blueprint import routes as esa_routes
        from .ner_blueprint import routes as ner_routes
        from .db_blueprint import routes as db_routes
        from .external_access_blueprint import routes as ext_routes

        # Register Blueprints
        app.register_blueprint(mercury_routes.mercury_bp)
        app.register_blueprint(esa_routes.esa_bp)
        app.register_blueprint(ner_routes.ner_bp)
        app.register_blueprint(db_routes.db_bp)
        app.register_blueprint(ext_routes.ex_ac_bp)

        return app
