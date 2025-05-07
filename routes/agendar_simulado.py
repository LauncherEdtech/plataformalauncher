# app/routes/agendar_simulado.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.simulado import Simulado
from app import db
from datetime import datetime, timedelta
import random

agendar_simulado_bp = Blueprint('agendar_simulado', __name__, url_prefix='/agendar-simulado')

@agendar_simulado_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    Rota principal para agendamento de simulados.
    Permite ao usuário configurar e agendar um novo simulado.
    """
    if request.method == 'POST':
        # Extrair dados do formulário
        areas = request.form.getlist('areas')
        duracao = int(request.form.get('duracao', 120))
        num_questoes = int(request.form.get('num_questoes', 45))
        data_agendada_str = request.form.get('data_agendada')
        
        # Validações básicas
        if not areas:
            flash('Selecione pelo menos uma área de conhecimento', 'warning')
            return render_template('agendar_simulado/index.html')
        
        # Processar data de agendamento (opcional)
        data_agendada = None
        if data_agendada_str:
            try:
                data_agendada = datetime.strptime(data_agendada_str, '%Y-%m-%dT%H:%M')
                
                # Verificar se a data não é no passado
                if data_agendada < datetime.now():
                    flash('A data de agendamento não pode ser no passado', 'warning')
                    return render_template('agendar_simulado/index.html')
            except ValueError:
                flash('Formato de data inválido', 'danger')
                return render_template('agendar_simulado/index.html')
        
        # Construir título baseado nas áreas selecionadas
        areas_texto = ' e '.join(areas)
        titulo = f"Simulado Personalizado - {areas_texto}"
        
        # Criar o novo simulado
        simulado = Simulado(
            numero=get_next_simulado_number(current_user.id),
            titulo=titulo,
            areas=', '.join(areas),
            duracao_minutos=duracao,
            data_agendada=data_agendada,
            status='Pendente',
            user_id=current_user.id
        )
        
        db.session.add(simulado)
        db.session.commit()
        
        # Gerar questões para o simulado
        # Em um sistema real, você selecionaria questões do banco de dados
        # Para este exemplo, vamos criar questões aleatórias
        gerar_questoes_aleatorias(simulado.id, areas, num_questoes)
        
        flash('Simulado agendado com sucesso!', 'success')
        return redirect(url_for('simulados.index'))
    
    return render_template('agendar_simulado/index.html')

def get_next_simulado_number(user_id):
    """Obtém o próximo número de simulado para o usuário."""
    ultimo_simulado = Simulado.query.filter_by(user_id=user_id).order_by(Simulado.numero.desc()).first()
    if ultimo_simulado:
        return ultimo_simulado.numero + 1
    return 1

def gerar_questoes_aleatorias(simulado_id, areas, num_questoes):
    """
    Gera questões aleatórias para o simulado.
    Em um sistema real, você selecionaria questões de um banco de dados.
    """
    from app.models.simulado import Questao, Alternativa
    
    # Distribuir questões entre as áreas selecionadas
    questoes_por_area = num_questoes // len(areas)
    questoes_extras = num_questoes % len(areas)
    
    contador_questao = 1
    
    for area in areas:
        # Determinar quantas questões para esta área
        num_questoes_area = questoes_por_area
        if questoes_extras > 0:
            num_questoes_area += 1
            questoes_extras -= 1
        
        for i in range(num_questoes_area):
            # Dificuldade aleatória (entre 0.3 e 0.9)
            dificuldade = round(random.uniform(0.3, 0.9), 2)
            
            # Resposta correta aleatória
            resposta_correta = random.choice(['A', 'B', 'C', 'D', 'E'])
            
            # Criar questão
            questao = Questao(
                numero=contador_questao,
                texto=f"Questão {contador_questao} da área de {area}. Esta é uma questão de exemplo.",
                area=area,
                dificuldade=dificuldade,
                resposta_correta=resposta_correta,
                simulado_id=simulado_id
            )
            
            db.session.add(questao)
            db.session.flush()  # Para obter o ID da questão
            
            # Criar alternativas
            for letra in ['A', 'B', 'C', 'D', 'E']:
                texto_alternativa = f"Alternativa {letra} da questão {contador_questao}."
                if letra == resposta_correta:
                    texto_alternativa += " (Esta é a resposta correta)"
                
                alternativa = Alternativa(
                    letra=letra,
                    texto=texto_alternativa,
                    questao_id=questao.id
                )
                
                db.session.add(alternativa)
            
            contador_questao += 1
    
    db.session.commit()