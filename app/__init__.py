from flask import Flask, redirect, url_for
from app.extensions import db, login_manager, mail, migrate
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        db.create_all()
    
    # Import all blueprints
    from app.auth import auth_bp
    from app.reports import reports_bp
    from app.admin import admin_bp
    from app.officers import officers_bp
    from app.assessments import assessments_bp
    from app.quarterly import quarterly_bp
    
    # Register all blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(officers_bp, url_prefix='/officers')
    app.register_blueprint(assessments_bp, url_prefix='/assessments')
    app.register_blueprint(quarterly_bp)  # No prefix needed, uses /quarterly
    
    # Context processor to inject background logo settings into all templates
    @app.context_processor
    def inject_background_logo():
        """Inject background logo settings into all templates"""
        try:
            from app.models.system_settings import SystemSetting
            logo_url_setting = SystemSetting.query.filter_by(key='background_logo_url').first()
            logo_opacity_setting = SystemSetting.query.filter_by(key='background_logo_opacity').first()
            
            return {
                'background_logo_url': logo_url_setting.value if logo_url_setting else '',
                'background_logo_opacity': float(logo_opacity_setting.value) if logo_opacity_setting else 0.1
            }
        except Exception as e:
            # If table doesn't exist yet or any other error, return defaults
            return {
                'background_logo_url': '',
                'background_logo_opacity': 0.1
            }
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app