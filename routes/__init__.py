#app/routes/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    
    # Configurações do app
    app.config['SECRET_KEY'] = 'sua-chave-secreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1469@localhost:5432/launcher_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicialização de extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Importar blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.simulados import simulados_bp
    from app.routes.helpzone import helpzone_bp
    from app.routes.shop import shop_bp
    from app.routes.progresso import progresso_bp
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(simulados_bp)
    app.register_blueprint(helpzone_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(progresso_bp)
    
    return app