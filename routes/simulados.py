from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models.simulado import Simulado, Questao, Alternativa
from app.models.user import User
from app import db
from datetime import datetime, timedelta
from flask import current_app
import json

simulados_bp = Blueprint('simulados', __name__, url_prefix='/simulados')

@simulados_bp.route('/')
@login_required
def index():
    # Obter simulados pendentes
    simulados_pendentes = Simulado.query.filter_by(
        user_id=current_user.id,
        status='Pendente'
    ).all()
    
    # Obter simulados concluídos
    simulados_concluidos = Simulado.query.filter_by(
        user_id=current_user.id,
        status='Concluído'
    ).order_by(Simulado.data_realizado.desc()).all()
    
    # Obter estatísticas TRI (simulado para o gráfico)
    tri_ultimos_simulados = Simulado.query.filter_by(
        user_id=current_user.id,
        status='Concluído'
    ).order_by(Simulado.data_realizado.desc()).limit(3).all()
    
    # Formatar dados para o gráfico
    datas_grafico = []
    notas_grafico = []
    
    for sim in reversed(tri_ultimos_simulados):
        datas_grafico.append(sim.data_realizado.strftime('%d/%m'))
        notas_grafico.append(sim.nota_tri)
    
    # Obter desempenho por área
    areas = ['Linguagens', 'Humanas', 'Natureza', 'Matemática']
    desempenho_areas = {}
    
    # Cálculo mais preciso do desempenho por área
    for area in areas:
        # Buscar questões concluídas desta área
        questoes = Questao.query.join(Simulado).filter(
            Simulado.user_id == current_user.id,
            Simulado.status == 'Concluído',
            Questao.area == area
        ).all()
        
        total = len(questoes)
        acertos = sum(1 for q in questoes if q.verificar_resposta())
        
        if total > 0:
            desempenho_areas[area] = round((acertos / total) * 100)
        else:
            desempenho_areas[area] = 0
    
    return render_template('simulados/index.html',
                          simulados_pendentes=simulados_pendentes,
                          simulados_concluidos=simulados_concluidos,
                          datas_grafico=datas_grafico,
                          notas_grafico=notas_grafico,
                          desempenho_areas=desempenho_areas)

@simulados_bp.route('/<int:simulado_id>')
@login_required
def iniciar_simulado(simulado_id):
    simulado = Simulado.query.get_or_404(simulado_id)
    
    # Verificar se o simulado pertence ao usuário
    if simulado.user_id != current_user.id:
        flash('Você não tem permissão para acessar este simulado.', 'danger')
        return redirect(url_for('simulados.index'))
    
    # Verificar se o simulado já foi realizado
    if simulado.status == 'Concluído':
        return redirect(url_for('simulados.resultado', simulado_id=simulado_id))
    
    # Marcar horário de início se for a primeira vez
    if not simulado.data_realizado:
        simulado.data_realizado = datetime.utcnow()
        db.session.commit()
    
    # Obter a primeira questão do simulado
    primeira_questao = Questao.query.filter_by(simulado_id=simulado_id).order_by(Questao.numero).first()
    
    if not primeira_questao:
        flash('Este simulado não possui questões.', 'warning')
        return redirect(url_for('simulados.index'))
    
    return redirect(url_for('simulados.questao', simulado_id=simulado_id, questao_numero=primeira_questao.numero))

@simulados_bp.route('/<int:simulado_id>/questao/<int:questao_numero>', methods=['GET', 'POST'])
@login_required
def questao(simulado_id, questao_numero):
    simulado = Simulado.query.get_or_404(simulado_id)
    questao = Questao.query.filter_by(simulado_id=simulado_id, numero=questao_numero).first_or_404()
    
    # Verificar permissão
    if simulado.user_id != current_user.id:
        flash('Você não tem permissão para acessar este simulado.', 'danger')
        return redirect(url_for('simulados.index'))
    
    # Registrar o tempo quando o usuário acessa a questão (para cálculo de tempo)
    timestamp_acesso = int(datetime.utcnow().timestamp())
    
    # Processar resposta
    if request.method == 'POST':
        resposta = request.form.get('resposta')
        timestamp_resposta = request.form.get('timestamp', 0)
        
        if resposta in ['A', 'B', 'C', 'D', 'E']:
            # Salvar resposta
            questao.resposta_usuario = resposta
            
            # Calcular tempo de resposta
            if timestamp_resposta and timestamp_acesso:
                try:
                    tempo = int(timestamp_resposta) - timestamp_acesso
                    if tempo > 0:
                        questao.tempo_resposta = tempo
                except (ValueError, TypeError):
                    pass
                
            db.session.commit()
            
            # Verificar se há próxima questão
            proxima_questao = Questao.query.filter(
                Questao.simulado_id == simulado_id,
                Questao.numero > questao_numero
            ).order_by(Questao.numero).first()
            
            if proxima_questao:
                return redirect(url_for('simulados.questao', 
                                    simulado_id=simulado_id, 
                                    questao_numero=proxima_questao.numero))
            else:
                # Finalizar simulado
                return redirect(url_for('simulados.finalizar', simulado_id=simulado_id))
    
    # Obter todas as questões para a navegação
    todas_questoes = Questao.query.filter_by(simulado_id=simulado_id).order_by(Questao.numero).all()
    
    # Calcular progresso
    total_questoes = len(todas_questoes)
    progresso = (questao_numero / total_questoes) * 100
    
    return render_template('simulados/questao.html',
                          simulado=simulado,
                          questao=questao,
                          todas_questoes=todas_questoes,
                          progresso=progresso,
                          timestamp_acesso=timestamp_acesso)

@simulados_bp.route('/<int:simulado_id>/salvar-resposta', methods=['POST'])
@login_required
def salvar_resposta_ajax(simulado_id):
    """Endpoint para salvar resposta via AJAX sem redirecionar"""
    if not request.is_json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), 400
        
    data = request.get_json()
    questao_id = data.get('questao_id')
    resposta = data.get('resposta')
    tempo = data.get('tempo')
    
    # Validações
    if not questao_id or not resposta or resposta not in ['A', 'B', 'C', 'D', 'E']:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    
    # Buscar questão
    questao = Questao.query.get(questao_id)
    if not questao or questao.simulado_id != simulado_id:
        return jsonify({'success': False, 'error': 'Question not found'}), 404
    
    # Verificar permissão
    simulado = Simulado.query.get(simulado_id)
    if simulado.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    # Salvar resposta
    questao.resposta_usuario = resposta
    if tempo and isinstance(tempo, int) and tempo > 0:
        questao.tempo_resposta = tempo
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@simulados_bp.route('/<int:simulado_id>/finalizar')
@login_required
def finalizar(simulado_id):
    simulado = Simulado.query.get_or_404(simulado_id)
    
    # Verificar permissão
    if simulado.user_id != current_user.id:
        flash('Você não tem permissão para acessar este simulado.', 'danger')
        return redirect(url_for('simulados.index'))
    
    # Calcular tempo de realização
    if simulado.data_realizado:
        tempo_realizado = datetime.utcnow() - simulado.data_realizado
        horas = tempo_realizado.seconds // 3600
        minutos = (tempo_realizado.seconds % 3600) // 60
        simulado.tempo_realizado = f"{horas:02d}h{minutos:02d}"
    
    # Marcar como concluído
    simulado.status = 'Concluído'
    
    # Calcular nota TRI com o novo algoritmo mais sofisticado
    simulado.nota_tri = simulado.calcular_nota_tri()
    
    # Calcular estatísticas adicionais
    simulado.calcular_estatisticas()
    
    # Adicionar XP ao usuário com base na nota
    if simulado.nota_tri > 0:
        # Fórmula para calcular XP: 10% da nota TRI arredondado para múltiplo de 5
        xp_ganho = round((simulado.nota_tri * 0.1) / 5) * 5
        current_user.xp_total += int(xp_ganho)
        
        flash(f'Você ganhou {int(xp_ganho)} XP por completar o simulado!', 'success')
    
    db.session.commit()
    
    flash('Simulado finalizado com sucesso!', 'success')
    return redirect(url_for('simulados.resultado', simulado_id=simulado_id))

@simulados_bp.route('/<int:simulado_id>/resultado')
@login_required
def resultado(simulado_id):
    simulado = Simulado.query.get_or_404(simulado_id)
    
    # Verificar permissão
    if simulado.user_id != current_user.id:
        flash('Você não tem permissão para acessar este simulado.', 'danger')
        return redirect(url_for('simulados.index'))
    
    # Verificar se o simulado foi concluído
    if simulado.status != 'Concluído':
        flash('Este simulado ainda não foi concluído.', 'warning')
        return redirect(url_for('simulados.index'))
    
    # Obter estatísticas por área
    areas = {}
    for questao in simulado.questoes:
        area = questao.area
        if area not in areas:
            areas[area] = {'total': 0, 'acertos': 0}
        
        areas[area]['total'] += 1
        if questao.verificar_resposta():
            areas[area]['acertos'] += 1
    
    # Calcular percentuais
    for area in areas:
        areas[area]['percentual'] = (areas[area]['acertos'] / areas[area]['total']) * 100 if areas[area]['total'] > 0 else 0
    
    # Gerar dados para gráfico de tempo por questão
    tempos_questoes = []
    numeros_questoes = []
    
    for questao in simulado.questoes.order_by(Questao.numero):
        if questao.tempo_resposta:
            numeros_questoes.append(questao.numero)
            # Converter segundos para minutos para o gráfico
            tempos_questoes.append(round(questao.tempo_resposta / 60, 1))
    
    # Obter histórico de notas para comparação
    historico_notas = Simulado.query.filter(
        Simulado.user_id == current_user.id,
        Simulado.status == 'Concluído',
        Simulado.id != simulado_id
    ).order_by(Simulado.data_realizado.desc()).limit(3).all()
    
    # Calcular média do usuário para comparação
    media_usuario = db.session.query(db.func.avg(Simulado.nota_tri)).filter(
        Simulado.user_id == current_user.id,
        Simulado.status == 'Concluído'
    ).scalar() or 0
    
    # Obter pontos fortes e fracos
    pontos_fortes = []
    pontos_fracos = []
    
    # Ordenar áreas por desempenho
    areas_ordenadas = sorted(areas.items(), key=lambda x: x[1]['percentual'], reverse=True)
    
    # Top 2 áreas como pontos fortes
    for area, dados in areas_ordenadas[:2]:
        if dados['percentual'] >= 50:  # Só considerar como forte se >= 50%
            pontos_fortes.append(f"{area}: {dados['percentual']:.1f}%")
    
    # Bottom 2 áreas como pontos fracos
    for area, dados in reversed(areas_ordenadas[-2:]):
        if dados['percentual'] < 70:  # Só considerar como fraco se < 70%
            pontos_fracos.append(f"{area}: {dados['percentual']:.1f}%")
    
    return render_template('simulados/resultado.html',
                          simulado=simulado,
                          areas=areas,
                          tempos_questoes=json.dumps(tempos_questoes),
                          numeros_questoes=json.dumps(numeros_questoes),
                          historico_notas=historico_notas,
                          media_usuario=media_usuario,
                          pontos_fortes=pontos_fortes,
                          pontos_fracos=pontos_fracos)