import json
import os

# --- Configurações ---
# O caminho completo para o seu arquivo .txt original.
# ATENÇÃO: As barras invertidas (\) em caminhos do Windows precisam ser "escapadas"
# com outra barra invertida (\\) ou você pode usar barras normais (/) que o Python entende.
# Ou, mais seguro, usar string raw (r'...') para evitar problemas com escapes.
CAMINHO_ARQUIVO_TXT = r'W:\MINISTÉRIO DAS CIDADES\Consulta 7217\DECRETO Nº XXX, DE XX DE XX DE 2025.txt'

# O nome do arquivo JSON de saída. Ele será salvo na mesma pasta deste script Python.
NOME_ARQUIVO_JSON_SAIDA = 'decreto.json'
caminho_arquivo_json_saida = os.path.join(os.path.dirname(__file__), NOME_ARQUIVO_JSON_SAIDA)

# --- Processo de Geração ---
conteudo_do_txt = ""

print(f"Tentando ler o arquivo TXT de: {CAMINHO_ARQUIVO_TXT}")

try:
    # Abre o arquivo TXT para leitura.
    # Tentamos 'utf-8' primeiro, que é o mais comum e robusto para caracteres especiais.
    # Se der erro, tentaremos 'latin-1'.
    try:
        with open(CAMINHO_ARQUIVO_TXT, 'r', encoding='utf-8') as f:
            conteudo_do_txt = f.read()
    except UnicodeDecodeError:
        print("Erro de decodificação UTF-8 no TXT. Tentando com 'latin-1'...")
        with open(CAMINHO_ARQUIVO_TXT, 'r', encoding='latin-1') as f:
            conteudo_do_txt = f.read()

    # Cria o dicionário Python no formato desejado para o JSON
    dados_json = {
        "conteudo_decreto": conteudo_do_txt
    }

    # Salva o dicionário como um arquivo JSON.
    # indent=4 torna o JSON mais legível com identação de 4 espaços.
    # ensure_ascii=False permite que caracteres acentuados sejam gravados diretamente
    # em vez de serem convertidos para sequências de escape \uXXXX.
    # encoding='utf-8' garante que o arquivo JSON seja salvo corretamente com UTF-8.
    with open(caminho_arquivo_json_saida, 'w', encoding='utf-8') as f:
        json.dump(dados_json, f, indent=4, ensure_ascii=False)

    print(f"\nSucesso! O arquivo '{NOME_ARQUIVO_JSON_SAIDA}' foi gerado em: {caminho_arquivo_json_saida}")
    print(f"O tamanho do conteúdo lido do TXT é: {len(conteudo_do_txt)} caracteres.")

except FileNotFoundError:
    print(f"Erro: O arquivo TXT '{CAMINHO_ARQUIVO_TXT}' não foi encontrado.")
    print("Por favor, verifique se o caminho e o nome do arquivo estão corretos.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")