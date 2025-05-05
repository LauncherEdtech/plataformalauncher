from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.simulado import Simulado
from app.models.user import User
from app import db
from datetime import datetime, timedelta
from flask import current_app


progresso_bp = Blueprint('progresso', __name__, url_prefix='/progresso')

@progresso_bp.route('/')
@login_required
def index():
    # Calcular total de XP acumulado
    xp_total = current_user.xp_total
    
    # Obter histórico de simulados
    simulados = Simulado.query.filter_by(
        user_id=current_user.id,
        status='Concluído'
    ).order_by(Simulado.data_realizado.desc()).all()
    
    # Calcular progresso por área
    areas = ['Linguagens', 'Humanas', 'Natureza', 'Matemática']
    progresso_areas = {}
    
    # Simplificado - em um sistema real, você calcularia isso com base em dados reais
    for area in areas:
        progresso_areas[area] = {
            'total_exercicios': 100,
            'exercicios_feitos': 65,
            'percentual': 65
        }
    
    # Obter estatísticas de tempo de estudo
    # Simplificado - em um sistema real, você rastrearia o tempo de estudo
    estatisticas_tempo = {
        'hoje': 120,  # em minutos
        'semana': 720,  # em minutos
        'mes': 3000   # em minutos
    }
    
    # Obter dados de evolução para gráficos
    # Simplificado - em um sistema real, você teria dados históricos reais
    data_atual = datetime.now()
    datas = [(data_atual - timedelta(days=i)).strftime('%d/%m') for i in range(7)]
    datas.reverse()
    
    progresso_semanal = {
        'datas': datas,
        'valores': [30, 45, 60, 40, 75, 50, 65]  # pontos por dia
    }
    
    return render_template('progresso/index.html',
                          xp_total=xp_total,
                          simulados=simulados,
                          progresso_areas=progresso_areas,
                          estatisticas_tempo=estatisticas_tempo,
                          progresso_semanal=progresso_semanal)