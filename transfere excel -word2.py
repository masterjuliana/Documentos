import pandas as pd
from docx import Document
from docx.shared import Pt

# Definir caminhos dos arquivos
arquivo_excel = r"W:\MINISTÉRIO DAS CIDADES\Consulta 7217\python\Consideracoes-sobre-a-Consulta_Publica_Decreto_7217.2010.xlsx"
arquivo_word_saida = r"W:\MINISTÉRIO DAS CIDADES\Consulta 7217\python\saida.docx"

try:
    df = pd.read_excel(arquivo_excel, engine="openpyxl")
except FileNotFoundError:
    raise FileNotFoundError(f"O arquivo '{arquivo_excel}' não foi encontrado.")
except Exception as e:
    raise RuntimeError(f"Erro ao ler o arquivo Excel: {e}")

# Remover espaços extras dos nomes das colunas
df.columns = df.columns.str.strip()

# Colunas desejadas
colunas_desejadas = ['Item CP alterado', 'Numero', 'Titulo da Contribuição', 'Texto', 'Justificativa', 'Nome']

# Verificar se todas as colunas existem
colunas_ausentes = [col for col in colunas_desejadas if col not in df.columns]
if colunas_ausentes:
    raise ValueError(f"Colunas ausentes no Excel: {', '.join(colunas_ausentes)}")

# Selecionar as colunas desejadas
df = df[colunas_desejadas]

if df.empty:
    raise ValueError("Nenhum dado encontrado após a seleção das colunas! Verifique o conteúdo do arquivo Excel.")

# Substituir _x000D_ por aspas "
df = df.replace(r'_x000D_', '"', regex=True)

# Converter "Item CP alterado" para números, tratando valores errados
df["Item CP alterado"] = pd.to_numeric(df["Item CP alterado"], errors="coerce")
df = df.dropna(subset=["Item CP alterado"])
df["Item CP alterado"] = df["Item CP alterado"].astype(int)

# Contar o número de contribuições por "Item CP alterado"
df_contribuicoes_agrupado = df.groupby("Item CP alterado")["Texto"].apply(lambda x: "\n".join(x)).reset_index()

# Abrir o documento de saída
doc = Document(arquivo_word_saida)

# Iterar pelas tabelas do documento para encontrar a linha correta
for table in doc.tables:
    for row in table.rows:
        item_cp_cell = row.cells[0].text.strip()  # Coluna "Item" no Word

        # Verificar se "Item CP alterado" está na tabela
        if item_cp_cell.isdigit():
            item_cp = int(item_cp_cell)

            # Encontrar as contribuições associadas no Excel
            matching_row = df_contribuicoes_agrupado[df_contribuicoes_agrupado["Item CP alterado"] == item_cp]

            if not matching_row.empty:
                # Dividir a coluna "Visões das contribuições" proporcionalmente
                row.cells[2].text = matching_row["Texto"].values[0]  # Adicionar contribuições

# Salvar o arquivo ajustado
arquivo_word_ajustado = r"W:\MINISTÉRIO DAS CIDADES\Consulta 7217\python\saida_ajustada.docx"
doc.save(arquivo_word_ajustado)

print(f"Arquivo Word ajustado criado: {arquivo_word_ajustado}")
