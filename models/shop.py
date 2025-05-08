from datetime import datetime
from app import db
from flask import current_app

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    imagem = db.Column(db.String(255))
    preco_xp = db.Column(db.Integer, nullable=False)
    estoque = db.Column(db.Integer, default=100)
    disponivel = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    resgates = db.relationship('Resgate', backref='produto', lazy='dynamic')
    
    def __repr__(self):
        return f'<Produto {self.id}: {self.nome}>'

class Resgate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_resgate = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pendente')  # Pendente, Enviado, Entregue
    endereco_entrega = db.Column(db.Text)
    
    # Chaves estrangeiras
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Resgate {self.id} - Produto {self.produto_id} por Usuário {self.user_id}>'