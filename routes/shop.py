from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.shop import Produto, Resgate
from app.models.user import User
from app import db
from datetime import datetime
from flask import current_app

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

@shop_bp.route('/')
def index():
    # Obter parâmetros de filtragem e ordenação
    ordenar = request.args.get('ordenar', 'todos')
    
    # Consulta base
    query = Produto.query.filter_by(disponivel=True)
    
    # Aplicar ordenação
    if ordenar == 'menor_preco':
        query = query.order_by(Produto.preco_xp)
    elif ordenar == 'maior_preco':
        query = query.order_by(Produto.preco_xp.desc())
    
    # Executar consulta
    produtos = query.all()
    
    # Verificar XP do usuário atual
    xp_atual = current_user.xp_total if current_user.is_authenticated else 0
    
    return render_template('shop/index.html',
                          produtos=produtos,
                          xp_atual=xp_atual,
                          ordenar=ordenar)

@shop_bp.route('/produto/<int:produto_id>')
def produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    
    # Verificar XP do usuário atual
    xp_atual = current_user.xp_total if current_user.is_authenticated else 0
    pode_resgatar = xp_atual >= produto.preco_xp if current_user.is_authenticated else False
    
    return render_template('shop/produto.html',
                          produto=produto,
                          xp_atual=xp_atual,
                          pode_resgatar=pode_resgatar)

@shop_bp.route('/resgatar/<int:produto_id>', methods=['GET', 'POST'])
@login_required
def resgatar(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    
    # Verificar se usuário tem XP suficiente
    if current_user.xp_total < produto.preco_xp:
        flash('Você não tem XP suficiente para resgatar este produto.', 'danger')
        return redirect(url_for('shop.produto', produto_id=produto_id))
    
    # Verificar se produto está disponível e em estoque
    if not produto.disponivel or produto.estoque <= 0:
        flash('Este produto não está disponível no momento.', 'danger')
        return redirect(url_for('shop.produto', produto_id=produto_id))
    
    if request.method == 'POST':
        endereco_entrega = request.form.get('endereco')
        
        if not endereco_entrega:
            flash('Por favor, informe um endereço de entrega.', 'warning')
            return render_template('shop/resgatar.html', produto=produto)
        
        # Criar resgate
        resgate = Resgate(
            produto_id=produto_id,
            user_id=current_user.id,
            endereco_entrega=endereco_entrega,
            status='Pendente'
        )
        
        # Atualizar XP do usuário
        current_user.xp_total -= produto.preco_xp
        
        # Atualizar estoque do produto
        produto.estoque -= 1
        
        db.session.add(resgate)
        db.session.commit()
        
        flash('Produto resgatado com sucesso! Acompanhe o status na sua área de resgates.', 'success')
        return redirect(url_for('shop.meus_resgates'))
    
    return render_template('shop/resgatar.html', produto=produto)

@shop_bp.route('/meus-resgates')
@login_required
def meus_resgates():
    resgates = Resgate.query.filter_by(user_id=current_user.id).order_by(Resgate.data_resgate.desc()).all()
    
    return render_template('shop/meus_resgates.html', resgates=resgates)