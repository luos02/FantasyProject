from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Registrar blueprints
    from app.views.auth_views import auth_bp
    from app.views.content_views import content_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)

    return app