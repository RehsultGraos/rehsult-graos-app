
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Rehsult Grãos", layout="wide")

def gerar_grafico_radar(setores, area):
    categorias = list(setores.keys())
    valores = list(setores.values())

    valores += valores[:1]
    categorias += categorias[:1]

    angulos = [n / float(len(categorias)) * 2 * 3.14159 for n in range(len(categorias))]

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.25)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)
    ax.set_title(f"Radar - {area}")
    st.pyplot(fig)

def gerar_pdf(analise, setores_por_area):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", "", fname="arial.ttf", uni=True)
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "✅ Diagnóstico Concluído", ln=True)
    pdf.ln(5)

    for area, setores in setores_por_area.items():
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 10, f"📊 Resultados - {area}", ln=True)
        pdf.set_font("Arial", size=12)
        for setor, valor in setores.items():
            pdf.cell(0, 10, f"{setor}: {valor:.1f}%", ln=True)
        pdf.ln(5)

    pdf.multi_cell(0, 10, (
        f"🤖 Análise com GPT-4 (simulada):

"
        f"{analise}"
    ))

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)

# Logo e título
st.image("LOGO REAGRO TRATADA.png", width=150)
st.title("🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

# Exemplo de dados
setores_exemplo = {
    "Plantas Daninhas": {
        "Manejo integrado": 85,
        "Pré emergente": 92,
        "Dessecação": 78,
        "Capina": 80
    },
    "Fertilidade": {
        "Análise de Solo": 60,
        "Calagem e Gessagem": 75,
        "Macronutrientes": 90
    }
}

# Simulando análise
analise_simulada = """
✅ **Análise Simulada:**

- A área de **Análise de Solo** apresenta baixa pontuação, indicando atenção.
- O setor de **Capina** nas plantas daninhas foi razoável, mas pode melhorar.
- A aplicação de **Macronutrientes** está com boa pontuação.

🎯 **Recomendações**:

- Realizar análise de solo mais precisa.
- Reavaliar práticas de capina.
- Manter o manejo de macronutrientes.
"""

# Mostrando dados
for area, setores in setores_exemplo.items():
    st.markdown(f"### 📊 Resultados - {area}")
    pontuacao_geral = sum(setores.values()) / len(setores)
    st.markdown(f"**Pontuação Geral:** {pontuacao_geral:.1f}%")
    gerar_grafico_radar(setores, area)

# Análise com IA simulada
st.markdown("### 🤖 Análise com GPT-4 (simulada)")
st.markdown(analise_simulada)

# Botão para download do PDF
pdf_buffer = gerar_pdf(analise_simulada, setores_exemplo)
st.download_button(label="📄 Baixar Relatório em PDF", data=pdf_buffer, file_name="diagnostico.pdf")
