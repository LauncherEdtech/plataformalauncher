from datetime import datetime
from app import db
from flask import current_app

class Redacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200))
    conteudo = db.Column(db.Text)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    nota = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    
    # Chave estrangeira
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Redacao {self.id}: {self.titulo}>'