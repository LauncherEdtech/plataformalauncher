from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.dashboard import Estatistica
from app.models.simulado import Simulado
from app.models.redacao import Redacao
from flask import current_app

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    # Obtém estatísticas do usuário
    estatisticas = Estatistica.get_or_create(current_user.id)
    
    # Obtém simulados pendentes
    simulados_pendentes = Simulado.query.filter_by(
        user_id=current_user.id, 
        status='Pendente'
    ).limit(2).all()
    
    # Obtém redações recentes
    redacoes = Redacao.query.filter_by(
        user_id=current_user.id
    ).order_by(Redacao.data_envio.desc()).limit(1).all()
    
    return render_template('dashboard.html', 
                           estatisticas=estatisticas,
                           simulados_pendentes=simulados_pendentes,
                           redacoes=redacoes)