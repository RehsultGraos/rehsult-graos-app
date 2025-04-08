
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from io import BytesIO
from PIL import Image

# Configurações iniciais
st.set_page_config(page_title="Rehsult Grãos", layout="centered")

# Logo
st.image("LOGO REAGRO TRATADA.png", width=180)
st.title("🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

# Função para gerar gráfico radar
def gerar_grafico_radar(setores, titulo_area):
    labels = list(setores.keys())
    valores = list(setores.values())
    labels.append(labels[0])
    valores.append(valores[0])

    angulos = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.3)
    ax.set_yticklabels([])
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(labels)
    ax.set_title(f"📊 {titulo_area}", fontsize=14, weight='bold')
    st.pyplot(fig)

# Função para gerar PDF
def gerar_pdf(analise, setores_areas):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("ArialUnicode", fname="DejaVuSans.ttf", uni=True)
    pdf.set_font("ArialUnicode", size=12)

    pdf.set_text_color(0, 102, 0)
    pdf.set_font(style='B')
    pdf.cell(200, 10, txt="Diagnóstico Rehsult Grãos", ln=True, align='C')
    pdf.set_font(style='')

    pdf.ln(10)
    pdf.multi_cell(0, 10, "Análise com GPT-4 (simulada):
")
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, analise)

    pdf.ln(10)
    pdf.set_text_color(0, 102, 0)
    pdf.set_font(style='B')
    pdf.cell(200, 10, txt="Pontuação por Setor:", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(style='')

    for area, setores in setores_areas.items():
        pdf.set_font(style='B')
        pdf.cell(200, 10, txt=f"{area}:", ln=True)
        pdf.set_font(style='')
        for setor, valor in setores.items():
            pdf.cell(200, 10, txt=f"- {setor}: {valor:.1f}%", ln=True)

    output_path = "/mnt/data/diagnostico_rehsultgraos.pdf"
    pdf.output(output_path)
    return output_path

# Simulação de setores avaliados
setores_areas = {
    "Plantas Daninhas": {
        "Pré-emergente": 40,
        "Cobertura": 60,
        "Pós-emergente": 80
    },
    "Fertilidade": {
        "Análise de Solo": 35,
        "Calagem e Gessagem": 55,
        "Macronutrientes": 75
    }
}

# Análise simulada baseada nas pontuações
def gerar_analise_simulada(setores_areas):
    analise = "✅ **Análise Simulada:**

"
    recomendacoes = []

    for area, setores in setores_areas.items():
        for setor, valor in setores.items():
            if valor < 50:
                analise += f"- A área de **{setor}** em **{area}** apresenta baixa pontuação, indicando atenção.
"
                recomendacoes.append(f"Revisar práticas no setor **{setor}** em **{area}**.")
            elif valor < 70:
                analise += f"- A área de **{setor}** em **{area}** está razoável, mas pode melhorar.
"
                recomendacoes.append(f"Otimizar setor **{setor}** em **{area}**.")
            else:
                analise += f"- A área de **{setor}** em **{area}** está com boa pontuação.
"

    analise += "
🎯 **Recomendações:**

"
    for rec in recomendacoes:
        analise += f"- {rec}
"

    return analise

# Exibir análise e gráficos
st.markdown("## ✅ Diagnóstico Concluído")
analise = gerar_analise_simulada(setores_areas)

for area, setores in setores_areas.items():
    gerar_grafico_radar(setores, area)

st.markdown("### 🤖 Análise com GPT-4 (simulada)")
st.markdown(analise, unsafe_allow_html=True)

# Gerar e baixar PDF
pdf_path = gerar_pdf(analise, setores_areas)
with open(pdf_path, "rb") as f:
    st.download_button("📄 Baixar Diagnóstico em PDF", f, file_name="diagnostico_rehsultgraos.pdf")
