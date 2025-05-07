from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from flask import current_app

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    email = db.Column(db.String(256), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    nome_completo = db.Column(db.String(256))
    xp_total = db.Column(db.Integer, default=0)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    simulados = db.relationship('Simulado', backref='usuario', lazy='dynamic')
    redacoes = db.relationship('Redacao', backref='usuario', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))