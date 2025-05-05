from app import db
from flask import current_app

class Questao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer)
    texto = db.Column(db.Text)
    area = db.Column(db.String(50))  # Linguagens, Matemática, etc.
    dificuldade = db.Column(db.Float)  # Para cálculo TRI
    resposta_correta = db.Column(db.String(1))  # A, B, C, D ou E
    resposta_usuario = db.Column(db.String(1), nullable=True)
    
    # Chave estrangeira
    simulado_id = db.Column(db.Integer, db.ForeignKey('simulado.id'))
    
    # Relacionamentos
    alternativas = db.relationship('Alternativa', backref='questao', lazy='dynamic')
    
    def __repr__(self):
        return f'<Questao {self.id}>'
    
    def verificar_resposta(self):
        return self.resposta_usuario == self.resposta_correta

class Alternativa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    letra = db.Column(db.String(1))  # A, B, C, D ou E
    texto = db.Column(db.Text)
    
    # Chave estrangeira
    questao_id = db.Column(db.Integer, db.ForeignKey('questao.id'))
    
    def __repr__(self):
        return f'<Alternativa {self.letra}>'