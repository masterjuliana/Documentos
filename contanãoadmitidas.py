import re

def analisar_contribuicoes(caminho_arquivo):
    """
    Analisa as contribuições no arquivo de texto, contando contribuições sem "Parágrafo:"
    e o número de contribuições com campos ausentes.

    Args:
        caminho_arquivo (str): O caminho para o arquivo de texto.

    Returns:
        tuple: Uma tupla contendo:
                - Uma lista de dicionários, onde cada dicionário representa uma contribuição
                 e contém "Contribuinte", "Status", "Número", "Texto".
                - Um dicionário onde as chaves são os nomes dos campos
                 ("Contribuinte", "Status", "Número", "Texto", "Parágrafo")
                 e os valores são o número de contribuições com esse campo ausente.
    """

    contribuicoes_sem_paragrafo = []
    campos_ausentes = {
        "Contribuinte": 0,
        "Status": 0,
        "Número": 0,
        "Texto": 0,
        "SemParágrafo": 0
    }
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            texto = arquivo.read()

        regex = re.compile(
            r"Contribuinte:\s*(.*?)\s*"
            r"Status\s*(.*?)\s*"
            r"Número:\s*(.*?)\s*"
            r"([\s\S]*?)(?=\nContribuinte:|\Z)",
            re.IGNORECASE
        )

        matches = re.finditer(regex, texto)

        for match in matches:
            contribuinte = match.group(1).strip()
            status = match.group(2).strip()
            numero = match.group(3).strip()
            texto_contribuicao = match.group(4).strip()

            contribuicao = {
                "Contribuinte": contribuinte,
                "Status": status,
                "Número": numero,
                "Texto": texto_contribuicao
            }

            # Check for missing values and update counts
            for campo, valor in contribuicao.items():
                if not valor or valor.isspace():
                    campos_ausentes[campo] += 1

            if "parágrafo:" not in texto_contribuicao.lower():
                contribuicoes_sem_paragrafo.append(contribuicao)
                campos_ausentes["SemParágrafo"] += 1

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{caminho_arquivo}'")
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")
    return contribuicoes_sem_paragrafo, campos_ausentes

# Example Usage
caminho_arquivo = r"W:\MINISTÉRIO DAS CIDADES\Consulta 7217\apresentação\não admitidas.txt"  # Replace with your file path
contribuicoes_problematicas, contagem_campos_ausentes = analisar_contribuicoes(caminho_arquivo)


if contagem_campos_ausentes:
    print("\nContagem de Campos Ausentes:")
    for campo, contagem in contagem_campos_ausentes.items():
        print(f"  {campo}: {contagem}")
else:
    print("Nenhuma contribuição encontrada.")