from datetime import datetime
from app import db
from flask import current_app

class Duvida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    resolvida = db.Column(db.Boolean, default=False)
    area = db.Column(db.String(50))  # Ex: #quimica, #redacao, #matematica
    
    # Chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relacionamentos
    respostas = db.relationship('Resposta', backref='duvida', lazy='dynamic')
    votos = db.relationship('DuvidaVoto', backref='duvida', lazy='dynamic')
    
    def __repr__(self):
        return f'<Dúvida {self.id}: {self.titulo}>'
    
    def total_votos(self):
        return sum([voto.valor for voto in self.votos])
    
class Resposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    solucao = db.Column(db.Boolean, default=False)  # Marca se é a resposta aceita
    
    # Chaves estrangeiras
    duvida_id = db.Column(db.Integer, db.ForeignKey('duvida.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relacionamentos
    votos = db.relationship('RespostaVoto', backref='resposta', lazy='dynamic')
    
    def __repr__(self):
        return f'<Resposta {self.id} para Dúvida {self.duvida_id}>'
    
    def total_votos(self):
        return sum([voto.valor for voto in self.votos])

class DuvidaVoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Integer, default=0)  # 1 = upvote, -1 = downvote
    
    # Chaves estrangeiras
    duvida_id = db.Column(db.Integer, db.ForeignKey('duvida.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    __table_args__ = (
        db.UniqueConstraint('duvida_id', 'user_id', name='unique_duvida_vote'),
    )

class RespostaVoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Integer, default=0)  # 1 = upvote, -1 = downvote
    
    # Chaves estrangeiras
    resposta_id = db.Column(db.Integer, db.ForeignKey('resposta.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    __table_args__ = (
        db.UniqueConstraint('resposta_id', 'user_id', name='unique_resposta_vote'),
    )