import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Definir caminho para o executável do Tesseract
pytesseract.pytesseract.tesseract_cmd = r"J:\tesseract\tesseract.exe"

# Caminho do PDF de entrada
pdf_path = r"W:\MINISTÉRIO DAS CIDADES\Consulta 7217\Contribuições PDF\CP-930603 - FRANCISCO DOS SANTOS LOPES.pdf"
# Caminho do arquivo .txt de saída
output_txt_path = r"W:\MINISTÉRIO DAS CIDADES\Consulta 7217\Contribuições PDF\CP-930603 - FRANCISCO DOS SANTOS LOPES.txt"

# Abrir o PDF
doc = fitz.open(pdf_path)
all_text = ""

for i, page in enumerate(doc):
    print(f"Processando página {i + 1} de {len(doc)}...")

    # Renderizar como imagem em alta resolução
    pix = page.get_pixmap(dpi=300)
    img_bytes = pix.tobytes("png")

    # Carregar imagem com Pillow
    image = Image.open(io.BytesIO(img_bytes))

    # Aplicar OCR em português
    text = pytesseract.image_to_string(image, lang="por", config="--psm 6")

    # Adicionar separador por página
    all_text += f"\n--- Página {i + 1} ---\n{text}\n"

# Salvar o texto no arquivo .txt
with open(output_txt_path, "w", encoding="utf-8") as f:
    f.write(all_text)

print(f"\n✅ OCR finalizado. Texto salvo em:\n{output_txt_path}")
