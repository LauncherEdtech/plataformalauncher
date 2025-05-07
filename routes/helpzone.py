from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.helpzone import Duvida, Resposta, DuvidaVoto, RespostaVoto
from app.models.user import User
from app import db
from flask import current_app
from datetime import datetime

helpzone_bp = Blueprint('helpzone', __name__, url_prefix='/helpzone')

@helpzone_bp.route('/')
def index():
    # Obter parâmetros de filtragem e ordenação
    palavrachave = request.args.get('q', '')
    area = request.args.get('area', '')
    ordenar = request.args.get('ordenar', 'recentes')
    
    # Consulta base
    query = Duvida.query
    
    # Aplicar filtros
    if palavrachave:
        query = query.filter(Duvida.titulo.ilike(f'%{palavrachave}%') | 
                           Duvida.conteudo.ilike(f'%{palavrachave}%'))
    
    if area:
        query = query.filter(Duvida.area == area)
    
    # Aplicar ordenação
    if ordenar == 'recentes':
        query = query.order_by(Duvida.data_criacao.desc())
    elif ordenar == 'populares':
        # Esta é uma solução simples; em produção, seria mais eficiente
        # usando um subquery com contagem de votos ou um campo calculado
        duvidas = query.all()
        duvidas.sort(key=lambda d: d.total_votos(), reverse=True)
        
        # Obter top ajudantes da semana (simplificado)
        top_ajudantes = User.query.order_by(User.xp_total.desc()).limit(3).all()
        
        return render_template('helpzone/index.html',
                              duvidas=duvidas,
                              palavrachave=palavrachave,
                              area=area,
                              ordenar=ordenar,
                              areas_disponiveis=['matematica', 'portugues', 'quimica', 'fisica', 'biologia', 'historia', 'geografia', 'redacao'],
                              top_ajudantes=top_ajudantes)
    
    # Executar consulta
    duvidas = query.all()
    
    # Obter top ajudantes da semana (simplificado)
    top_ajudantes = User.query.order_by(User.xp_total.desc()).limit(3).all()
    
    return render_template('helpzone/index.html',
                          duvidas=duvidas,
                          palavrachave=palavrachave,
                          area=area,
                          ordenar=ordenar,
                          areas_disponiveis=['matematica', 'portugues', 'quimica', 'fisica', 'biologia', 'historia', 'geografia', 'redacao'],
                          top_ajudantes=top_ajudantes)

@helpzone_bp.route('/duvida/nova', methods=['GET', 'POST'])
@login_required
def nova_duvida():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        conteudo = request.form.get('conteudo')
        area = request.form.get('area')
        
        if not titulo or not conteudo or not area:
            flash('Preencha todos os campos obrigatórios', 'warning')
            return render_template('helpzone/nova_duvida.html')
        
        duvida = Duvida(
            titulo=titulo,
            conteudo=conteudo,
            area=area,
            user_id=current_user.id
        )
        
        db.session.add(duvida)
        db.session.commit()
        
        flash('Sua dúvida foi publicada com sucesso!', 'success')
        return redirect(url_for('helpzone.duvida', duvida_id=duvida.id))
    
    return render_template('helpzone/nova_duvida.html',
                          areas_disponiveis=['matematica', 'portugues', 'quimica', 'fisica', 'biologia', 'historia', 'geografia', 'redacao'])

@helpzone_bp.route('/duvida/<int:duvida_id>')
def duvida(duvida_id):
    duvida = Duvida.query.get_or_404(duvida_id)
    respostas = Resposta.query.filter_by(duvida_id=duvida_id).order_by(Resposta.solucao.desc(), Resposta.data_criacao).all()
    
    # Verificar se o usuário atual tem mesmo dúvida
    tem_mesma_duvida = False
    voto_duvida = None
    
    if current_user.is_authenticated:
        voto_duvida = DuvidaVoto.query.filter_by(duvida_id=duvida_id, user_id=current_user.id).first()
    
    # Obter informações de voto para cada resposta
    votos_respostas = {}
    if current_user.is_authenticated:
        for resposta in respostas:
            voto = RespostaVoto.query.filter_by(resposta_id=resposta.id, user_id=current_user.id).first()
            votos_respostas[resposta.id] = voto.valor if voto else 0
    
    return render_template('helpzone/duvida.html',
                          duvida=duvida,
                          respostas=respostas,
                          tem_mesma_duvida=tem_mesma_duvida,
                          voto_duvida=voto_duvida.valor if voto_duvida else 0,
                          votos_respostas=votos_respostas)

@helpzone_bp.route('/duvida/<int:duvida_id>/responder', methods=['POST'])
@login_required
def responder(duvida_id):
    duvida = Duvida.query.get_or_404(duvida_id)
    conteudo = request.form.get('conteudo')
    
    if not conteudo:
        flash('O conteúdo da resposta não pode estar vazio', 'warning')
        return redirect(url_for('helpzone.duvida', duvida_id=duvida_id))
    
    resposta = Resposta(
        conteudo=conteudo,
        duvida_id=duvida_id,
        user_id=current_user.id
    )
    
    db.session.add(resposta)
    
    # Adicionar XP ao usuário por responder
    current_user.xp_total += 10
    
    db.session.commit()
    
    flash('Sua resposta foi publicada com sucesso!', 'success')
    return redirect(url_for('helpzone.duvida', duvida_id=duvida_id))

@helpzone_bp.route('/duvida/<int:duvida_id>/mesma-duvida', methods=['POST'])
@login_required
def mesma_duvida(duvida_id):
    # Implementar lógica para marcar que o usuário tem a mesma dúvida
    # Isso pode ser implementado como um tipo especial de voto
    flash('Marcado como "Tenho a mesma dúvida"', 'success')
    return redirect(url_for('helpzone.duvida', duvida_id=duvida_id))

@helpzone_bp.route('/resposta/<int:resposta_id>/solucao', methods=['POST'])
@login_required
def marcar_solucao(resposta_id):
    resposta = Resposta.query.get_or_404(resposta_id)
    duvida = Duvida.query.get_or_404(resposta.duvida_id)
    
    # Verificar permissão (apenas o autor da dúvida pode marcar como solução)
    if duvida.user_id != current_user.id:
        flash('Você não tem permissão para realizar esta ação', 'danger')
        return redirect(url_for('helpzone.duvida', duvida_id=duvida.id))
    
    # Desmarcar todas as respostas como solução
    for r in duvida.respostas:
        r.solucao = False
    
    # Marcar esta resposta como solução
    resposta.solucao = True
    
    # Marcar a dúvida como resolvida
    duvida.resolvida = True
    
    # Adicionar XP ao autor da resposta
    resposta_autor = User.query.get(resposta.user_id)
    if resposta_autor:
        resposta_autor.xp_total += 50
    
    db.session.commit()
    
    flash('Resposta marcada como solução!', 'success')
    return redirect(url_for('helpzone.duvida', duvida_id=duvida.id))

@helpzone_bp.route('/duvida/<int:duvida_id>/voto', methods=['POST'])
@login_required
def votar_duvida(duvida_id):
    duvida = Duvida.query.get_or_404(duvida_id)
    valor = int(request.form.get('valor', 0))
    
    if valor not in [-1, 0, 1]:
        flash('Valor de voto inválido', 'danger')
        return redirect(url_for('helpzone.duvida', duvida_id=duvida_id))
    
    # Verificar se o usuário já votou nesta dúvida
    voto = DuvidaVoto.query.filter_by(duvida_id=duvida_id, user_id=current_user.id).first()
    
    if voto:
        if valor == 0:
            # Remover voto
            db.session.delete(voto)
        else:
            # Atualizar voto
            voto.valor = valor
    else:
        # Criar novo voto
        voto = DuvidaVoto(
            valor=valor,
            duvida_id=duvida_id,
            user_id=current_user.id
        )
        db.session.add(voto)
    
    db.session.commit()
    
    return redirect(url_for('helpzone.duvida', duvida_id=duvida_id))

@helpzone_bp.route('/resposta/<int:resposta_id>/voto', methods=['POST'])
@login_required
def votar_resposta(resposta_id):
    resposta = Resposta.query.get_or_404(resposta_id)
    valor = int(request.form.get('valor', 0))
    
    if valor not in [-1, 0, 1]:
        flash('Valor de voto inválido', 'danger')
        return redirect(url_for('helpzone.duvida', duvida_id=resposta.duvida_id))
    
    # Verificar se o usuário já votou nesta resposta
    voto = RespostaVoto.query.filter_by(resposta_id=resposta_id, user_id=current_user.id).first()
    
    if voto:
        if valor == 0:
            # Remover voto
            db.session.delete(voto)
        else:
            # Atualizar voto
            voto.valor = valor
    else:
        # Criar novo voto
        voto = RespostaVoto(
            valor=valor,
            resposta_id=resposta_id,
            user_id=current_user.id
        )
        db.session.add(voto)
    
    db.session.commit()
    
    return redirect(url_for('helpzone.duvida', duvida_id=resposta.duvida_id))