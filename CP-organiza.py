import pandas as pd

# Texto da tabela fornecido pelo usuário
texto_tabela = """
Número da Contribuição/   Dispositivo/    Contribuição Recebida/  Proposta de Redação Acolhida/   Situação da Contribuição/   Justificativa Técnica
CP-917373/  Art. 2º, inciso I/  Rever se o texto está restritivo por engano./   I – ação de saneamento básico: implantação de solução individual, coletiva ou comunitária de saneamento básico em área rural, cuja operação e manutenção possam ser realizadas pelo usuário, por associações, cooperativas ou pelo poder público local, conforme as condições técnicas, econômicas e sociais da população atendida, assegurando-se a adequada prestação dos serviços nos termos do art. 5º da Lei nº 11.445, de 2007;/  Acolhida Total/  Considera-se pertinente o ajuste, de forma a deixar explícito o âmbito de aplicação previsto.
CP-918698/  Art. 2º, inciso I/  No enunciado, o termo saneamento básico restringe à área rural./    I – ação de saneamento básico em área rural: implantação de solução individual, coletiva ou comunitária de saneamento básico cuja operação e manutenção possam ser realizadas pelo usuário, por associações, cooperativas ou pelo poder público local, conforme as condições técnicas, econômicas e sociais da população atendida, assegurando-se a adequada prestação dos serviços nos termos do art. 5º da Lei nº 11.445, de 2007;/  Acolhida Total/  A redação foi ajustada para deixar explícito o âmbito de aplicação previsto.
"""

# Separar as linhas e criar listas para armazenar os dados
linhas = texto_tabela.strip().split("\n")[1:]  # Pula o cabeçalho
dados = []

for linha in linhas:
    partes = linha.split("/")
    if len(partes) >= 6:
        dados.append([parte.strip() for parte in partes[:6]])

# Criar DataFrame
colunas = [
    "Número da Contribuição",
    "Dispositivo",
    "Contribuição Recebida",
    "Proposta de Redação Acolhida",
    "Situação da Contribuição",
    "Justificativa Técnica"
]
df = pd.DataFrame(dados, columns=colunas)

# Salvar como Excel
caminho_arquivo = "/mnt/data/contribuicoes_formatadas.xlsx"
df.to_excel(caminho_arquivo, index=False)

caminho_arquivo
