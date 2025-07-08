import csv
import re

def parse_decreto_para_dados_tabela(texto_decreto):
    """
    Analisa o texto de um decreto para extrair informações estruturadas
    e a quantidade de contribuições por item.

    Args:
        texto_decreto (str): O conteúdo completo do decreto como uma string.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa
              uma linha da tabela formatada para análise.
    """
    dados_processados = []
    
    # Variáveis para manter o contexto atual (Título, Capítulo, Seção, Artigo, etc.)
    current_titulo = ""
    current_capitulo = ""
    current_secao = ""
    current_artigo = ""

    # Dividir o texto em linhas para processamento
    linhas = texto_decreto.split('\n')

    # Expressões regulares para identificar os elementos
    re_titulo = re.compile(r'^(TÍTULO [IVXLCDM]+)$')
    re_capitulo = re.compile(r'^(CAPÍTULO [IVXLCDM]+)$')
    # Ajuste para Seção que pode ter título em vez de número romano
    re_secao = re.compile(r'^(Seção [IVXLCDM]+|Seção [A-Za-zÀ-ÖØ-öø-ÿ\s]+)$') # Inclui Seção com texto
    
    # Expressão para capturar Número do Item, Quantidade de Contribuições e o texto subsequente
    re_item_e_contribuicao = re.compile(r'^(\d+)\s+(\d+)\s+(.*)$')
    
    # Expressões para identificar Artigos, Incisos e Alíneas dentro do texto
    re_artigo_em_texto = re.compile(r'^Art\. (\d+)[º]?')
    re_inciso_em_texto = re.compile(r'^[IVXLCDM]+\s*-') # I -, II -, III -, etc.
    re_alinea_em_texto = re.compile(r'^[a-z]\)') # a), b), c), etc.
    re_paragrafo_em_texto = re.compile(r'^§\s*(\d+)º?|Parágrafo único\.') # § 1º, § único, etc.

    for i, linha in enumerate(linhas):
        linha_limpa = linha.strip()

        if not linha_limpa:
            continue # Ignorar linhas vazias

        # Verifica TÍTULO
        match_titulo = re_titulo.match(linha_limpa)
        if match_titulo:
            current_titulo = match_titulo.group(1)
            current_capitulo = "" # Reset capítulo ao mudar de título
            current_secao = ""    # Reset seção ao mudar de título
            current_artigo = ""   # Reset artigo ao mudar de título
            continue

        # Verifica CAPÍTULO
        match_capitulo = re_capitulo.match(linha_limpa)
        if match_capitulo:
            current_capitulo = match_capitulo.group(1)
            current_secao = ""    # Reset seção ao mudar de capítulo
            current_artigo = ""   # Reset artigo ao mudar de capítulo
            continue

        # Verifica SEÇÃO
        match_secao = re_secao.match(linha_limpa)
        if match_secao:
            current_secao = match_secao.group(1)
            current_artigo = ""   # Reset artigo ao mudar de seção
            continue

        # Verifica se é uma linha de item com número e contribuições
        match_item_contrib = re_item_e_contribuicao.match(linha_limpa)
        if match_item_contrib:
            num_item = match_item_contrib.group(1)
            qtd_contribuicoes = match_item_contrib.group(2)
            texto_item = match_item_contrib.group(3).strip() # Texto do Art/Inciso/Alínea/Parágrafo
            
            titulo_item = current_titulo
            capitulo_item = current_capitulo
            secao_item = current_secao
            artigo_item = ""
            inciso_item = ""
            alinea_item = ""
            
            # Tenta identificar se o texto do item é um Artigo, Inciso ou Alínea
            match_art = re_artigo_em_texto.match(texto_item)
            if match_art:
                artigo_item = f"Art. {match_art.group(1)}"
                current_artigo = artigo_item # Atualiza o artigo atual
            else:
                match_inciso = re_inciso_em_texto.match(texto_item)
                if match_inciso:
                    # O Inciso é o início da linha, ex: "I - ação de saneamento..."
                    inciso_item = texto_item.split(' - ')[0].strip()
                    artigo_item = current_artigo # Mantém o artigo do contexto
                else:
                    match_alinea = re_alinea_em_texto.match(texto_item)
                    if match_alinea:
                        # A Alínea é o início da linha, ex: "a) do titular..."
                        alinea_item = texto_item.split(')')[0].strip()
                        artigo_item = current_artigo # Mantém o artigo do contexto
                    else:
                        # Se não for Artigo, Inciso ou Alínea, pode ser um Parágrafo (§) ou outro texto
                        # Mas ele estará associado ao último artigo conhecido.
                        if re_paragrafo_em_texto.match(texto_item):
                            artigo_item = current_artigo # Mantém o artigo do contexto
                            # Não estamos criando uma coluna separada para "Parágrafo",
                            # ele é implicitamente associado ao Artigo.

            dados_processados.append({
                "Título": titulo_item,
                "Capítulo": capitulo_item,
                "Seção": secao_item,
                "Art.": artigo_item,
                "Inciso": inciso_item,
                "Alínea": alinea_item,
                "Número do Item": num_item,
                "Quantidade de Contribuições": qtd_contribuicoes
            })
            continue
            
    return dados_processados

# Reutilizando a função de geração de tabela e planilha do exemplo anterior
def gerar_tabela_analise_e_planilha(dados_tabela, nome_arquivo_csv="analise_decreto.csv"):
    """
    Gera uma tabela formatada para análise no console e salva os dados
    em um arquivo CSV.
    """
    # 1. Definição do Cabeçalho da Tabela
    cabecalho = [
        "Título", "Capítulo", "Seção", "Art.", "Inciso",
        "Alínea", "Número do Item", "Quantidade de Contribuições"
    ]

    # --- Parte 1: Gerar a Tabela no Console ---
    larguras = {col: len(col) for col in cabecalho}
    for linha in dados_tabela:
        for col in cabecalho:
            conteudo_celula = str(linha.get(col, ""))
            if len(conteudo_celula) > larguras[col]:
                larguras[col] = len(conteudo_celula)

    linha_cabecalho_console = " | ".join([f"{col:<{larguras[col]}}" for col in cabecalho])
    print(linha_cabecalho_console)

    linha_separadora_console = "+".join(["-" * larguras[col] for col in cabecalho])
    print(linha_separadora_console)

    for linha in dados_tabela:
        valores_linha = [str(linha.get(col, "")) for col in cabecalho]
        linha_formatada_console = " | ".join([f"{valor:<{larguras[cabecalho[i]]}}"
                                              for i, valor in enumerate(valores_linha)])
        print(linha_formatada_console)

    print(f"\n--- Salvando dados na planilha '{nome_arquivo_csv}' ---")

    # --- Parte 2: Salvar a Planilha CSV ---
    try:
        with open(nome_arquivo_csv, mode='w', newline='', encoding='utf-8') as arquivo_csv:
            writer = csv.DictWriter(arquivo_csv, fieldnames=cabecalho)
            writer.writeheader()
            writer.writerows(dados_tabela)
        print(f"Planilha '{nome_arquivo_csv}' gerada com sucesso!")
    except IOError as e:
        print(f"Erro ao salvar o arquivo CSV: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


# --- Conteúdo COMPLETO do Decreto (Atualizado com a continuação) ---
conteudo_decreto = """
Presidência da República
Acessibilidade  Entrar
Busca



Navegação
Participa + Brasil
Página Inicial / Órgãos Públicos > Ministério das Cidades > MCID - Coordenação-Geral do Marco Legal do Saneamento > Minuta de Decreto que atualiza o Decreto nº 7.217, de 2010, regulamentador da Lei nº 11.445, de 2007.


Minuta de Decreto que atualiza o Decreto nº 7.217, de 2010, regulamentador da Lei nº 11.445, de 2007.
Órgão: Ministério das Cidades
Setor: MCID - Coordenação-Geral do Marco Legal do Saneamento
Status: Encerrada
Publicação no DOU:  19/03/2025  
Abertura: 19/03/2025
Encerramento: 03/05/2025
Processo: 80000.005700/2024-13
Contribuições recebidas: 1220
Responsável pela consulta: Secretaria Nacional de Saneamento Ambiental
Contato: cgml.snsa@cidades.gov.br
Resumo
Trata-se de proposta de atualização e compatibilização do conteúdo do Decreto nº 7.217/2010 com as alterações promovidas pela Lei nº 14.026/2020, regulamentando as novas diretrizes, readequando as antigas, orientando os diversos atores envolvidos na aplicação dos novos dispositivos trazidos pela Lei, especialmente nos setores vulneráveis e áreas rurais, com foco no atingimento das metas propostas de universalização dos serviços de saneamento.
Desta forma, prevê a revogação do Decreto nº 7.217/2010, com o intuito de manter um regulamento único e atualizado em função dos novos dispositivos.
Observa-se que o texto em questão é fruto das discussões realizadas no âmbito do Grupo de Trabalho da SNSA e finalizado em 2023.
Solicitamos que as contribuições sejam objetivas, com proposta de texto claros de alteração, supressão ou inclusão de dispositivos.
Para participar, certifique-se de estar "logado" na plataforma, selecione o parágrafo que deseja contribuir clicando sobre ele ou no balão ao lado.
Desde já agradecemos a sua participação!
Conteúdo
- Clique no balão  ou no parágrafo que deseja contribuir -
DECRETO Nº XXX, DE XX DE XX DE 2025

Regulamenta a Lei nº 11.445, de 5 de janeiro de 2007, que estabelece as diretrizes nacionais para o saneamento básico, e dá outras providências.

O PRESIDENTE DA REPÚBLICA, no uso das atribuições que lhe confere o art. 84, incisos IV e VI, alínea "a", da Constituição, e tendo em vista o disposto na Lei nº 11.445, de 5 de janeiro de 2007, DECRETA:
TÍTULO I
DAS DISPOSIÇÕES PRELIMINARES
CAPÍTULO I
DO OBJETO
1
 6
	Art. 1º Este Decreto estabelece normas para execução da Lei nº 11.445, de 5 de janeiro de 2007.

CAPÍTULO II
DAS DEFINIÇÕES
2
 20
	Art. 2º Para os fins deste Decreto, consideram-se as definições dos artigos 3º, 3º-A, 3º-B, 3º-C e 3º-D da Lei nº 11.445, de 2007, bem como as seguintes definições:
3
 45
	I - ação de saneamento básico: implantação de solução individual ou coletiva de saneamento básico em área rural, em que a operação e manutenção dependa do usuário e que atenda adequadamente à população, nos termos do art. 5º da Lei nº 11.445, de 2007;
4
 20
	II - água potável: água para consumo humano cujos parâmetros microbiológicos, físicos e químicos atendam ao padrão de potabilidade estabelecido pelas normas do Ministério da Saúde;  
5
 19
	III - aviso: informação dirigida ao usuário pelo prestador dos serviços, com comprovação de recebimento, que tenha como objetivo notificar sobre a prestação dos serviços;
6
 2
	IV - comunicação: informação dirigida a usuários e ao regulador, inclusive por meio de veiculação em mídia impressa ou eletrônica;  
7
 3
	V - conferências das cidades: conferências sobre assuntos de interesse urbano, nos níveis nacional, estadual e municipal, conforme inciso III do art. 43 da Lei nº 10.257, de 10 de julho de 2001.
8
 5
	VI - edificação permanente: construção de caráter não transitório, destinada a abrigar atividade humana;
9
 5
	VII - entidade reguladora, entidade de regulação, regulador, agência reguladora ou consórcio público de regulação: entidade de natureza autárquica dotada de independência decisória e autonomia administrativa, orçamentária e financeira, que desempenha a função de regulação e fiscalização atendendo aos princípios de transparência, tecnicidade, celeridade e objetividade das decisões;
10
 4
	VIII - requisitos de eficácia e eficiência: parâmetros de qualidade de efluentes, a fim de se alcançar progressivamente, por meio do aperfeiçoamento dos sistemas e processos de tratamento, o atendimento às classes dos corpos hídricos, conforme seu enquadramento;
11
 7
	IX - fiscalização: atividades de acompanhamento, monitoramento, controle ou avaliação, no sentido de garantir o cumprimento de normas e regulamentos editados pelo poder público e a utilização, efetiva ou potencial, do serviço público;
12
 5
	X - metas progressivas de qualidade dos efluentes de unidades de tratamento de esgotos sanitários: objetivos de qualidade dos efluentes de unidades de tratamento de esgotos sanitários que devem ser alcançados de forma progressiva para atender aos padrões das classes dos corpos hídricos em que forem lançados;
13
 2
	XI - parceria público-privada: contrato administrativo de concessão, na modalidade patrocinada ou administrativa, nos termos da Lei nº 11.079, de 30 de dezembro de 2004;  
14
 5
	XII - planejamento: atividades atinentes à identificação, qualificação, quantificação, organização e orientação de todas as ações, públicas e privadas, por meio das quais o serviço público deve ser prestado ou colocado à disposição de forma adequada;
15
 5
	XIII - prestação de serviço público de saneamento básico: atividade, acompanhada ou não de execução de obra, com objetivo de permitir aos usuários acesso a serviço público de saneamento básico com características e padrões de qualidade determinados pela legislação, planejamento ou regulação;  
16
 12
	XIV - prestador de serviço público ou prestador dos serviços: o órgão ou entidade, inclusive empresa:  
17
 7
	a) do titular, ao qual a lei tenha atribuído competência de prestar serviço público de saneamento básico; ou  
18
 6
	b) ao qual o titular tenha delegado a prestação do serviço público de saneamento básico, observado o disposto no art. 10 da Lei nº 11.445, de 2007;
19
 7
	XV - regulação: todo e qualquer ato que discipline ou organize determinado serviço público, incluindo suas características, padrões de qualidade e de quantidade, regularidade dos serviços, impacto socioambiental, direitos e obrigações dos usuários e dos responsáveis por sua oferta ou prestação, e fixação e revisão do valor de tarifas e outros preços públicos;    
20
 9
	XVI - saneamento básico em área rural: ação ou serviço de saneamento básico implementado em áreas rurais ou com características predominantemente rurais definidas em programa específico, conforme o inciso III do § 1º do art. 52 da Lei nº 11.445, de 2007, cujo objetivo esteja voltado para a proteção à dignidade humana;
21
 3
	XVII - serviço público de saneamento básico: conjunto dos serviços públicos de abastecimento de água, de esgotamento sanitário, de limpeza urbana e manejo de resíduos sólidos e de drenagem e manejo das águas pluviais urbanas, bem como infraestruturas destinadas exclusivamente a cada um destes serviços;  
22
 16
	XVIII - solução alternativa e descentralizada de saneamento básico: ação de saneamento básico ofertada quando a localidade não for atendida por sistemas públicos de saneamento, podendo ser de uso individual ou coletivo: 
23
 3
	a) individual: quando atende a apenas um domicílio;
24
 1
	b) coletivo: quando atende a mais de um domicílio; 
25
 16
	XIX - titular do serviço: os Municípios e o Distrito Federal, observadas as disposições sobre exercício da titularidade em casos de interesse comum constantes do art. 8º da Lei nº 11.445, de 2007.
26
 12
	XX - universalização: ampliação progressiva do acesso de todos os domicílios ocupados aos serviços públicos de saneamento básico; e  
27
 0
	XXI - usuário: pessoa física ou jurídica que se beneficia ou se utiliza, efetiva ou potencialmente, de serviço público.  
28
 11
	§ 1º Para os fins do inciso XIV do caput deste Decreto, consideram-se também prestador de serviço público de manejo de resíduos sólidos as associações ou cooperativas, formadas por pessoas físicas de baixa renda, reconhecidas pelo Poder Público como catadores de materiais recicláveis, que executam coleta, processamento e comercialização de resíduos sólidos urbanos recicláveis ou reutilizáveis.  
TÍTULO II

DAS DIRETRIZES PARA OS SERVIÇOS PÚBLICOS DE SANEAMENTO BÁSICO

CAPÍTULO I

DOS SERVIÇOS PÚBLICOS DE SANEAMENTO BÁSICO 

Seção I

Dos Serviços Públicos de Abastecimento de Água
29
 3
	Art. 3º Consideram-se serviços públicos de abastecimento de água aqueles especificados no art. 3º-A da Lei nº 11.445, de 2007.
30
 5
	Art. 4º O Ministério da Saúde definirá os parâmetros e padrões de potabilidade da água, bem como estabelecerá os procedimentos e responsabilidades relativos ao controle e vigilância da qualidade da água para consumo humano.    
31
 7
	§ 1º A responsabilidade do prestador de serviço público no que se refere ao controle da qualidade da água não prejudica a vigilância da qualidade da água para consumo humano por parte da autoridade de saúde pública.    
32
 6
	§ 2º Os prestadores dos serviços de abastecimento de água devem informar e orientar a população sobre os procedimentos a serem adotados em caso de situações de emergência que ofereçam risco à saúde pública, atendidas as orientações fixadas pela autoridade competente.    
33
 11
	Art. 5º A instalação hidráulica predial ligada à rede pública de abastecimento de água não poderá ser também alimentada por outras fontes.    
34
 6
	§ 1º A legislação e as normas de regulação deverão prever sanções administrativas a quem infringir o disposto no caput.  
35
 3
	§ 2º O disposto no § 1º do caput deste Decreto não exclui a possibilidade da adoção de medidas administrativas para fazer cessar a irregularidade, bem como a responsabilização civil no caso de contaminação de água das redes públicas ou do próprio usuário.  
36
 10
	§ 3º Serão admitidas instalações hidráulicas prediais com objetivo de reúso de efluentes ou aproveitamento de água de chuva, desde que devidamente autorizadas pela autoridade competente.    
37
 27
	Art. 6º A remuneração pela prestação dos serviços públicos de abastecimento de água poderá ser fixada com base no volume consumido de água, podendo ser progressiva, em razão do consumo.    
38
 2
	§ 1º O volume de água consumido deve ser aferido por meio de medição individualizada, levando-se em conta cada uma das unidades, mesmo quando situadas na mesma edificação.
39
 8
	§ 2º Ficam excetuadas do disposto no § 1º do caput deste Decreto, entre outras previstas na legislação, as situações em que as infraestruturas das edificações existentes não permitam individualização do consumo ou em que a absorção dos custos para instalação dos medidores individuais seja economicamente inviável para o usuário.    
40
 6
	§ 3º Nas situações previstas no § 2º do caput deste Decreto, poderão ser instrumentalizados contratos especiais com os prestadores dos serviços, nos quais serão estabelecidas as responsabilidades, os critérios de rateio e a forma de remuneração.  
41
 15
	Art. 7º As edificações permanentes urbanas serão conectadas às redes públicas de abastecimento de água disponíveis e estarão sujeitas ao pagamento de taxas, tarifas e outros preços públicos decorrentes da disponibilização e da manutenção da infraestrutura e do uso desses serviços, nos termos do art. 45 da Lei nº 11.445, de 2007.  
42
 1
	§ 1º A cobrança do valor referido no caput não isenta o usuário da obrigação da conexão às redes disponíveis.  
43
 7
	§ 2º Poderão ser adotados subsídios para viabilizar a conexão, inclusive intradomiciliar, dos usuários de baixa renda, conforme definição em contrato ou em normativo da entidade reguladora.
44
 23
	§ 3. A entidade reguladora ou o titular dos serviços públicos de saneamento básico deverá definir, nos termos do § 5º do art. 45 da Lei nº 11.445, de 2007, os critérios para dispensa dos usuários de conectar-se à rede pública de abastecimento de água, quando da utilização de captação de água de chuva.
45
 13
	Art. 8º No que se refere o art. 43-A da Lei nº 11.455, de 2007, as entidades reguladoras devem definir critérios e prazos para que os prestadores dos serviços possam corrigir falhas na rede de abastecimento de água e coibir as ligações irregulares, podendo utilizar como parâmetros normas de referência da Agência Nacional de Águas e Saneamento Básico (ANA).
Seção II

Dos Serviços Públicos de Esgotamento Sanitário
46
 0
	Art. 9º Consideram-se serviços públicos de esgotamento sanitário aqueles especificados no art. 3º-B da Lei nº 11.445, de 2007.
47
 16
	Art. 10. A legislação e as normas de regulação poderão prever penalidades em face de lançamentos de esgotos não compatíveis com a rede de esgotamento sanitário, bem como em face do lançamento de águas pluviais.    
48
 3
	Parágrafo único. A legislação e as normas de regulação poderão considerar como esgotos sanitários também os efluentes industriais cujas características sejam semelhantes às do esgoto doméstico.  
49
 9
	Art. 11. A remuneração pela prestação de serviço público de esgotamento sanitário poderá ser fixada com base no volume de água cobrado pelo serviço de abastecimento de água.
50
 8
	Art. 12. Quando disponibilizada rede pública de esgotamento sanitário, o usuário estará sujeito aos pagamentos de taxas, tarifas e outros preços públicos decorrentes da disponibilização e da manutenção da infraestrutura e do uso desses serviços, mesmo que não tenha efetuado a conexão, nos termos do art. 45 da Lei nº 11.445, de 2007.
51
 6
	§ 1º Na hipótese em que houver inviabilidade técnico-construtiva da conexão, comprovada mediante laudo específico e circunstanciado, a edificação permanente urbana deverá adotar solução alternativa e descentralizada, individual ou coletiva, para a destinação dos efluentes.  
52
 10
	§ 2º No caso de adoção de soluções alternativas e descentralizadas, individual ou coletiva, deverão ser observadas as normas editadas pela entidade reguladora e pelos órgãos responsáveis pelas políticas ambientais, de saúde e de recursos hídricos.  
53
 6
	§ 3º O usuário deverá se conectar à rede pública, conforme estabelecido no § 5º do art. 45 da Lei nº 11.445, de 2007.  
54
 7
	§ 4º A entidade reguladora ou o titular dos serviços públicos de saneamento básico deverão estabelecer prazo para a conexão dos usuários à rede de esgotos nos termos do § 6º do art. 45 da Lei nº 11.445, de 2007.
55
 12
	§ 5º Após a conclusão de sua implantação, o prestador dos serviços notificará o usuário, por meio do aviso, a disponibilidade da rede pública de esgotamento sanitário, a viabilidade técnica e a obrigatoriedade de conexão no prazo estabelecido pela entidade reguladora ou pelo titular.
56
 8
	§ 6º O prestador dos serviços deverá informar a entidade regulada nos casos de inviabilidade técnica de conexão pelo usuário.
57
 8
	§ 7º Após realização da notificação disciplinada no § 5º do caput deste Decreto, findado o prazo estabelecido no § 4º do caput deste Decreto, caso não haja a conexão pelo usuário, o prestador dos serviços poderá realizar sua conexão e os valores decorrentes do serviço serão cobrados do usuário.
58
 8
	§ 8º A conexão a que se refere o § 7º do caput deste Decreto será realizada pelos prestadores dos serviços, observadas as condições técnicas necessárias, independentemente de autorização de seu proprietário, quando o sistema estiver disponível em área pública.
59
 4
	§ 9º Poderão ser adotados subsídios para viabilizar a conexão dos usuários de baixa renda, conforme definição em contrato ou em normativo da entidade reguladora.
60
 9
	§ 10. Mesmo que o usuário não tenha se conectado à rede pública de esgotamento sanitário, é assegurada a cobrança de um valor mínimo nos termos do § 4º do art. 45 da Lei nº 11.455, de 2007, ressalvados os casos do § 1º do caput deste Decreto.
61
 10
	§ 11. A entidade reguladora ou o titular dos serviços públicos de saneamento básico deverá definir, nos termos do § 5º do art. 45 da Lei nº 11.445, de 2007, os critérios para dispensa dos usuários de conectar-se à rede pública de esgotamento sanitário, quando da utilização de água de reúso.
62
 4
	§ 12. O prestador dos serviços fornecerá à entidade reguladora e ao titular dos serviços, sempre que solicitado, as informações atualizadas acerca do cadastro das redes de esgotamento sanitário disponíveis e das edificações a elas não conectadas, com a indicação dos respectivos responsáveis, nos termos do § 7º do art. 45 da Lei nº 11.455, de 2007.
Seção III

Dos Serviços Públicos de Manejo de Resíduos Sólidos Urbanos
63
 6
	Art. 13. Consideram-se serviços públicos de manejo de resíduos sólidos as atividades dispostas no art. 3º-C da Lei nº 11.445, de 2007.
64
 9
	Art. 14. Os resíduos sólidos originários de atividades comerciais, industriais e de serviços, se caracterizados como não perigosos, podem, em razão de sua natureza, composição ou volume, ser equiparados aos domiciliares pelo poder público municipal.  
65
 3
	§ 1º A limpeza de logradouros públicos e o gerenciamento dos resíduos gerados em decorrência da realização de eventos privados é de responsabilidade dos seus organizadores e promotores, os quais deverão arcar com os ônus decorrentes dessas atividades, observadas as normas definidas pelo titular dos serviços.
66
 5
	§ 2º O disposto no § 1º do caput deste Decreto não exclui a possibilidade da adoção de medidas administrativas para fazer cessar irregularidades, bem como a responsabilização civil no caso de dano ambiental e ao patrimônio público.
67
 11
	Art. 15. Admite-se a dispensa de licitação para a contratação de associações ou cooperativas formadas exclusivamente de pessoas físicas de baixa renda reconhecidas pelo poder público como catadores de materiais recicláveis na prestação dos serviços de limpeza pública e de manejo de resíduos, conforme inciso XXVII do art. 24 da Lei nº 8.666, de 21 de junho de 1993, e alinea j, inciso IV do art. 75 da Lei nº 14.133, de 1º de abril de 2021. 
68
 4
	Parágrafo único. As contratações de associações ou cooperativas de catadores deverão ser formalizadas de modo a permitir o monitoramento e a fiscalização pela entidade reguladora.
69
 12
	Art. 16. A remuneração pela prestação de serviço público de manejo de resíduos sólidos urbanos deverá levar em conta o disposto no art. 35 da Lei nº 11.445, de 2007, e, ainda, considerar mecanismos econômicos de incentivo à redução da geração de resíduos e à recuperação dos resíduos gerados.
Seção IV

Dos Serviços Públicos de Drenagem e Manejo de Águas Pluviais Urbanas
70
 6
	Art. 17. Consideram-se serviços públicos de manejo das águas pluviais urbanas aqueles especificados no art. 3º-D da Lei nº 11.445, de 2007.  
71
 10
	Art. 18. A cobrança pela prestação do serviço público de manejo das águas pluviais urbanas deve levar em conta o disposto no art. 36 da Lei nº 11.445, de 2007.
Seção V

Da Interrupção dos Serviços
72
 9
	Art. 19. A prestação de serviço público de saneamento básico deverá obedecer ao princípio da continuidade, podendo ser interrompida pelo prestador dos serviços nas hipóteses estabelecidas no art. 40 da Lei nº 11.445, de 2007.
CAPÍTULO II

DO EXERCÍCIO DA TITULARIDADE
73
 7
	Art. 20. O titular dos serviços formulará a respectiva política pública de saneamento básico nos termos do art. 9º da Lei nº 11.445, de 2007, devendo, para tanto, observar a ampla participação da população e de associações representativas dos vários segmentos da sociedade, como previsto no inciso II do art. 2º da Lei nº 10.257, de 2001.
74
 7
	Parágrafo único. Ao Sistema Único de Saúde - SUS, por meio de seus órgãos de direção e de controle social, compete participar da formulação da política e da execução das ações e serviços de saneamento básico, inclusive por intermédio dos planos de saneamento básico. 
CAPÍTULO III

DAS METAS DE UNIVERSALIZAÇÃO
75
 3
	Art. 21. Para o cumprimento das metas de universalização, deverão ser observados os prazos previstos no art. 11-B da Lei nº 11.445, de 2007.
76
 4
	§ 1º As metas a que se refere o art. 11-B da Lei nº 11.445, de 2007, aplicam-se:
77
 6
	I - tanto à população urbana quanto à rural, contabilizadas separadamente;
78
 4
	II - à toda modalidade de prestação de serviço público de saneamento básico, devendo o titular dos serviços buscar alternativas para atingir as metas de universalização para a totalidade de sua população, independentemente da existência de contrato.
79
 5
	§ 2º As metas de redução de perdas, não intermitência e qualidade dos processos de tratamento previstas no caput do art. 11-B da Lei nº 11.445, de 2007, devem ser estabelecidas pelo titular ou entidade reguladora.
80
 2
	§ 3º Para fins de cumprimento das metas de universalização previstas no caput do art. 11-B da Lei nº 11.445, de 2007:
81
 10
	I - no caso de disponibilização de rede de abastecimento de água ou de esgotamento sanitário, será considerada a efetiva conexão dos domicílios;
82
 5
	II - no caso de atendimento por soluções alternativas e descentralizadas, individual ou coletiva, na forma do § 4º do art. 11-B e do § 1º do art. 45 da Lei nº 11.445, de 2007, quando cumprirem os seguintes requisitos mínimos:
83
 3
	a) para o caso do abastecimento de água potável, na situação em que a água consumida se originar em poço, nascente ou cisterna desde que canalizada até pelo menos um cômodo do domicílio com canalização interna, em qualquer caso sem intermitências; e  
84
 7
	b) para o caso do esgotamento sanitário, na situação de uso de fossas sépticas, tanques sépticos ou outras soluções de tratamento ou destinação adequados, conforme normas e requisitos técnicos, seguidos de unidades complementares, quando couber. 
85
 2
	III - deverão ser atendidas as metas de redução de perdas, não intermitência e qualidade dos processos de tratamento, nos termos do § 2º do caput deste Decreto.
86
 4
	§ 4º Os requisitos mínimos a que se referem as alíneas a e b do inciso II do § 3º do caput deste Decreto poderão ser complementados por norma editada pela entidade reguladora competente, bem como pelos órgãos responsáveis pelas políticas ambiental, sanitária e de recursos hídricos.
87
 5
	§ 5º A ANA poderá elaborar norma de referência para complementar os requisitos mínimos de que trata do § 4º do caput deste Decreto.
88
 5
	§ 6º Caberá às agências reguladoras regulamentar e fiscalizar a operação dos serviços de saneamento básico nos casos da utilização de soluções alternativas e descentralizadas, individual ou coletiva.
89
 7
	§ 7º A meta de universalização que garanta o atendimento de 90% (noventa por cento) da população com coleta e tratamento a que se refere o caput do art. 11-B da Lei nº 11.445, de 2007, deverá considerar que 100% do esgoto coletado seja tratado.
90
 11
	§ 8º A dilação de prazo a que se refere o § 9º do art. 11-B da Lei nº 11.445, de 2007, poderá ser aplicada aos municípios isoladamente, caso:
91
 4
	I - os contratos de concessão ou de parcerias público-privadas precedidos de licitação tenham sido firmados anteriormente à data de publicação deste Decreto;
92
 8
	II - a concessão ou parceria público-privada já tenha sido licitada, tenha sido submetida à consulta pública ou que seja objeto de estudos já contratados pelas instituições financeiras federais; ou
93
 7
	III - a prestação do serviço tenha como objetivo atender as áreas rurais.
94
 5
	§ 9º A agência reguladora competente deverá estabelecer em até 2 (dois) anos, a partir da publicação deste Decreto, as metas progressivas para a substituição do sistema unitário pelo sistema separador absoluto de que trata o § 3º do art. 44 da Lei nº 11.445, de 2007, observados os planos de saneamento básico.
95
 3
	§ 10. Enquanto estiver em vigência a transição estabelecida pelo § 3º do art. 44 da Lei nº 11.445, de 2007, os sistemas unitários serão considerados para cálculo da meta de universalização.
96
 3
	Art. 22. Deverão ser definidas metas progressivas e graduais de universalização, observadas as especificidades locais e regionais, que terão o cumprimento verificado pela entidade reguladora.
CAPÍTULO IV

DO PLANEJAMENTO
97
 4
	Art. 23. O processo de planejamento do saneamento básico envolve:  
98
 0
	I - o Plano Nacional de Saneamento Básico (Plansab), elaborado pela União;
99
 0
	II - os planos regionais de saneamento básico, elaborados pela União nos termos do inciso II do art. 52 da Lei nº 11.445, de 2007;
100
 0
	III - os planos regionais de saneamento básico, elaborados pelos titulares participantes de prestação de serviço regionalizada; e
101
 5
	IV - os planos municipais de saneamento básico elaborados pelos titulares.    
102
 1
	§ 1º O planejamento dos serviços públicos de saneamento básico atenderá ao princípio da solidariedade entre os entes da Federação, podendo desenvolver-se mediante cooperação federativa.  
103
 1
	§ 2º O plano regional poderá englobar apenas parte do território do Estado da Federação que o elaborar, nos termos do § 8º do art. 19 da Lei nº 11.445, de 2007.    
104
 2
	§ 3º No que se refere o § 2º do caput deste Decreto, para fins de monitoramento do plano regional, a geração de dados e informações deverá englobar a parcela territorial abrangida.    
105
 5
	Art. 24. A prestação de serviço público de saneamento básico observará plano aprovado pelo titular, que atenderá ao disposto no art. 19 da Lei nº 11.445, de 2007.
106
 2
	§ 1º O plano de saneamento básico, ou o eventual plano específico, poderá ser elaborado mediante apoio técnico ou financeiro prestado por outros entes da Federação, pelo prestador dos serviços ou por instituições universitárias ou de pesquisa científica, garantida a participação dos titulares dos serviços, dos órgãos governamentais, dos usuários, das entidades técnicas e de organizações da sociedade civil e de defesa do consumidor relacionadas ao setor saneamento, conforme art. 47 da Lei nº 11.445, de 2007.
107
 3
	§ 2º Os indicadores utilizados nos planos de saneamento básico devem ter como base os do Plansab, do Sistema Nacional de Informações em Saneamento Básico (Sinisa) e os definidos pela ANA nas normas de referência.
108
 4
	§ 3º Os planos de saneamento básico, no componente de resíduos sólidos urbanos, deverão conter prescrições para manejo dos resíduos da construção civil e de serviços de saúde.  
109
 2
	§ 4º Os planos de saneamento básico poderão contemplar todo o conteúdo mínimo dos planos municipais ou intermunicipais de gestão integrada de resíduos sólidos previsto no art. 19 da Lei nº 12.305, de 02 de agosto de 2010.
110
 3
	Art. 25. O processo de elaboração e revisão dos planos de saneamento básico deverá efetivar-se, de forma a garantir a ampla participação das comunidades, dos movimentos e das entidades da sociedade civil e deverá prever sua divulgação em conjunto com os estudos que os fundamentarem, observado o disposto no art. 51 da Lei nº 11.445, de 2007.
111
 9
	Parágrafo único. Após 31 de dezembro de 2024, a existência de plano de saneamento básico com anuência do titular dos serviços será condição para o acesso aos recursos orçamentários da União ou aos recursos de financiamentos geridos ou administrados por órgão ou entidade da administração pública federal, quando destinados a serviços de saneamento básico.
112
 4
	Art. 26. Compete aos titulares de serviços públicos de saneamento básico:
113
 1
	I - manter seus planos atualizados e acessíveis em sítio eletrônico para consulta da sociedade civil, em conformidade com a Lei nº 12.527, de 18 de novembro de 2011, de Acesso à Informação;
114
 3
	II - comunicar à ANA a existência do plano; e
115
 11
	III - disponibilizar ao Sinisa informações atualizadas sobre a existência e/ou contidas no plano, conforme métodos, procedimentos e periodicidade do referido sistema.
116
 2
	Art. 27. Para cumprir o determinado no § 1º do art. 17 da Lei nº 11.445, de 2007, o plano regional deve conter metas de abrangência regional.
117
 4
	§ 1º O plano regional de saneamento básico se sobreporá aos planos municipais nos componentes do saneamento básico abordados paralelamente;
118
 3
	§ 2º O plano regional poderá ser complementar ao plano municipal e vice-versa, em termos de componentes do saneamento básico abrangidos, contanto que, ao final, todos os componentes do saneamento básico sejam abrangidos nos diferentes planos.
119
 3
	Art. 28. Os Municípios com população inferior a 20.000 (vinte mil) habitantes poderão apresentar planos simplificados, com menor nível de detalhamento, conforme previsto no § 9º do art. 19 da Lei nº 11.445, de 2007, abrangendo, no mínimo:  
120
 1
	I - diagnóstico situacional, com foco no dimensionamento do déficit de acesso aos serviços de saneamento básico, com o estabelecimento de indicadores e nas variáveis ambientais que contribuem ou dificultam esse acesso;  
121
 0
	II - estabelecimento de metas de universalização do acesso aos serviços acompanhadas de metas intermediárias anuais;  
122
 2
	III - programas, projetos, ações e investimentos necessários para atingir as metas estabelecidas, identificando possíveis fontes de financiamento;  
123
 1
	IV - ações para emergências e contingências; e
124
 0
	V - mecanismos de avaliação e monitoramento do plano.
125
 4
	Art. 29. O disposto no plano de saneamento básico é vinculante para o Poder Público que o elaborou e para os prestadores de serviço público de saneamento básico, conforme art. 19 da Lei nº 11.445, de 2007, observadas as demais disposições deste artigo.
126
 7
	§ 1º No caso de serviços prestados mediante delegação, eventuais divergências entre o plano de saneamento básico que foi usado como referência para a contratação e a realidade, verificadas após o início da prestação dos serviços, deverão ser consideradas na revisão contratual que vier a se proceder, assegurado o direito à manutenção do equilíbrio econômico-financeiro do contrato, se for o caso, em conformidade com as regras do edital e as normas da entidade reguladora.
127
 1
	§ 2º As alterações do plano de saneamento básico realizadas posteriormente à delegação dos serviços somente terão eficácia com relação ao delegatário depois de incluídas por meio de aditamento contratual, em comum acordo com a contratada e sempre mediante a preservação concomitante do equilíbrio econômico-financeiro.
128
 7
	§ 3º O plano deverá identificar as situações em que não haja capacidade de pagamento dos usuários e indicar solução para atingimento das metas previstas, inclusive as metas progressivas de qualidade dos efluentes.
CAPÍTULO V

DA REGULAÇÃO

Seção I

Da Função e dos Objetivos da Regulação
129
 1
	Art. 30. A regulação atenderá à função e aos objetivos dispostos, respectivamente, nos arts. 21 e 22 da Lei nº 11.445, de 2007.
Seção II

Das Normas de Regulação
130
 7
	Art. 31. Cada um dos serviços públicos de saneamento básico deverá ser regulado e pode possuir regulação concomitante ou específica.  
131
 5
	Art. 32. As normas de regulação dos serviços serão editadas:    
132
 0
	I - por legislação do titular, no que se refere:  
133
 2
	a) aos direitos e obrigações dos usuários e prestadores dos serviços, bem como às penalidades a que estarão sujeitos; e
134
 1
	b) aos procedimentos e critérios para a atuação das entidades de regulação e de fiscalização;
135
 1
	II - por norma da entidade de regulação, no que se refere às dimensões técnica, econômica, financeira, contábil e social de prestação dos serviços, observado o disposto no art. 23 da Lei nº 11.445, de 2007.
136
 3
	Art. 33. Diante da ausência de regras contratuais na prestação direta pela Administração Pública, competirá ao ente regulador, através de norma específica, respeitadas as normas e legislação do titular sobre a matéria, e em consonância com as normas de referência emitidas pela ANA, disciplinar condições gerais para a regulação e fiscalização dos serviços, baseados em indicadores e metas de desempenho em conformidade com os planos de saneamento básico.    
137
 2
	Art. 34. As regras sancionatórias aplicáveis à prestação direta pela Administração Pública serão definidas pelo ente regulador, através de norma específica e em consonância com as normas de referência emitidas pela ANA.
Seção III

Dos Órgãos e das Entidades de Regulação
138
 9
	Art. 35. As atividades administrativas de fiscalização e de regulação dos serviços de saneamento básico deverão ser realizadas por meio de entidade de natureza autárquica dotada de independência decisória e autonomia administrativa, orçamentária e financeira, podendo ser executadas pelo titular:  
139
 2
	I - diretamente, inclusive mediante consórcio público do qual participe; ou    
140
 5
	II - mediante delegação, por meio de convênio de cooperação, a órgão ou entidade de outro ente da Federação ou a consórcio público do qual não participe, instituído para gestão associada de serviços públicos, nos moldes dos §§ 1º e 1º-A do art. 23 da Lei nº 11.445, de 2007.
141
 1
	§ 1º Nos casos de prestação regionalizada dos serviços de saneamento básico, os titulares poderão adotar os mesmos critérios econômicos, sociais e técnicos da regulação em toda área de abrangência do conjunto de municípios, conforme art. 24 da Lei nº 11.445, de 2007.
142
 5
	§ 2º Quando da prestação regionalizada, as decisões sobre a modalidade de execução das atividades administrativas de fiscalização e regulação dos serviços, se direta ou delegada, deverão ser discutidas de forma colegiada, por meio da instância de governança da estrutura de prestação regionalizada, nos termos do art. 7º-A da Lei nº 13.089, de 12 de janeiro de 2015, do Estatuto da Metrópole. 
143
 10
	Art. 36. Compete ao titular dos serviços públicos de saneamento básico definir a entidade responsável pela regulação e fiscalização dos serviços, conforme disposto no § 5º do art. 8º da Lei nº 11.445, de 2007.
144
 10
	Parágrafo único. É permitida a atuação de mais de uma entidade reguladora no âmbito do município, exceto na hipótese dos componentes de abastecimento de água potável, esgotamento sanitário e manejo de águas pluviais, que são atividades complementares e interdependentes, observadas as estruturas de prestação regionalizada de serviços de saneamento básico. 
145
 5
	Art. 37. Na hipótese em que houver mais de uma entidade reguladora dentro de uma mesma área de prestação regionalizada dos serviços, estas deverão celebrar termo de convênio/cooperação para uniformizar a regulação e a fiscalização dos serviços públicos cujas competências sejam-lhes comuns.    
146
 4
	§ 1º O termo a ser celebrado entre as entidades reguladoras a que se refere o caput deste Decreto deverá conter cláusulas que estabeleçam pelo menos:  
147
 1
	I - as normas relativas às dimensões técnica, econômica, financeira e social dos serviços prestados, incluindo as que disciplinem os contratos, que serão editadas conjuntamente;    
148
 1
	II - a estipulação conjunta de parâmetros, critérios, fórmulas, padrões ou indicadores de mensuração e aferição da qualidade dos serviços e do desempenho dos prestadores dos serviços;
149
 0
	III - a delimitação das áreas e dos componentes dos serviços públicos de saneamento básico que serão objeto de fiscalização, direta ou indireta, por cada uma das entidades, de forma isolada ou comum, considerada a possibilidade da aplicação de sanções;
150
 0
	IV - os critérios para a definição da entidade reguladora competente para a solução das solicitações e reclamações recebidas dos usuários, assegurado o redirecionamento automático na hipótese em que a solicitação ou a reclamação for dirigida a entidade incompetente;    
151
 1
	V - a definição dos dados a serem requeridos dos prestadores dos serviços e a periodicidade de seus fornecimentos para fins de alimentação das bases de dados do sistema de informações e o acompanhamento da evolução da prestação dos serviços; e
152
 1
	VI - a forma de atuação conjunta para o acompanhamento das metas progressivas de expansão e de qualidade dos serviços e os respectivos prazos.
153
 3
	§ 2º Eventuais conflitos regulatórios resultantes da delegação de mais de uma entidade reguladora dentro de uma mesma área de prestação regionalizada dos serviços poderão ser submetidos a mediação ou arbitramento pela ANA, nos termos do disposto no § 5º do art. 4º-A da Lei nº 9.984, de 17 de julho de 2000.
Seção IV

Da Publicidade dos Atos de Regulação
154
 7
	Art. 38. A publicidade dos relatórios, estudos, decisões e instrumentos que se refiram à regulação dos serviços de saneamento básico deverá ser assegurada observado o disposto no art. 26 da Lei nº 11.445, de 2007.
Seção V

Da Verificação do Cumprimento dos Planos de Saneamento Básico
155
 4
	Art. 39. Incumbe à entidade reguladora e fiscalizadora dos serviços a verificação do cumprimento dos planos de saneamento básico por parte dos prestadores dos serviços, conforme disposto no parágrafo único do art. 20 da Lei nº 11.445, de 2007.
156
 3
	§ 1º O ciclo de verificação do cumprimento dos planos de saneamento básico por parte das entidades reguladoras deverá ser realizado, no mínimo, a cada dois anos, dando ampla publicidade aos relatórios gerados.    
157
 1
	§ 2º O relatório de verificação do cumprimento do plano de saneamento básico deverá ser encaminhado ao titular dos serviços e, quando se tratar de plano regional, à entidade de governança interfederativa.  
CAPÍTULO VI

DO CONTROLE SOCIAL
158
 8
	Art. 40. O controle social dos serviços públicos de saneamento básico deverá ser instituído pelo titular dos serviços mediante adoção de pelo menos um dos seguintes mecanismos, sem o prejuízo de outras formas complementares de controle:    
159
 0
	I - audiências públicas;    
160
 0
	II - consultas públicas;  
161
 0
	III - conferências das cidades; ou
162
 4
	IV - órgãos colegiados de caráter consultivo na formulação da política de saneamento básico, bem como no seu planejamento e avaliação ? resguardados, em sua composição, os representantes mencionados nos incisos I a V do art. 47 da Lei nº 11.445, de 2007.
163
 4
	§ 1º As audiências públicas mencionadas no inciso I do caput deste Decreto devem se realizar de modo a possibilitar a participação da população, podendo ser realizadas de forma regionalizada.    
164
 3
	§ 2º As consultas públicas devem ser promovidas de modo a permitir ampla participação social, com críticas e sugestões às propostas do Poder Público, garantida a divulgação posterior de seus resultados e a adequada resposta às contribuições recebidas.
165
 2
	§ 3º É assegurado aos órgãos colegiados de controle social o acesso, mediante solicitação formal, a quaisquer documentos e informações produzidos por órgãos ou entidades de regulação ou de fiscalização, nos termos do art. 26 da Lei nº 11.455, de 2007, e considerando, ainda, o previsto na Lei nº 12.527, de 2011.
166
 10
	§ 4º É vedado o acesso aos recursos federais ou aos geridos ou administrados por órgão ou entidade da União, quando destinados a serviços de saneamento básico, àqueles responsáveis pelo pleito nos municípios cujos titulares de serviços públicos de saneamento básico que não tenham instituído, por meio de legislação específica, o controle social realizado por órgão colegiado, nos termos do inciso IV do caput deste Decreto.
167
 3
	Art. 41. Os Estados, a União e as estruturas de prestação regionalizadas poderão adotar os instrumentos de controle social previstos no art. 40 deste Decreto.
168
 0
	Parágrafo único. A delegação do exercício de competências não prejudicará o controle social sobre as atividades delegadas ou a elas conexas.
CAPÍTULO VII

DA PRESTAÇÃO DOS SERVIÇOS

Seção I

Da Prestação Mediante Contrato
169
 9
	Art. 42.  Os contratos de prestação dos serviços públicos de saneamento básico deverão obedecer ao disposto nos arts. 10, 10-A, 10-B, 11, 11-A e 11-B da Lei nº 11.445, de 2007.
170
 11
	Art. 43. As minutas de edital e do contrato de concessão e os estudos de viabilidade econômico-financeira deverão ser avaliados previamente pela entidade de regulação competente antes de sua submissão à audiência e consulta pública de que trata o inciso IV do art. 11 da Lei nº 11.445, de 2007.
171
 8
	Parágrafo único. A entidade reguladora, quando da avaliação dos documentos de que trata o caput, deverá se manifestar sobre as questões técnicas, econômicas e sociais de sua competência no prazo de 60 (sessenta) dias corridos após a comunicação oficial, podendo ser prorrogado por 30 (trinta) em caso de solicitação da entidade reguladora.
Seção II

Das Condições de Validade dos Contratos
172
 2
	Art. 44. Os contratos que tenham por objeto a prestação de serviço público de saneamento básico deverão seguir as condições de validade dispostas no art. 11 da Lei nº 11.445, de 2007.
173
 10
	§ 1º O estudo de viabilidade técnica e econômico-financeira para estruturação de processos de concessões dos serviços de saneamento básico poderá ser elaborado nos moldes estabelecidos por regulamento em ato do Ministro das Cidades. 
174
 4
	§ 2º O disposto no caput deste Decreto não se aplica aos contratos celebrados com fundamento no inciso IV do art. 24 da Lei nº 8.666, de 1993, e do inciso VIII do art. 75 da Lei nº 14.133, de 2021, cujo objeto seja a prestação de qualquer dos serviços de saneamento básico.
CAPÍTULO VIII

DOS ASPECTOS ECONÔMICOS E FINANCEIROS

Seção I

Da Remuneração pelos Serviços
175
 8
	Art. 45. Os serviços públicos de saneamento básico terão a sustentabilidade econômico-financeira assegurada por meio de remuneração pela cobrança dos serviços, devendo ser observados o disposto nos arts. 29 a 41 da Lei nº 11.445, de 2007, para a instituição de tarifas, preços públicos, taxas e subsídios.
176
 14
	Art. 46. Poderão ser adotados subsídios tarifários e não tarifários para os usuários que não tenham capacidade de pagamento suficiente para cobrir o custo integral dos serviços, conforme disposto no § 2º do art. 29 da Lei nº 11.445, de 2007.
177
 5
	§ 1º Respeitadas as normas e a legislação do titular sobre a matéria, e em consonância com as normas de referência emitidas pela ANA, a cobrança pelos serviços voltada para a população de baixa renda deverá ser estabelecida por meio do emprego de tarifa social para os usuários incluídos na lista do Cadastro Único para Programas Sociais do Governo Federal (CadÚnico).
178
 5
	§ 2º Na falta da lista do Cadastro Único a que se refere o § 1º do caput deste Decreto, poderá ser utilizada lista oficial do Município contendo as famílias em situação de pobreza ou de extrema pobreza.
179
 3
	Art. 47. Nos termos do § 4º do art. 29 da Lei nº 11.445, de 2007, na hipótese de prestação de serviço público de saneamento básico sob regime de concessão, as tarifas e preços públicos serão arrecadados pelo prestador dos serviços diretamente do usuário, e essa arrecadação será facultativa em caso de taxas.
180
 2
	§ 1º O disposto no caput deste Decreto aplica-se:    
181
 0
	I ? às concessões de serviços públicos de saneamento básico regidas pela Lei nº 8.987, de 13 de fevereiro de 1995; e
182
 0
	II ? às concessões de serviços públicos de saneamento básico na modalidade patrocinada, regidas pela Lei nº 11.079, de 30 de dezembro de 2004.    
183
 0
	§ 2º Na hipótese de prestação dos serviços sob regime de concessão na modalidade administrativa, regida pela Lei nº 11.079, de 2004, é facultado ao titular a escolha pela modalidade de cobrança pelos serviços públicos de saneamento básico, incluindo taxas, tarifas e outros preços públicos.  
184
 1
	Art. 48. A ocorrência, magnitude e definição dos subsídios não tarifários deverá vincular-se ao benefício de usuários e localidades que não tenham capacidade de pagamento ou escala econômica suficiente para cobrir o custo integral dos serviços.    
185
 4
	Parágrafo único. Na hipótese de introdução de novo instrumento de cobrança a partir da vigência deste Decreto, caso haja proposição de subsídios não tarifários, o titular dos serviços deverá apresentar ao ente regulador estudos que comprovem atendimento ao caput deste Decreto, observadas as normas de regulação editadas pela entidade reguladora.
186
 7
	Art. 49. O documento de cobrança relativo à remuneração pela prestação de serviço público de saneamento básico ao usuário final deverá:    
187
 1
	I - explicitar itens e custos dos serviços, de forma a permitir o seu controle direto pelo usuário final na forma do parágrafo único do art. 39 da Lei nº 11.445, de 2007; e  
188
 2
	II - conter informações mensais sobre a qualidade da água entregue aos consumidores, em cumprimento ao inciso I do art. 5º do Anexo do Decreto nº 5.440, de 4 de maio de 2005.  
CAPÍTULO IX

DA RELAÇÃO DOS SERVIÇOS PÚBLICOS DE SANEAMENTO BÁSICO COM OS RECURSOS HÍDRICOS
189
 4
	Art. 50. A utilização dos recursos hídricos deve observar o disposto no art. 4º da Lei nº 11.445, de 2007.
190
 0
	Parágrafo único. A prestação de serviço público de saneamento básico deverá ser realizada com base no uso sustentável dos recursos hídricos.
191
 5
	Art. 51. O tratamento de esgotos deve ter nível suficiente para atender às normas de lançamento de efluentes, aos padrões das classes dos corpos hídrico e critérios e valores orientadores de qualidade do solo, na forma do § 2º do art. 44 da Lei nº 11.445, de 2007.
192
 4
	Art. 52. O Conselho Nacional de Meio Ambiente e o Conselho Nacional de Recursos Hídricos editarão, no âmbito de suas respectivas competências, normas para o cumprimento do disposto no art. 44 da Lei nº 11.445, de 2007, para a definição dos requisitos de eficácia e eficiência a fim de alcançar progressivamente os padrões estabelecidos pela legislação ambiental, e para o estabelecimento de metas progressivas de qualidade dos efluentes de unidades de tratamento de esgotos sanitários para que atenda aos padrões das classes dos corpos hídricos em que forem lançados.
193
 3
	Parágrafo único. Os prestadores dos serviços deverão prestar informações sobre a eficácia e eficiência das unidades de tratamento de esgotos sanitários no Sinisa.
194
 1
	Art. 53. Na situação prevista no art. 46 da Lei nº 11.445, de 2007, a tarifa de contingência, caso adotada, incidirá, preferencialmente, sobre os consumidores que ultrapassarem os limites definidos no racionamento.    
TÍTULO III

DA POLÍTICA FEDERAL DE SANEAMENTO BÁSICO

CAPÍTULO I

DAS DIRETRIZES E DOS OBJETIVOS
195
 3
	Art. 54. A Política Federal de Saneamento Básico é o conjunto de planos, programas, projetos e ações promovidos por órgãos e entidades federais, isoladamente ou em cooperação com outros entes da Federação, ou com particulares, de forma a cumprir com as diretrizes e os objetivos definidos nos arts. 48 e 49 da Lei nº 11.445, de 2007.
CAPÍTULO II

DOS PLANOS DE SANEAMENTO BÁSICO DA UNIÃO

Seção I

Das Disposições Gerais
196
 3
	Art. 55. A União elaborará, sob a coordenação do Ministério das Cidades:  
197
 0
	I - o Plano Nacional de Saneamento Básico - Plansab; e  
198
 0
	II - os planos regionais de saneamento básico, elaborados e executados em articulação com os Estados, Distrito Federal e Municípios envolvidos para as regiões integradas de desenvolvimento econômico ou nas que haja a participação de órgão ou entidade federal na prestação de serviço público de saneamento básico.
199
 1
	§ 1º Os planos mencionados no caput deste Decreto:  
200
 0
	I - serão elaborados sempre com horizonte de vinte anos;  
201
 0
	II - serão avaliados anualmente;  
202
 0
	III - serão revisados a cada quatro anos, até o final do primeiro trimestre do ano de elaboração do plano plurianual da União; e    
203
 5
	IV - deverão ser compatíveis com as disposições dos planos de recursos hídricos, inclusive o Plano Nacional de Recursos Hídricos e planos de bacias.    
204
 0
	§ 2º Os órgãos e entidades federais cooperarão com os titulares ou consórcios por eles constituídos na elaboração dos planos de saneamento básico.
205
 0
	§ 3º Excepcionalmente, o período de revisão do Plansab poderá ser ajustado em função da ocorrência dos censos demográficos do IBGE, para inclusão e aproveitamento de seus dados.
Seção II

Do Plano Nacional de Saneamento Básico (Plansab)
206
 3
	Art. 56. O Plansab será elaborado e revisado mediante procedimento com as seguintes fases:    
207
 0
	I - diagnóstico;  
208
 0
	II - formulação de proposta;  
209
 0
	III - divulgação e debates;  
210
 5
	IV - apreciação pelos Conselhos Nacionais de Saúde, Meio Ambiente, Recursos Hídricos;    
211
 0
	V - apreciação e deliberação pelo Comitê Interministerial do Saneamento Básico (Cisb);    
212
 0
	VI - encaminhamento do decreto de aprovação do Plano ou de sua revisão para publicação, nos termos da legislação; e  
213
 1
	VII - avaliação dos resultados e impactos de sua implementação. 
214
 2
	Art. 57. A proposta de plano ou de sua revisão deverá ser divulgada e debatida por meio de audiências públicas ou de consulta pública, e dos conselhos nacionais, além de outros meios à disposição do poder público.  
215
 1
	§ 1° A realização das audiências públicas e da consulta pública será disciplinada por instrução do Ministério das Cidades.
216
 4
	§ 2° A apreciação pelos conselhos nacionais será simultânea, e deverá ser realizada no prazo máximo de sessenta dias corridos dias a partir do seu recebimento oficial, ao fim dos quais será considerada concluída. 
217
 0
	§ 3° Os resultados da consulta pública, das audiências públicas e da apreciação pelos conselhos nacionais deverão ser publicados integralmente na internet.  
218
 0
	§ 4° As alterações sugeridas poderão ser incorporadas à proposta, ressalvados os casos que comprometam a coerência e viabilidade técnica.  
219
 4
	§ 5° O Conselho das Cidades poderá solicitar a proposta para apreciação observado o prazo disposto no §2° do caput deste Decreto.
220
 2
	§ 6º Decorrido o prazo mencionado no §2° do caput deste Decreto, a proposta será submetida ao Cisb para apreciação e deliberação.  
221
 0
	Art. 58. Após apreciação e deliberação pelo Cisb, a proposta de decreto será encaminhada nos termos da legislação.  
222
 0
	Art. 59. O Plansab deverá ser avaliado anualmente pelo Ministério das Cidades em relação ao cumprimento dos objetivos e metas estabelecidos, dos resultados esperados e dos impactos verificados.
223
 1
	§ 1º A avaliação a que se refere o caput deste Decreto deverá ser feita com base nos indicadores de monitoramento, de resultado e de impacto previstos nos próprios planos.  
224
 0
	§ 2º A avaliação integrará o diagnóstico e servirá de base para o processo de formulação de proposta de plano para o período subsequente.
Seção III

Dos Planos Regionais de Responsabilidade da União
225
 0
	Art. 60.  A União elaborará, em articulação com os Estados, Distrito Federal e Municípios envolvidos, os planos regionais de saneamento básico para:   
226
 0
	I - as regiões integradas de desenvolvimento econômico; e  
227
 0
	II - as regiões em que haja a participação de órgão ou entidade federal na prestação de serviço público de saneamento básico.    
228
 0
	§ 1º Os planos regionais de saneamento básico de responsabilidade da União atenderão, no que couber, aos mesmos procedimentos previstos para o Plansab, conforme disciplinado no art. 56 deste Decreto.
229
 1
	§ 2º A proposta de plano regional de saneamento básico será aprovada por todos os entes da Federação diretamente envolvidos, após prévia oitiva de seus respectivos conselhos de meio ambiente, de saúde e de recursos hídricos. 
CAPÍTULO III

DO SISTEMA NACIONAL DE INFORMAÇÕES EM SANEAMENTO BÁSICO - SINISA
230
 0
	Art. 61. São objetivos do Sinisa aqueles dispostos no art. 53 da Lei nº 11.445, de 2007.
231
 1
	Art. 62. São objetivos específicos do Sinisa:
232
 2
	I - auxiliar no planejamento e execução das políticas públicas de saneamento básico, urbana e rural, permitindo a identificação, quantificação, qualificação, organização e orientação das ações (públicas e privadas) da prestação dos serviços de forma adequada;
233
 1
	II - subsidiar a aplicação de recursos, apresentando a situação do saneamento básico nos municípios brasileiros;
234
 0
	III - subsidiar a avaliação de desempenho da prestação dos serviços, possibilitando a comparação entre os dados dos diversos prestadores dos serviços;
235
 1
	IV - contribuir para o aperfeiçoamento da gestão dos serviços de saneamento básico, a partir da avaliação dos níveis de eficiência e eficácia;  
236
 0
	V - assistir às atividades regulatórias e de fiscalização, com dados que subsidiam a elaboração de normas e metodologia de cálculo de indicadores;
237
 0
	VI - subsidiar o controle social, permitindo aos usuários acesso facilitado ao conjunto de dados de saneamento básico no país; e
238
 3
	VII - possibilitar o monitoramento e a avaliação dos resultados dos planos e das ações e serviços de saneamento básico.
239
 6
	§ 1º O Sinisa poderá incorporar indicadores de monitoramento, de resultados e de impacto integrantes do Plansab e dos planos regionais, de que trata o art. 55 deste Decreto.
240
 0
	§ 2º O Sinisa deve incorporar e implementar progressivamente informações e indicadores para as áreas urbana e rural.
241
 0
	§ 3º Nos termos do § 7º do art. 53 da Lei nº 11.455, de 2007, os titulares, os prestadores de serviço público de saneamento básico e as entidades reguladoras fornecerão as informações a que lhe competem, conforme critérios, métodos e periodicidade estabelecidos pelo Sinisa.
242
 3
	Art. 63. Para cumprimento dos objetivos do Sinisa, o Ministério das Cidades deverá:  
243
 0
	I - manter a base de dados atualizada na internet, com acesso público e gratuito, possibilitando consulta à série histórica das informações coletadas e indicadores gerados pelo sistema;  
244
 1
	II - coletar anualmente dados dos titulares, prestadores ou entidades reguladoras dos serviços públicos de saneamento básico; e
245
 2
	III - permitir visualização às entidades reguladoras das informações preenchidas pelos prestadores dos serviços regulados, durante o período de coleta de informações até a publicação anual dos dados.
246
 2
	§ 1º As normas, as portarias, os planos e os demais instrumentos regulatórios para o setor saneamento básico deverão ser fundamentados e utilizar, prioritariamente, a base de dados do Sinisa.  
247
 0
	§ 2º A implantação do Sinisa poderá se dar de forma progressiva, por módulos, de acordo com a evolução do sistema.
248
 2
	§ 3º O Sinisa poderá coletar dados de outras fontes além das mencionados no inciso II do caput deste Decreto.
249
 2
	Art. 64. As entidades reguladoras deverão auditar as informações fornecidas ao Sinisa pelos prestadores dos serviços por elas regulados, de acordo com mecanismo sistemático de auditoria definido em ato do Ministro das Cidades, nos termos do § 6º do art. 53 da Lei nº 11.445, de 2007.
250
 0
	§ 1º A auditoria dos dados do Sinisa deverá ocorrer em todos os anos de referência e poderá adotar soluções graduais e progressivas para sua implementação.
251
 1
	§ 2º A auditoria dos dados do Sinisa poderá ser realizada posteriormente à publicação dos dados pelo Sinisa nos primeiros 5 (cinco) anos após a publicação do presente Decreto.
252
 1
	§ 3º A partir do sexto ano posterior à publicação do presente Decreto a auditoria dos dados deverá ser feita previamente à publicação dos dados pelo Sinisa.
253
 1
	§ 4º A auditoria dos dados deverá ser feita para cada município operado pelo prestador dos serviços e, quando a prestação dos serviços for regionalizada, também para o bloco regional.
254
 3
	§ 5º Para fins da auditoria mencionada no caput deste Decreto, nos termos do art. 25 da Lei nº 11.445, de 2007, os prestadores públicos e privados de serviço público de saneamento básico deverão permitir ao titular ou entidade reguladora o acesso, quando solicitado, aos equipamentos, instalações e registros contábeis, financeiros, administrativos, de pessoal, comercial ou quaisquer outras informações de uso na operação, administração ou manutenção dos sistemas de saneamento básico, mesmo que o prestador já possua auditoria interna ou externa.
255
 0
	§ 6º Toda e qualquer informação cedida pelo prestador dos serviços para efeitos de auditoria devem estar resguardadas de divulgação pelos titulares e entidades reguladoras por meio de termo de confidencialidade, a fim de cumprir o instituto legal do segredo empresarial, industrial ou comercial, além dos dispositivos previstos na Lei Geral de Proteção a Dados, instituída pela Lei nº 13.709, de 14 de agosto de 2018.
256
 0
	§ 7º A entidade reguladora deverá dar ampla publicidade ao resultado da auditoria, informando o resultado para cada informação e indicador auditados.
257
 2
	Art. 65. Será disponibilizado anualmente uma Certidão de Regularidade ao Sinisa, sempre que os dados forem fornecidos e auditados dentro do prazo estabelecido no calendário anual do Sinisa.
258
 0
	§ 1º Na ocorrência de informações inconsistentes não justificadas no preenchimento dos formulários e esgotadas as possibilidades de revisão, conforme critérios, métodos e periodicidade estabelecidos pelo Ministério das Cidades, haverá o cancelamento dos respectivos formulários.
259
 1
	§ 2º Ocorrendo o cancelamento mencionado no § 1º do caput deste Decreto, o prestador dos serviços e o titular tornam-se inadimplentes com o fornecimento dos dados no município, na modalidade e no ano de referência a que se refere o cancelamento. 
260
 1
	§ 3º Quando se tratar de informações fornecidas pela entidade reguladora, ocorrendo o cancelamento mencionado no § 1º do caput deste Decreto, a entidade reguladora e o titular tornam-se inadimplentes com o fornecimento dos dados no município, na modalidade e no ano de referência a que se refere o cancelamento. 
261
 2
	§ 4º Os titulares e prestadores públicos e privados dos serviços públicos de saneamento básico que não fornecerem dados para auditoria das informações do Sinisa ficarão inadimplentes na modalidade e no ano de referência.
262
 2
	§ 5º As entidades reguladoras que não realizarem a auditoria dos dados do Sinisa ficarão inadimplentes no ano de referência.
263
 0
	§ 6º A adimplência dos prestadores dos serviços e entidades reguladoras é extensiva aos municípios por eles operados e regulados, cujos dados tenham sido fornecidos e auditados.
264
 1
	§ 7º O disposto no § 2º do caput deste Decreto passará a vigorar a partir do sexto ano posterior à publicação do presente Decreto.
CAPÍTULO IV

DO APOIO DA UNIÃO À IMPLANTAÇÃO DE SISTEMAS ALTERNATIVOS E DESCENTRALIZADOS DE SANEAMENTO BÁSICO
265
 5
	Art. 66. A União poderá apoiar a implementação de soluções alternativas e descentralizadas, individual ou coletiva, de saneamento básico, para fins de auxiliar os entes federativos subnacionais no cumprimento das metas de universalização previstas no art. 11-B da Lei nº 11.445, de 2007.
266
 12
	Art. 67. A União deverá elaborar diretrizes para orientar a elaboração de estudos e implantação de infraestrutura em áreas rurais, levando-se em consideração os aspectos relacionados à disponibilidade hídrica, densidade populacional, viabilidade técnica e disponibilidade de serviço público de saneamento básico.
CAPÍTULO V

DAS DISPOSIÇÕES FINAIS
267
 6
	Art. 68. O Poder Executivo da União deverá regulamentar, no prazo de 01 (um) ano a partir da publicação deste Decreto, o reuso de efluente sanitário tratado e o uso de água de chuva de forma a atender o disposto na Lei nº 11.445, de 2007.
268
 1
	Art. 69. Fica revogado o Decreto nº 7.217, de 21 de junho de 2010.
269
 0
	Art. 70. Este Decreto entra em vigor na data de sua publicação. 
270
 25
	OBS: CONTRIBUIÇÕES ADICIONAIS - USE ESTE ESPAÇO
Participe!
Para participar deve estar logado no portal.
Contribuições Recebidas
1220 contribuições recebidas
Para ver o teor das contribuições deve estar logado no portal
"""

# 1. Processar o texto do decreto para extrair os dados
dados_extraidos = parse_decreto_para_dados_tabela(conteudo_decreto)

# 2. Gerar a tabela no console e a planilha CSV com os dados extraídos
genero_planilha = "analise_decreto_completo_atualizado.csv"
gerar_tabela_analise_e_planilha(dados_extraidos, nome_arquivo_csv=genero_planilha)