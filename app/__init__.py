from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    db_path = os.environ.get('DATABASE_PATH', '/data/solar_tracker.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'solar-tracker-dev-key-change-in-prod')

    db.init_app(app)

    from app.routes.dashboard import dashboard_bp
    from app.routes.expenses import expenses_bp
    from app.routes.consumption import consumption_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    app.register_blueprint(consumption_bp, url_prefix='/consumption')
    app.register_blueprint(settings_bp, url_prefix='/settings')

    with app.app_context():
        db.create_all()
        _seed_default_settings()

    return app


def _seed_default_settings():
    from app.models import SystemSettings
    if not SystemSettings.query.first():
        settings = SystemSettings(
            system_size_kw=0.0,
            panel_count=0,
            inverter_brand='',
            expected_annual_production_kwh=0.0,
            electricity_rate=0.25,
            currency='USD',
        )
        db.session.add(settings)
        db.session.commit()
