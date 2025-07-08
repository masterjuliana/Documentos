from fpdf import FPDF
pdf = FPDF()  # Correto

# Substituir travessões e outros caracteres especiais por equivalentes ASCII
def clean_text(text):
    return text.replace("–", "-").replace("“", "\"").replace("”", "\"").replace("’", "'")

# Recriar o PDF com textos corrigidos
pdf.add_page()

# Conteúdo do parecer com texto limpo
pdf.set_font("Arial", size=12)  # Ajuste de fonte

pdf.cell(200, 10, "I. Contribuições Acolhidas", ln=True, align="C")
pdf.multi_cell(0, 10, clean_text(
    "- Aprimoramento da redação para mais clareza e inclusão.\n"
    "- Evitar interpretações restritivas do termo.\n"
    "- Observância aos padrões legais e normativos.\n"
    "- Reconhecimento da diversidade das comunidades rurais.\n"
    "- Ênfase em efetividade, salubridade e sustentabilidade."
))

# Continuação para as outras seções...

# Salvar PDF corrigido
pdf_path = "C:\\Users\\julia\\contribuiçõesanalisadas.pdf"
pdf.output(pdf_path)
