import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import tabula
import os
import PyPDF2
from transformers import pipeline

# ---------------------- Classificador de Tema ----------------------
temas = [
    "DA PRESTAÇÃO DOS SERVIÇOS",
    "DA REGULAÇÃO",
    "DA RELAÇÃO DOS SERVIÇOS PÚBLICOS DE SANEAMENTO BÁSICO COM OS RECURSOS HÍDRICOS",
    "DAS DEFINIÇÕES",
    "DAS DIRETRIZES E DOS OBJETIVOS",
    "DAS DISPOSIÇÕES FINAIS",
    "DAS METAS DE UNIVERSALIZAÇÃO",
    "DO APOIO DA UNIÃO À IMPLANTAÇÃO DE SISTEMAS ALTERNATIVOS E DESCENTRALIZADOS DE SANEAMENTO BÁSICO",
    "DO CONTROLE SOCIAL",
    "DO EXERCÍCIO DA TITULARIDADE",
    "DO OBJETO",
    "DO PLANEJAMENTO",
    "DO SISTEMA NACIONAL DE INFORMAÇÕES EM SANEAMENTO BÁSICO - SINISA",
    "DOS ASPECTOS ECONÔMICOS E FINANCEIROS",
    "DOS PLANOS DE SANEAMENTO BÁSICO DA UNIÃO",
    "DOS SERVIÇOS PÚBLICOS DE SANEAMENTO BÁSICO",
    "OBS: CONTRIBUIÇÕES ADICIONAIS - USE ESTE ESPAÇO"
]

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def extrair_texto_pdf(caminho_pdf):
    texto = ""
    with open(caminho_pdf, "rb") as arquivo:
        leitor = PyPDF2.PdfReader(arquivo)
        for pagina in leitor.pages:
            texto += pagina.extract_text() or ""
    return texto.strip()

def classificar_pdf_gui():
    pasta = filedialog.askdirectory(title="Selecione a pasta com PDFs")
    if not pasta:
        return
    try:
        resultados = []
        for nome_arquivo in os.listdir(pasta):
            if nome_arquivo.lower().endswith(".pdf"):
                caminho_pdf = os.path.join(pasta, nome_arquivo)
                texto = extrair_texto_pdf(caminho_pdf)
                if texto:
                    indice, tema = classificar_tema(texto[:1000])
                    resultados.append({
                        "Arquivo": nome_arquivo,
                        "Número do Tema": indice,
                        "Tema Classificado": tema
                    })
        if resultados:
            df = pd.DataFrame(resultados)
            saida = os.path.join(pasta, "resultados_classificacao.csv")
            df.to_csv(saida, index=False, encoding='utf-8-sig')
            messagebox.showinfo("Sucesso", f"Classificação salva em:\n{saida}")
        else:
            messagebox.showwarning("Aviso", "Nenhum conteúdo válido foi encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def classificar_tema(texto):
    resultado = classifier(texto, temas)
    tema_principal = resultado["labels"][0]
    indice = temas.index(tema_principal) + 1
    return indice, tema_principal

# ---------------------- Converter PDF em Excel ----------------------
def extrair_pdf_para_excel():
    caminho_pdf = filedialog.askopenfilename(title="Selecione o PDF", filetypes=[("PDF files", "*.pdf")])
    if not caminho_pdf:
        return
    try:
        tabelas = tabula.read_pdf(caminho_pdf, pages='all', multiple_tables=True, lattice=True)
        colunas = ["REDAÇÃO POSTA EM CONSULTA", "CONTRIBUIÇÕES SSB"]
        filtradas = [t[colunas].dropna(how="all") for t in tabelas if all(c in t.columns for c in colunas)]
        if filtradas:
            df_final = pd.concat(filtradas, ignore_index=True)
            saida = os.path.splitext(caminho_pdf)[0] + "_convertido.xlsx"
            df_final.to_excel(saida, index=False)
            messagebox.showinfo("Sucesso", f"Excel salvo em:\n{saida}")
        else:
            messagebox.showwarning("Aviso", "Colunas não encontradas no PDF.")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

# ---------------------- Mesclar Excel ----------------------
def mesclar_planilhas():
    caminho_excel = filedialog.askopenfilename(title="Selecione o Excel", filetypes=[("Excel files", "*.xlsx")])
    if not caminho_excel:
        return
    try:
        planilhas = pd.read_excel(caminho_excel, sheet_name=None)
        colunas = ["REDAÇÃO POSTA EM CONSULTA", "CONTRIBUIÇÕES SSB"]
        todas = []
        for nome, df in planilhas.items():
            if all(c in df.columns for c in colunas):
                df_filtrado = df[colunas].dropna(how='all')
                df_filtrado["ABA DE ORIGEM"] = nome
                todas.append(df_filtrado)
        if todas:
            final = pd.concat(todas, ignore_index=True)
            novo_caminho = os.path.splitext(caminho_excel)[0] + "_mesclado.xlsx"
            final.to_excel(novo_caminho, index=False)
            messagebox.showinfo("Sucesso", f"Mesclagem salva em:\n{novo_caminho}")
        else:
            messagebox.showwarning("Aviso", "Colunas não encontradas.")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

# ---------------------- Interface ----------------------
janela = tk.Tk()
janela.title("Ferramentas SSB - Decreto 7217")
janela.geometry("420x300")

tk.Label(janela, text="Ferramentas para análise de contribuições", font=("Arial", 13, "bold")).pack(pady=15)

tk.Button(janela, text="📥 Converter PDF para Excel", width=40, command=extrair_pdf_para_excel).pack(pady=5)
tk.Button(janela, text="📊 Mesclar abas do Excel", width=40, command=mesclar_planilhas).pack(pady=5)
tk.Button(janela, text="🧠 Classificar PDFs por tema (Decreto 7217)", width=40, command=classificar_pdf_gui).pack(pady=5)

janela.mainloop()
