# Criar gráfico de rosca com porcentagens fora do gráfico
fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(
    quantidades,
    labels=categorias,
    autopct="%1.1f%%",
    startangle=90,
    colors=cores,
    wedgeprops=dict(width=0.4),
    pctdistance=1.15  # Distância dos percentuais para fora do gráfico
)

# Ajustar estilo dos textos
for autotext in autotexts:
    autotext.set_fontsize(10)
    autotext.set_color('black')

ax.set_title("Distribuição dos Tipos de Fonte", fontsize=14)
plt.tight_layout()

# Salvar novo gráfico
grafico_donut_externo_path = "/mnt/data/grafico_tipos_fonte_donut_externo.png"
plt.savefig(grafico_donut_externo_path)

grafico_donut_externo_path
