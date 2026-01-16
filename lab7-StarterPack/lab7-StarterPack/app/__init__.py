from flask import Flask
from config import Config
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicjalizacja rozszerzeń
    db.init_app(app)
    migrate.init_app(app, db)

    # Rejestracja Blueprintów
    from .blueprints.ui import ui_bp
    from .blueprints.api.hosts import api_bp

    app.register_blueprint(ui_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        from .models import Host
        db.create_all()
    return app