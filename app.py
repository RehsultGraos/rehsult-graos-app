
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from io import BytesIO
import os

st.set_page_config(page_title="Rehsult Grãos", layout="centered")

# Exibir logo
st.image("LOGO REAGRO TRATADA.png", width=180)
st.title("🌱 Rehsult Grãos")
st.markdown("Diagnóstico de fazendas produtoras de grãos com análise simulada GPT-4")

# Dados simulados
setores_areas = {
    "Fertilidade": {"Análise de Solo": 55.0, "Calagem e Gessagem": 42.0, "Macronutrientes": 60.0},
    "Plantas Daninhas": {"Pré-emergente": 35.0, "Cobertura": 50.0}
}

def gerar_grafico_radar(setores, area):
    categorias = list(setores.keys())
    valores = list(setores.values()) + [list(setores.values())[0]]
    categorias += [categorias[0]]
    angulos = np.linspace(0, 2 * np.pi, len(categorias), endpoint=False).tolist()
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, marker='o')
    ax.fill(angulos, valores, alpha=0.3)
    ax.set_yticklabels([])
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias)
    ax.set_title(f"📊 Radar - {area}")
    st.pyplot(fig)

def gerar_analise_simulada(setores):
    analise = "✅ Análise Simulada:

"
    for area, setores_area in setores.items():
        for setor, valor in setores_area.items():
            if valor < 50:
                analise += f"- O setor {setor} em {area} apresenta baixa pontuação.
"
            elif valor < 70:
                analise += f"- O setor {setor} em {area} está razoável, mas pode melhorar.
"
            else:
                analise += f"- O setor {setor} em {area} está com boa pontuação.
"
    analise += "
🎯 Recomendações:
- Revisar práticas nos setores com desempenho fraco.
- Otimizar os setores intermediários.
"
    return analise

def gerar_pdf_completo(analise, setores_areas, output_path="/mnt/data/diagnostico_completo.pdf"):
    os.makedirs("/mnt/data", exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Diagnóstico de Fazenda - Rehsult Grãos", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, "Análise com GPT-4 (simulada):")
    pdf.ln(2)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 10, analise)

    pdf.ln(10)
    for area, setores in setores_areas.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Área: {area}", ln=True)
        pdf.set_font("Arial", '', 11)
        for setor, pct in setores.items():
            pdf.cell(0, 10, f"  - {setor}: {pct:.1f}%", ln=True)

    pdf.output(output_path)
    return output_path

# Exibir resultados
st.subheader("✅ Diagnóstico Concluído")
for area, setores in setores_areas.items():
    st.markdown(f"### 📊 Resultados - {area}")
    media = np.mean(list(setores.values()))
    st.markdown(f"**Pontuação Geral:** {media:.1f}%")
    gerar_grafico_radar(setores, area)

# Análise
analise = gerar_analise_simulada(setores_areas)
st.markdown("### 🤖 Análise com GPT-4 (simulada)")
st.markdown(analise)

# PDF
pdf_path = gerar_pdf_completo(analise, setores_areas)
with open(pdf_path, "rb") as f:
    st.download_button("📄 Baixar PDF do Diagnóstico", f, file_name="diagnostico_completo.pdf")
