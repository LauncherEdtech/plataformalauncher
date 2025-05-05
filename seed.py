# seed.py
from app import create_app, db
from app.models.user import User
from app.models.simulado import Simulado, Questao, Alternativa
from app.models.shop import Produto
from app.models.redacao import Redacao  # Importe o modelo Redacao se existir
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

app = create_app()

# Dados de exemplo para questões realistas
questoes_exemplo = [
    {
        "area": "Linguagens",
        "texto": "Leia o texto a seguir:\n\n'A língua é um sistema de signos que exprime ideias, e é comparável, por isso, à escrita, ao alfabeto dos surdos-mudos, aos ritos simbólicos, às formas de polidez, aos sinais militares etc. Ela é apenas o principal desses sistemas.'\n\nO texto acima, de Ferdinand de Saussure, define a língua como:",
        "alternativas": [
            "Um conjunto de signos usados apenas na comunicação verbal.",
            "O mais importante sistema de signos usado para expressar ideias.",
            "Um sistema simbólico inferior aos demais citados no texto.",
            "Um conjunto de regras gramaticais que organiza os signos linguísticos.",
            "Uma manifestação individual de fala, passível de mudanças pelo usuário."
        ],
        "resposta_correta": "B",
        "dificuldade": 0.5
    },
    {
        "area": "Linguagens",
        "texto": "O emprego da vírgula está correto em todas as alternativas, EXCETO:",
        "alternativas": [
            "Ontem à noite, assisti a um filme interessante.",
            "O candidato, nervoso com a prova, não conseguiu se concentrar.",
            "Paulo, que é meu amigo, ganhou o concurso de redação.",
            "Ele comprou, um novo celular com o dinheiro que economizou.",
            "No próximo sábado, se não houver imprevisto, iremos à praia."
        ],
        "resposta_correta": "D",
        "dificuldade": 0.4
    },
    {
        "area": "Matemática",
        "texto": "Uma escada de 10 metros de comprimento está apoiada em uma parede vertical. O pé da escada está a 6 metros da parede. A que altura do solo está o topo da escada?",
        "alternativas": [
            "4 metros",
            "6 metros",
            "8 metros",
            "10 metros",
            "12 metros"
        ],
        "resposta_correta": "A",
        "dificuldade": 0.6
    },
    {
        "area": "Matemática",
        "texto": "Resolva a equação: 2x² - 5x - 3 = 0",
        "alternativas": [
            "x = 3 ou x = -0,5",
            "x = 3 ou x = 0,5",
            "x = -3 ou x = 0,5",
            "x = -3 ou x = -0,5",
            "x = 2 ou x = -3"
        ],
        "resposta_correta": "A",
        "dificuldade": 0.7
    },
    {
        "area": "Humanas",
        "texto": "Sobre a Revolução Industrial, ocorrida inicialmente na Inglaterra durante o século XVIII, pode-se afirmar corretamente que:",
        "alternativas": [
            "Diminuiu a produção de mercadorias em comparação ao período artesanal.",
            "Melhorou as condições de trabalho e de vida para todos os trabalhadores.",
            "Propiciou a expansão do sistema capitalista e da produção em larga escala.",
            "Eliminou totalmente o trabalho manual nas indústrias europeias.",
            "Reduziu a migração do campo para as cidades industriais."
        ],
        "resposta_correta": "C",
        "dificuldade": 0.5
    },
    {
        "area": "Humanas",
        "texto": "A Guerra Fria, período histórico que sucedeu a Segunda Guerra Mundial, foi caracterizada por:",
        "alternativas": [
            "Conflito armado direto entre Estados Unidos e União Soviética.",
            "Expansão de regimes democráticos em todo o mundo.",
            "Disputa ideológica entre o capitalismo e o socialismo.",
            "Alinhamento político e econômico entre as duas superpotências.",
            "Fim das tensões nucleares no cenário mundial."
        ],
        "resposta_correta": "C",
        "dificuldade": 0.5
    },
    {
        "area": "Natureza",
        "texto": "O processo pelo qual a água passa do estado líquido para o gasoso, absorvendo calor do ambiente, é chamado de:",
        "alternativas": [
            "Fusão",
            "Condensação",
            "Solidificação",
            "Evaporação",
            "Sublimação"
        ],
        "resposta_correta": "D",
        "dificuldade": 0.4
    },
    {
        "area": "Natureza",
        "texto": "A respeito da Tabela Periódica dos Elementos, é INCORRETO afirmar que:",
        "alternativas": [
            "Os elementos estão organizados em ordem crescente de número atômico.",
            "As propriedades dos elementos são periódicas em relação ao número atômico.",
            "Os elementos de uma mesma família apresentam propriedades químicas semelhantes.",
            "Os gases nobres são altamente reativos devido à sua configuração eletrônica.",
            "Os metais alcalinos perdem facilmente um elétron, formando cátions monovalentes."
        ],
        "resposta_correta": "D",
        "dificuldade": 0.7
    },
    {
        "area": "Linguagens",
        "texto": "Analise o seguinte trecho do poema 'Vou-me Embora pra Pasárgada', de Manuel Bandeira:\n\n'Vou-me embora pra Pasárgada\nLá sou amigo do rei\nLá tenho a mulher que eu quero\nNa cama que escolherei'\n\nÉ correto afirmar que o poema expressa:",
        "alternativas": [
            "Uma descrição realista de um lugar existente chamado Pasárgada.",
            "Uma crítica direta ao sistema monárquico brasileiro.",
            "Um lugar utópico onde o eu lírico poderia realizar seus desejos.",
            "O desejo de voltar à infância vivida em uma cidade pequena.",
            "Uma narrativa histórica sobre um reino antigo da Pérsia."
        ],
        "resposta_correta": "C",
        "dificuldade": 0.6
    },
    {
        "area": "Matemática",
        "texto": "Em uma progressão aritmética, o primeiro termo é 5 e a razão é 3. Qual é o décimo termo?",
        "alternativas": [
            "14",
            "23",
            "32",
            "41",
            "50"
        ],
        "resposta_correta": "C",
        "dificuldade": 0.5
    },
    {
        "area": "Humanas",
        "texto": "Qual destes eventos é conhecido como marco inicial da Idade Contemporânea?",
        "alternativas": [
            "Queda do Império Romano do Ocidente",
            "Tomada de Constantinopla pelos turcos otomanos",
            "Revolução Francesa",
            "Primeira Guerra Mundial",
            "Queda do Muro de Berlim"
        ],
        "resposta_correta": "C",
        "dificuldade": 0.5
    },
    {
        "area": "Natureza",
        "texto": "Qual das seguintes organelas celulares é responsável pela respiração celular e produção de ATP?",
        "alternativas": [
            "Ribossomo",
            "Complexo de Golgi",
            "Mitocôndria",
            "Lisossomo",
            "Retículo endoplasmático"
        ],
        "resposta_correta": "C",
        "dificuldade": 0.4
    }
]

with app.app_context():
    # Criar tabelas
    db.create_all()
    
    # Limpar dados existentes e criar novos
    print("Limpando banco de dados...")
    try:
        # Usar raw SQL para contornar restrições de chave estrangeira
        db.session.execute("DELETE FROM alternativa")
        db.session.execute("DELETE FROM questao")
        db.session.execute("DELETE FROM simulado")
        db.session.execute("DELETE FROM produto")
        db.session.execute("DELETE FROM user")
        
        # Se o modelo Redacao existir, também limpe essa tabela
        try:
            db.session.execute("DELETE FROM redacao")
        except:
            print("Tabela redacao não encontrada ou já está vazia.")
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao limpar banco de dados: {str(e)}")
        print("Continuando com a criação de dados...")
    
    print("Criando dados de exemplo...")
    
    # Criar usuários de exemplo
    users = [
        {
            "username": "estudante1",
            "email": "estudante1@example.com",
            "nome_completo": "João Silva",
            "password": "senha123",
            "xp_total": 750
        },
        {
            "username": "estudante2",
            "email": "estudante2@example.com",
            "nome_completo": "Maria Oliveira",
            "password": "senha123",
            "xp_total": 1200
        },
        {
            "username": "admin",
            "email": "admin@launcher.com",
            "nome_completo": "Administrador Sistema",
            "password": "admin123",
            "xp_total": 9999
        }
    ]
    
    for user_data in users:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            nome_completo=user_data["nome_completo"],
            xp_total=user_data["xp_total"]
        )
        user.password_hash = generate_password_hash(user_data["password"])
        db.session.add(user)
    
    db.session.commit()
    
    # Criar títulos e áreas mais realistas para simulados
    titulos_simulados = [
        {"titulo": "Simulado Nacional ENEM", "areas": "Geral (Todas Áreas)"},
        {"titulo": "Simulado de Linguagens e Códigos", "areas": "Linguagens"},
        {"titulo": "Simulado de Matemática", "areas": "Matemática"},
        {"titulo": "Simulado de Ciências Humanas", "areas": "Humanas"},
        {"titulo": "Simulado de Ciências da Natureza", "areas": "Natureza"},
        {"titulo": "Simulado Integrado", "areas": "Linguagens e Matemática"},
        {"titulo": "Simulado Intensivo", "areas": "Humanas e Natureza"}
    ]
    
    # Criar simulados: alguns concluídos, outros pendentes
    for i, user in enumerate(User.query.all()):
        # Cada usuário terá de 2 a 4 simulados
        num_simulados = random.randint(2, 4)
        
        for j in range(1, num_simulados + 1):
            titulo_simulado = random.choice(titulos_simulados)
            
            simulado = Simulado(
                numero=j,
                titulo=f"{titulo_simulado['titulo']} #{j}",
                areas=titulo_simulado["areas"],
                duracao_minutos=random.choice([60, 120, 180, 240]),
                user_id=user.id,
                status="Pendente"  # Por padrão, começa como pendente
            )
            
            # Para o primeiro usuário, garanta alguns simulados pendentes
            if i == 0 and j >= num_simulados - 1:
                simulado.status = "Pendente"
            # Para todos, alguns simulados são concluídos
            elif random.random() < 0.6:  # 60% de chance de ser concluído
                simulado.status = "Concluído"
                simulado.data_realizado = datetime.now() - timedelta(days=random.randint(1, 30))
                simulado.tempo_realizado = f"{random.randint(1, 3)}h{random.randint(10, 59)}"
                simulado.nota_tri = random.randint(400, 850)
            
            db.session.add(simulado)
            db.session.commit()  # Commit aqui para obter o ID do simulado
            
            # Criar questões para cada simulado (de 5 a 15 questões)
            num_questoes = random.randint(5, 15)
            
            # Copiar as questões de exemplo e complementar com questões genéricas se necessário
            questoes_simulado = questoes_exemplo.copy()
            random.shuffle(questoes_simulado)
            
            for k in range(1, num_questoes + 1):
                # Se temos mais questões do que o exemplo, usamos dados genéricos
                if k <= len(questoes_simulado):
                    q_data = questoes_simulado[k-1]
                    area = q_data["area"]
                    texto = q_data["texto"]
                    alt_textos = q_data["alternativas"]
                    resposta_correta = q_data["resposta_correta"]
                    dificuldade = q_data["dificuldade"]
                else:
                    area = random.choice(["Linguagens", "Matemática", "Humanas", "Natureza"])
                    texto = f"Texto da questão {k} do simulado {j}. Esta é uma questão de {area}."
                    alt_textos = [f"Alternativa genérica {l} da questão {k}." for l in "ABCDE"]
                    resposta_correta = random.choice(["A", "B", "C", "D", "E"])
                    dificuldade = random.uniform(0.3, 0.9)
                
                questao = Questao(
                    numero=k,
                    texto=texto,
                    area=area,
                    dificuldade=dificuldade,
                    resposta_correta=resposta_correta,
                    simulado_id=simulado.id
                )
                
                # Para simulados concluídos, adicionar resposta do usuário
                if simulado.status == "Concluído":
                    # Probabilidade de acerto baseada na dificuldade
                    prob_acerto = 1 - dificuldade  # Quanto mais difícil, menor a chance de acertar
                    if random.random() < prob_acerto:
                        questao.resposta_usuario = resposta_correta
                    else:
                        opcoes = ["A", "B", "C", "D", "E"]
                        opcoes.remove(resposta_correta)
                        questao.resposta_usuario = random.choice(opcoes)
                    
                    # Adicionar tempo de resposta (entre 30 segundos e 5 minutos)
                    questao.tempo_resposta = random.randint(30, 300)
                
                db.session.add(questao)
                db.session.commit()  # Commit para obter o ID da questão
                
                # Criar alternativas para cada questão
                for idx, letra in enumerate(["A", "B", "C", "D", "E"]):
                    alternativa = Alternativa(
                        letra=letra,
                        texto=alt_textos[idx] if idx < len(alt_textos) else f"Alternativa {letra} da questão {k}.",
                        questao_id=questao.id
                    )
                    db.session.add(alternativa)
                
                db.session.commit()
        
        # Criar algumas redações para cada usuário se o modelo Redacao existir
        try:
            temas_redacao = [
                "O impacto da tecnologia na educação brasileira",
                "Desafios para a preservação ambiental no século XXI",
                "Caminhos para combater a desinformação na era digital",
                "A importância da educação financeira para jovens",
                "Consequências da polarização política na sociedade"
            ]
            
            for k in range(1, random.randint(0, 3)):
                data_envio = datetime.now() - timedelta(days=random.randint(1, 60))
                
                redacao = Redacao(
                    titulo=random.choice(temas_redacao),
                    conteudo=f"Texto da redação {k} do usuário {user.username}. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam at justo vel nunc lacinia consectetur.",
                    data_envio=data_envio,
                    user_id=user.id
                )
                
                # Algumas redações já foram corrigidas
                if random.random() < 0.7:
                    redacao.nota = random.randint(500, 1000)
                    redacao.feedback = "Feedback detalhado para esta redação. Você desenvolveu bem os argumentos, mas precisa melhorar a conclusão."
                
                db.session.add(redacao)
                db.session.commit()
        except Exception as e:
            print(f"Erro ao criar redações: {str(e)}")
            print("Continuando com a criação de produtos...")
    
    # Criar produtos para a loja com imagens mais realistas
    produtos = [
        {"nome": "Camisa Launcher Edição 2025", "preco_xp": 3000, "imagem": "camisa.jpg", "estoque": 50},
        {"nome": "Garrafa Térmica Launcher 500ml", "preco_xp": 2000, "imagem": "garrafa.jpg", "estoque": 30},
        {"nome": "Caneca Launcher Motivacional", "preco_xp": 1500, "imagem": "caneca.jpg", "estoque": 100},
        {"nome": "Fone Bluetooth Launcher Study", "preco_xp": 4000, "imagem": "fone.jpg", "estoque": 20},
        {"nome": "Kit Cadernos Launcher", "preco_xp": 2500, "imagem": "cadernos.jpg", "estoque": 40},
        {"nome": "Mochila Launcher Premium", "preco_xp": 5000, "imagem": "mochila.jpg", "estoque": 15}
    ]
    
    for p in produtos:
        produto = Produto(
            nome=p["nome"],
            descricao=f"Produto oficial da Plataforma Launcher. {p['nome']} de alta qualidade para acompanhar sua jornada de estudos.",
            imagem=p["imagem"],
            preco_xp=p["preco_xp"],
            estoque=p["estoque"],
            disponivel=True
        )
        db.session.add(produto)
    
    db.session.commit()
    print("Dados de exemplo criados com sucesso!")
    
    # Mostrar estatísticas dos dados criados
    print("\nEstatísticas dos dados gerados:")
    print(f"Usuários: {User.query.count()}")
    print(f"Simulados: {Simulado.query.count()}")
    print(f"Simulados Pendentes: {Simulado.query.filter_by(status='Pendente').count()}")
    print(f"Simulados Concluídos: {Simulado.query.filter_by(status='Concluído').count()}")
    print(f"Questões: {Questao.query.count()}")
    print(f"Alternativas: {Alternativa.query.count()}")
    
    # Verificar se o modelo Redacao existe
    try:
        print(f"Redações: {Redacao.query.count()}")
    except:
        print("Redações: Modelo não disponível")
    
    print(f"Produtos: {Produto.query.count()}")
    
    # Mostrar credenciais para login
    print("\nCredenciais para login:")
    for user in users:
        print(f"Username: {user['username']}, Senha: {user['password']}")