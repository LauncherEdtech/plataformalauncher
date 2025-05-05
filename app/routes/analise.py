from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models.simulado import Simulado, Questao
from app.models.user import User
from app import db
from datetime import datetime, timedelta
from collections import Counter
import json

analise_bp = Blueprint('analise', __name__, url_prefix='/analise')

@analise_bp.route('/')
@login_required
def index():
    """Dashboard principal de análise de desempenho"""
    # Obter todos os simulados concluídos do usuário
    simulados = Simulado.query.filter_by(
        user_id=current_user.id,
        status='Concluído'
    ).order_by(Simulado.data_realizado.desc()).all()
    
    if not simulados:
        return render_template('analise/sem_dados.html')
    
    # Preparar dados para gráficos
    
    # 1. Evolução da nota TRI ao longo do tempo
    datas = []
    notas = []
    for s in simulados:
        datas.append(s.data_realizado.strftime('%d/%m/%Y'))
        notas.append(s.nota_tri)
    
    # 2. Desempenho por área
    areas_stats = {}
    
    # Buscar todas as questões respondidas agrupadas por área
    questoes = Questao.query.join(Simulado).filter(
        Simulado.user_id == current_user.id,
        Simulado.status == 'Concluído'
    ).all()
    
    # Agrupar por área
    for q in questoes:
        if q.area not in areas_stats:
            areas_stats[q.area] = {'total': 0, 'acertos': 0}
        
        areas_stats[q.area]['total'] += 1
        if q.verificar_resposta():
            areas_stats[q.area]['acertos'] += 1
    
    # Calcular percentuais
    for area in areas_stats:
        if areas_stats[area]['total'] > 0:
            areas_stats[area]['percentual'] = round((areas_stats[area]['acertos'] / areas_stats[area]['total']) * 100, 1)
        else:
            areas_stats[area]['percentual'] = 0
    
    # 3. Análise de tempo
    tempo_medio_global = 0
    total_questoes_com_tempo = 0
    
    for s in simulados:
        for q in s.questoes:
            if q.tempo_resposta:
                tempo_medio_global += q.tempo_resposta
                total_questoes_com_tempo += 1
    
    if total_questoes_com_tempo > 0:
        tempo_medio_global = round(tempo_medio_global / total_questoes_com_tempo)
    
    # 4. Análise de padrões de resposta (erros comuns)
    erros_frequentes = {}
    
    for q in questoes:
        if not q.verificar_resposta() and q.resposta_usuario:
            key = f"{q.area}-{q.resposta_usuario}"
            if key not in erros_frequentes:
                erros_frequentes[key] = 0
            erros_frequentes[key] += 1
    
    # Ordenar e pegar os 5 mais frequentes
    erros_mais_frequentes = []
    for key, count in sorted(erros_frequentes.items(), key=lambda x: x[1], reverse=True)[:5]:
        area, resposta = key.split('-')
        erros_mais_frequentes.append({
            'area': area,
            'resposta': resposta,
            'count': count
        })
    
    # 5. Recomendações personalizadas baseadas nos dados
    recomendacoes = []
    
    # Identificar áreas com menos de 60% de acerto
    areas_fracas = []
    for area, stats in areas_stats.items():
        if stats['percentual'] < 60 and stats['total'] >= 5:
            areas_fracas.append(area)
    
    if areas_fracas:
        recomendacoes.append(f"Foque seus estudos em: {', '.join(areas_fracas)}")
    
    # Verificar consistência entre simulados
    if len(simulados) >= 3:
        variacao = max(notas) - min(notas)
        if variacao > 150:
            recomendacoes.append("Sua performance tem muita variação. Tente manter uma rotina mais consistente de estudos.")
        
    # Verificar tempo médio por questão
    if tempo_medio_global > 120:  # mais de 2 minutos por questão
        recomendacoes.append("Você está demorando muito por questão. Pratique técnicas de leitura dinâmica e resolução rápida.")
    
    return render_template('analise/index.html',
                          simulados=simulados,
                          datas=json.dumps(datas),
                          notas=json.dumps(notas),
                          areas_stats=areas_stats,
                          tempo_medio_global=tempo_medio_global,
                          erros_mais_frequentes=erros_mais_frequentes,
                          recomendacoes=recomendacoes)

@analise_bp.route('/desempenho-detalhado/<int:simulado_id>')
@login_required
def desempenho_detalhado(simulado_id):
    """Página de análise detalhada de um simulado específico"""
    simulado = Simulado.query.get_or_404(simulado_id)
    
    # Verificar permissão
    if simulado.user_id != current_user.id:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Verificar se o simulado foi concluído
    if simulado.status != 'Concluído':
        return jsonify({'error': 'Simulado não concluído'}), 400
    
    # Obter estatísticas detalhadas
    questoes = list(simulado.questoes)
    
    # 1. Distribuição de respostas por alternativa
    dist_alternativas = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'Não respondida': 0}
    for q in questoes:
        if q.resposta_usuario:
            dist_alternativas[q.resposta_usuario] += 1
        else:
            dist_alternativas['Não respondida'] += 1
    
    # 2. Tempo médio por questão, agrupado por acerto/erro
    tempo_acertos = []
    tempo_erros = []
    
    for q in questoes:
        if q.tempo_resposta:
            if q.verificar_resposta():
                tempo_acertos.append(q.tempo_resposta)
            else:
                tempo_erros.append(q.tempo_resposta)
    
    media_tempo_acertos = sum(tempo_acertos) / len(tempo_acertos) if tempo_acertos else 0
    media_tempo_erros = sum(tempo_erros) / len(tempo_erros) if tempo_erros else 0
    
    # 3. Análise de dificuldade vs acerto
    dificuldade_acerto = []
    dificuldade_erro = []
    
    for q in questoes:
        if q.verificar_resposta():
            dificuldade_acerto.append(q.dificuldade)
        else:
            dificuldade_erro.append(q.dificuldade)
    
    # 4. Correlação entre tempo e dificuldade
    correlacao_tempo_dificuldade = []
    
    for q in questoes:
        if q.tempo_resposta:
            correlacao_tempo_dificuldade.append({
                'tempo': q.tempo_resposta,
                'dificuldade': q.dificuldade,
                'acertou': q.verificar_resposta()
            })
    
    # 5. Gerar recomendações específicas
    recomendacoes = []
    
    # Verificar se o aluno tem dificuldade com questões difíceis
    if dificuldade_acerto and dificuldade_erro:
        media_dificuldade_acerto = sum(dificuldade_acerto) / len(dificuldade_acerto)
        media_dificuldade_erro = sum(dificuldade_erro) / len(dificuldade_erro)
        
        if media_dificuldade_erro > media_dificuldade_acerto + 0.2:
            recomendacoes.append("Você está tendo mais dificuldade em questões complexas. Foque em aprofundar seu conhecimento nos temas.")
    
    # Verificar se o aluno está demorando muito nas questões erradas
    if media_tempo_acertos and media_tempo_erros:
        if media_tempo_erros > media_tempo_acertos * 1.5:
            recomendacoes.append("Você está demorando muito em questões que acaba errando. Aprenda a identificar quando vale a pena pular uma questão.")
    
    # Verificar padrão de escolha de alternativas
    maior_alternativa = max(dist_alternativas.items(), key=lambda x: x[1] if x[0] != 'Não respondida' else 0)
    if maior_alternativa[1] > len(questoes) * 0.4 and maior_alternativa[0] != 'Não respondida':
        recomendacoes.append(f"Você tem uma tendência a escolher a alternativa {maior_alternativa[0]}. Verifique se não está tendo um viés de escolha.")
    
    # Calcular percentual de conclusão (questões respondidas)
    total_respondidas = sum(1 for q in questoes if q.resposta_usuario)
    percentual_conclusao = (total_respondidas / len(questoes)) * 100 if questoes else 0
    
    return render_template('analise/desempenho_detalhado.html',
                          simulado=simulado,
                          dist_alternativas=dist_alternativas,
                          media_tempo_acertos=media_tempo_acertos,
                          media_tempo_erros=media_tempo_erros,
                          correlacao_tempo_dificuldade=json.dumps(correlacao_tempo_dificuldade),
                          recomendacoes=recomendacoes,
                          percentual_conclusao=percentual_conclusao)

@analise_bp.route('/exportar-pdf/<int:simulado_id>')
@login_required
def exportar_pdf(simulado_id):
    """Endpoint para exportar análise em PDF (implementação simulada)"""
    # Na implementação real, você usaria uma biblioteca como WeasyPrint ou reportlab
    # para gerar o PDF e devolvê-lo como um download
    
    simulado = Simulado.query.get_or_404(simulado_id)
    
    # Verificar permissão
    if simulado.user_id != current_user.id:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Aqui você geraria o PDF... Em vez disso, apenas retornaremos uma mensagem
    return render_template('analise/exportar_simulacao.html', simulado=simulado)

@analise_bp.route('/comparar-simulados')
@login_required
def comparar_simulados():
    """Interface para comparar diferentes simulados"""
    # Obter todos os simulados concluídos
    simulados = Simulado.query.filter_by(
        user_id=current_user.id,
        status='Concluído'
    ).order_by(Simulado.data_realizado.desc()).all()
    
    # Verificar se existem simulados suficientes para comparar
    if len(simulados) < 2:
        return render_template('analise/sem_dados_comparacao.html')
    
    # Parâmetros da requisição
    simulado1_id = request.args.get('simulado1', type=int)
    simulado2_id = request.args.get('simulado2', type=int)
    
    # Se não foram especificados, usar os dois mais recentes
    if not simulado1_id or not simulado2_id:
        simulado1_id = simulados[0].id
        simulado2_id = simulados[1].id
    
    # Buscar dados dos simulados
    simulado1 = Simulado.query.get_or_404(simulado1_id)
    simulado2 = Simulado.query.get_or_404(simulado2_id)
    
    # Verificar permissão
    if simulado1.user_id != current_user.id or simulado2.user_id != current_user.id:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Comparar áreas
    areas_simulado1 = {}
    areas_simulado2 = {}
    
    # Gerar dados de comparação por área
    todas_areas = set()
    
    for q in simulado1.questoes:
        todas_areas.add(q.area)
        if q.area not in areas_simulado1:
            areas_simulado1[q.area] = {'total': 0, 'acertos': 0}
        
        areas_simulado1[q.area]['total'] += 1
        if q.verificar_resposta():
            areas_simulado1[q.area]['acertos'] += 1
    
    for q in simulado2.questoes:
        todas_areas.add(q.area)
        if q.area not in areas_simulado2:
            areas_simulado2[q.area] = {'total': 0, 'acertos': 0}
        
        areas_simulado2[q.area]['total'] += 1
        if q.verificar_resposta():
            areas_simulado2[q.area]['acertos'] += 1
    
    # Calcular percentuais
    for area in todas_areas:
        if area in areas_simulado1 and areas_simulado1[area]['total'] > 0:
            areas_simulado1[area]['percentual'] = (areas_simulado1[area]['acertos'] / areas_simulado1[area]['total']) * 100
        else:
            areas_simulado1[area] = {'total': 0, 'acertos': 0, 'percentual': 0}
            
        if area in areas_simulado2 and areas_simulado2[area]['total'] > 0:
            areas_simulado2[area]['percentual'] = (areas_simulado2[area]['acertos'] / areas_simulado2[area]['total']) * 100
        else:
            areas_simulado2[area] = {'total': 0, 'acertos': 0, 'percentual': 0}
    
    # Dados para gráfico de comparação
    areas_lista = list(todas_areas)
    percentuais1 = [areas_simulado1[a]['percentual'] for a in areas_lista]
    percentuais2 = [areas_simulado2[a]['percentual'] for a in areas_lista]
    
    # Analisar evolução
    evolucao = {}
    for area in todas_areas:
        diff = areas_simulado2[area]['percentual'] - areas_simulado1[area]['percentual']
        evolucao[area] = {
            'diff': diff,
            'status': 'melhorou' if diff > 0 else ('piorou' if diff < 0 else 'manteve')
        }
    
    return render_template('analise/comparar_simulados.html',
                          simulados=simulados,
                          simulado1=simulado1,
                          simulado2=simulado2,
                          areas_lista=json.dumps(areas_lista),
                          percentuais1=json.dumps(percentuais1),
                          percentuais2=json.dumps(percentuais2),
                          evolucao=evolucao)