import pandas as pd

# Lista das 18 contribuições
contribuicoes = [
    ("CP-921098", "Abordagem diminuta do saneamento em zona rural"),
    ("CP-921380", "Sugestões para minuta sobre saneamento básico"),
    ("CP-922413", "Saneamento"),
    ("CP-925343", "Financiamento"),
    ("CP-925406", "Financiamento para pequenos municípios"),
    ("CP-927300", "Adição de poder público"),
    ("CP-927332", "Saneamento Básico Equilibrado"),
    ("CP-929681", "Incentivo à Reciclagem"),
    ("CP-930115", "Conformidade (ABRAC)"),
    ("CP-930368", "Drenagem e DMAPU (IBDRE)"),
    ("CP-930371", "Sanções Sinisa (IBDRE)"),
    ("CP-930375", "Interoperabilidade SNIRH/Sinisa"),
    ("CP-930494", "MDIC"),
    ("CP-930537", "Outorgas do Saneamento"),
    ("CP-930540", "Mudanças Climáticas"),
    ("CP-930541", "Biogás e Biometano"),
    ("CP-930614", "Regionalização Art. 15"),
    ("CP-930638", "SABESP - Contribuição Geral")
]

# Avaliações manuais de critérios: Jurídico, Técnico, Viável, Impacto, Relevância
avaliacoes = [
    (4, 4, 3, 4, 3),
    (2, 1, 2, 1, 1),
    (5, 4, 4, 4, 3),
    (5, 4, 4, 5, 3),
    (5, 5, 4, 5, 4),
    (4, 4, 3, 4, 2),
    (4, 3, 3, 4, 2),
    (2, 2, 2, 2, 1),
    (3, 3, 3, 3, 2),
    (5, 4, 4, 5, 4),
    (5, 4, 4, 5, 3),
    (5, 4, 4, 4, 3),
    (4, 3, 3, 4, 3),
    (5, 5, 4, 4, 4),
    (5, 5, 4, 5, 3),
    (4, 4, 3, 4, 3),
    (4, 3, 2, 3, 2),
    (5, 5, 5, 5, 4),
]

pesos = [0.3, 0.25, 0.15, 0.2, 0.1]
notas = [round(sum(c * p for c, p in zip(linha, pesos)), 2) for linha in avaliacoes]

# Classificação
def classificar(nota):
    if nota >= 4.0:
        return "Aceita"
    elif nota >= 3.0:
        return "Aceita com ajustes"
    else:
        return "Rejeitada"

decisoes = [classificar(n) for n in notas]

# Montar DataFrame final
df = pd.DataFrame(contribuicoes, columns=["Número", "Título"])
df["Nota Final"] = notas
df["Decisão"] = decisoes

# Salvar
df.to_excel("devolutiva_decreto_7217.xlsx", index=False)
