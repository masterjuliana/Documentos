import docx
from openpyxl import Workbook
import re
import os
import fitz # PyMuPDF
import unicodedata

def normalize_text_for_comparison(text):
    """
    Normaliza o texto para comparação no PDF.
    Foca em limpar espaços e caracteres de controle, e tenta garantir consistência de acentos.
    """
    if text is None:
        return ""
    
    # 1. Substitui quebras de linha, retornos de carro e tabs por um único espaço
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 2. Tenta remover caracteres de controle unicode não imprimíveis, mas mantém caracteres "reais"
    text = ''.join(char for char in text if char.isprintable() or unicodedata.category(char)[0] == 'L' and unicodedata.category(char)[1] == 'm' or unicodedata.category(char)[0] == 'P')
    
    # Adicionando uma normalização Unicode mais forte para compatibilidade entre fontes.
    # NFD: Decomposição Canônica - separa caracteres base de seus diacríticos (acentos)
    # NFKC: Compatibilidade Canônica - tenta resolver algumas equivalências de caracteres.
    # Pode ser necessário experimentar entre NFD e NFKC. Vamos tentar NFKC primeiro, pois é mais "agressivo"
    # na padronização.
    text = unicodedata.normalize('NFKC', text)
    
    # Alguns PDFs podem ter problemas específicos com o 'º' ou 'ª'
    text = text.replace('º', 'o').replace('ª', 'a') # Substitui 'º' por 'o' e 'ª' por 'a' para maior compatibilidade.
    text = text.replace('§', 'S') # Tenta substituir § por S, se for um problema persistente. Pode ajustar.

    # Remove múltiplos espaços novamente após qualquer substituição
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def obter_pagina_dos_itens_no_pdf(caminho_pdf, itens_para_buscar):
    """
    Localiza os itens no PDF e retorna suas páginas iniciais.
    Args:
        caminho_pdf (str): Caminho para o arquivo PDF.
        itens_para_buscar (list): Lista de tuplas (identificador_completo_do_item, texto_da_minuta_curto_original).
                                 O texto_da_minuta_curto_original será normalizado e usado para buscar no PDF.
    Returns:
        dict: Um dicionário mapeando o identificador_completo_do_item para o número da página.
    """
    paginas_encontradas = {}
    doc_pdf = None

    try:
        doc_pdf = fitz.open(caminho_pdf)
        print(f"Documento PDF '{caminho_pdf}' aberto com sucesso para análise de páginas.")

        textos_de_busca_mapa = {}
        for identificador_completo, texto_minuta_curto_original in itens_para_buscar:
            # Normaliza o texto de busca do Word
            cleaned_text = normalize_text_for_comparison(texto_minuta_curto_original)
            
            # Escapa caracteres especiais de regex e permite variações de múltiplos espaços (tab, new line, space)
            regex_pattern = re.escape(cleaned_text).replace(r'\ ', r'\s+')
            
            # Compila a regex, ignorando maiúsculas/minúsculas e permitindo que o '.' case com nova linha
            textos_de_busca_mapa[identificador_completo] = re.compile(regex_pattern, re.IGNORECASE | re.DOTALL)

        textos_ja_encontrados = set()

        for page_num in range(doc_pdf.page_count):
            page = doc_pdf.load_page(page_num)
            page_text = page.get_text("text") # Tenta usar "text" como método de extração.
            
            # Tenta decodificar o texto se houver problemas de codificação.
            # PyMuPDF geralmente retorna UTF-8, mas em casos problemáticos, pode ajudar.
            try:
                # Vamos tentar forçar a decodificação de e para UTF-8.
                # Se o problema for de "latin-1" sendo lido como UTF-8 inválido, isso pode ajudar.
                # Esta linha é um "hack" para tentar corrigir chars quebrados.
                page_text_decoded = page_text.encode('latin-1', 'ignore').decode('utf-8', 'ignore')
            except UnicodeDecodeError:
                page_text_decoded = page_text # Se falhar, usa o original (já pode ser UTF-8)
            except Exception as e:
                print(f"Aviso de codificação na página {page_num + 1}: {e}")
                page_text_decoded = page_text

            # Normaliza o texto da página ANTES de tentar buscar
            normalized_page_text = normalize_text_for_comparison(page_text_decoded)

            for identificador_completo, regex_obj in textos_de_busca_mapa.items():
                if identificador_completo in textos_ja_encontrados:
                    continue

                if regex_obj.search(normalized_page_text):
                    paginas_encontradas[identificador_completo] = page_num + 1
                    textos_ja_encontrados.add(identificador_completo)

                    if len(paginas_encontradas) == len(itens_para_buscar):
                        break # Todos os itens foram encontrados
            if len(paginas_encontradas) == len(itens_para_buscar):
                break # Todos os itens foram encontrados

    except Exception as e:
        print(f"Erro ao analisar o PDF para números de página: {e}")
    finally:
        if doc_pdf:
            doc_pdf.close()

    return paginas_encontradas

# O restante do script (analisar_decreto_word e o bloco if __name__ == "__main__":)
# permanece o mesmo, pois as modificações foram nas funções de normalização e busca de PDF.
# Colocarei o restante para facilitar a cópia completa.

def analisar_decreto_word(caminho_documento_word, caminho_saida_excel):
    """
    Analisa um documento Word (.docx) para extrair itens de uma tabela,
    e, usando um PDF correspondente, inclui a quantidade de contribuições e o número de páginas,
    salvando tudo em um arquivo Excel (.xlsx).

    Args:
        caminho_documento_word (str): O caminho completo para o arquivo Word (.docx).
        caminho_saida_excel (str): O caminho completo para o arquivo Excel de saída (.xlsx).
    """
    caminho_pdf_correspondente = os.path.splitext(caminho_documento_word)[0] + ".pdf"

    if not os.path.exists(caminho_pdf_correspondente):
        print(f"Erro: O arquivo PDF correspondente não foi encontrado: '{caminho_pdf_correspondente}'")
        print("Por favor, salve o documento Word como PDF com o mesmo nome base (.docx e .pdf) e na mesma pasta.")
        return

    try:
        documento = docx.Document(caminho_documento_word)
        print(f"Documento Word '{caminho_documento_word}' aberto com sucesso.")
    except Exception as e:
        print(f"Erro ao abrir o documento Word: {e}")
        return

    dados_para_excel = []
    dados_para_excel.append(["Item Principal", "Texto da Minuta de Decreto", "Quantidade de Contribuições", "Página Inicial", "Número de Páginas"])

    regex_contexto = re.compile(r"^(Art\.\s*\d+º?|Parágrafo único\.?|\u00a7\s*\d+\u00ba?|[IVXLCDM]+\s*[-–.]\s*|[a-z]\))", re.IGNORECASE)

    encontrou_tabela_decreto = False
    tabela_decreto = None

    for table in documento.tables:
        if len(table.rows) > 0 and len(table.rows[0].cells) >= 3:
            cell1_text = table.rows[0].cells[0].text.strip()
            cell2_text = table.rows[0].cells[1].text.strip()
            cell3_text = table.rows[0].cells[2].text.strip()
            
            print(f"DEBUG: Cabeçalhos da primeira tabela lidos do Word: '{cell1_text}', '{cell2_text}', '{cell3_text}'")

            is_item_header = "ITEM" in cell1_text.upper()
            is_minuta_header = "MINUTA DE DECRETO" in cell2_text.upper()
            
            is_visoes_header = False
            if "VISÕES DAS CONTRIBUIÇÕES" in cell3_text.upper():
                is_visoes_header = True
            elif "VISOES DAS CONTRIBUICOES" in cell3_text.upper():
                is_visoes_header = True
            elif "VISAO DAS CONTRIBUICOES" in cell3_text.upper():
                is_visoes_header = True

            if is_item_header and is_minuta_header and is_visoes_header:
                encontrou_tabela_decreto = True
                tabela_decreto = table
                print("Tabela do decreto identificada.")
                break

    if not encontrou_tabela_decreto:
        print("A tabela principal do decreto não foi encontrada no documento Word com os cabeçalhos esperados.")
        print("Verifique se os cabeçalhos 'Item', 'Minuta de Decreto' e 'Visões das contribuições' (ou variações próximas) estão presentes na primeira linha da tabela.")
        return

    itens_para_buscar_no_pdf = []
    dados_itens_brutos = []

    for i, row in enumerate(tabela_decreto.rows):
        if i == 0:
            continue

        if len(row.cells) >= 3:
            item_principal_cell = row.cells[0]
            minuta_decreto_cell = row.cells[1]
            quantidade_contribuicoes_cell = row.cells[2]

            item_number_raw = item_principal_cell.text.strip()
            minuta_text_raw = minuta_decreto_cell.text.strip()
            quantidade_contribuicoes_text_raw = quantidade_contribuicoes_cell.text.strip()

            if item_number_raw.isdigit() and len(item_number_raw) > 0 and len(minuta_text_raw) > 0:
                match = regex_contexto.search(minuta_text_raw)
                if match:
                    item_context_segment = minuta_text_raw[len(match.group(0)):min(len(minuta_text_raw), len(match.group(0)) + 70)]
                    texto_para_busca_pdf_original = match.group(0) + " " + item_context_segment
                else:
                    texto_para_busca_pdf_original = minuta_text_raw[:70]

                full_item_identifier = f"{item_number_raw} - {minuta_text_raw[:100]}"

                itens_para_buscar_no_pdf.append((full_item_identifier, texto_para_busca_pdf_original))

                dados_itens_brutos.append({
                    "identificador": full_item_identifier,
                    "minuta_text": minuta_text_raw,
                    "quantidade_contribuicoes": quantidade_contribuicoes_text_raw,
                    "pagina_inicial": None,
                    "num_paginas": None
                })
        else:
            print(f"Aviso: Linha {i+1} da tabela tem menos de 3 células esperadas, ignorando. Conteúdo: {normalize_text_for_comparison(row.text)}")

    paginas_dos_itens = obter_pagina_dos_itens_no_pdf(caminho_pdf_correspondente, itens_para_buscar_no_pdf)

    previous_page = None
    previous_item_identifier = None
    total_paginas_documento = 0

    try:
        doc_final_pdf = fitz.open(caminho_pdf_correspondente)
        total_paginas_documento = doc_final_pdf.page_count
        doc_final_pdf.close()
    except Exception as e:
        print(f"Erro ao obter o número total de páginas do PDF: {e}. Usará 'N/A' para o último item.")
        total_paginas_documento = "N/A"

    for idx, item_data in enumerate(dados_itens_brutos):
        identificador = item_data["identificador"]
        current_page = paginas_dos_itens.get(identificador)

        if current_page is not None:
            item_data["pagina_inicial"] = current_page

            if previous_page is not None and previous_item_identifier is not None:
                for prev_idx_inner in range(idx - 1, -1, -1):
                    if dados_itens_brutos[prev_idx_inner]["identificador"] == previous_item_identifier:
                        end_page_prev_item = current_page - 1
                        if end_page_prev_item < dados_itens_brutos[prev_idx_inner]["pagina_inicial"]:
                             end_page_prev_item = dados_itens_brutos[prev_idx_inner]["pagina_inicial"]

                        dados_itens_brutos[prev_idx_inner]["num_paginas"] = end_page_prev_item - dados_itens_brutos[prev_idx_inner]["pagina_inicial"] + 1
                        break

            previous_page = current_page
            previous_item_identifier = identificador
        else:
            print(f"Aviso: Página inicial não encontrada no PDF para o item: '{identificador}'. Isso pode ocorrer se o texto do item não for único ou não estiver formatado como esperado no PDF.")
            item_data["pagina_inicial"] = "N/A"
            item_data["num_paginas"] = "N/A"

    if dados_itens_brutos:
        last_found_item_idx = -1
        for i in range(len(dados_itens_brutos) - 1, -1, -1):
            if dados_itens_brutos[i]["pagina_inicial"] != "N/A":
                last_found_item_idx = i
                break
        
        if last_found_item_idx != -1:
            last_item_data = dados_itens_brutos[last_found_item_idx]
            if isinstance(total_paginas_documento, int) and last_item_data["pagina_inicial"] != "N/A":
                last_item_data["num_paginas"] = total_paginas_documento - last_item_data["pagina_inicial"] + 1
            else:
                last_item_data["num_paginas"] = "N/A"

    for item_data in dados_itens_brutos:
        dados_para_excel.append([
            item_data["identificador"],
            item_data["minuta_text"],
            item_data["quantidade_contribuicoes"],
            item_data["pagina_inicial"],
            item_data["num_paginas"]
        ])

    wb = Workbook()
    ws = wb.active
    ws.title = "Analise Decreto"

    for row_data in dados_para_excel:
        ws.append(row_data)

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if cell.value is not None and len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    try:
        wb.save(caminho_saida_excel)
        print(f"Análise concluída! Dados salvos em: {caminho_saida_excel}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo Excel: {e}")

if __name__ == "__main__":
    caminho_documento_word = r"W:\MINISTÉRIO DAS CIDADES\Consulta 7217\contar páginas\GTI - PLANILHA GTI 7217.2010 – ANÁLISE DAS CONTRIBUIÇÕES.docx"
    nome_arquivo_excel_saida = "Analise_Decreto_Completa.xlsx"

    diretorio_do_word = os.path.dirname(caminho_documento_word)
    caminho_saida_excel = os.path.join(diretorio_do_word, nome_arquivo_excel_saida)

    if os.path.exists(caminho_documento_word):
        print(f"Iniciando processamento do documento: '{caminho_documento_word}'")
        analisar_decreto_word(caminho_documento_word, caminho_saida_excel)
    else:
        print(f"Erro: O arquivo Word não foi encontrado no caminho especificado: '{caminho_documento_word}'")
        print("Por favor, verifique se o caminho e o nome do arquivo estão corretos.")
